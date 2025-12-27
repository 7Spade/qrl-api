"""
Main application entry point for QRL Trading Bot
Flask web server for Cloud Run deployment
"""
import logging
import sys
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from pythonjsonlogger import jsonlogger

from config import config
from redis_client import redis_client
from bot import trading_bot
from mexc_client import mexc_client

# Configure logging
def setup_logging():
    """Configure JSON logging for Cloud Run"""
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    log_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)
    root_logger.setLevel(logging.INFO if not config.DEBUG else logging.DEBUG)
    
    return root_logger

logger = setup_logging()

# Create Flask app
app = Flask(__name__)

# Initialize services with error handling
try:
    # Test Redis connection
    redis_client.get_bot_status()
    logger.info("Redis connection successful")
except Exception as e:
    logger.warning(f"Redis connection failed (will continue with limited functionality): {e}")

try:
    # Test MEXC client
    mexc_client.health_check()
    logger.info("MEXC client initialized successfully")
except Exception as e:
    logger.warning(f"MEXC client initialization failed (will use fallback data): {e}")


@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint - redirect to dashboard or return JSON
    """
    # Check if request wants HTML (browser) or JSON (API)
    if request.accept_mimetypes.accept_html:
        return dashboard()
    
    return jsonify({
        'service': 'QRL Trading Bot',
        'version': '1.0.0',
        'status': 'running',
        'trading_pair': config.TRADING_PAIR
    })


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Web dashboard - shows balance, positions, and trading stats
    View-only interface (no control buttons)
    """
    try:
        # Get all data with fallbacks
        try:
            bot_status = redis_client.get_bot_status() or 'unknown'
            latest_price = redis_client.get_latest_price() or 0
            daily_trades = redis_client.get_daily_trades()
        except Exception as e:
            logger.warning(f"Dashboard: Redis connection failed, using defaults: {e}")
            bot_status = 'unknown'
            latest_price = 0
            daily_trades = 0
        
        # Get position data
        try:
            position = redis_client.get_position() or {}
            qrl_balance = position.get('size', 0)
        except Exception as e:
            logger.warning(f"Dashboard: Cannot get position from Redis: {e}")
            position = {}
            qrl_balance = 0
        
        # Get position layers
        try:
            layers_data = redis_client.get_position_layers()
        except Exception as e:
            logger.warning(f"Dashboard: Cannot get position layers from Redis: {e}")
            layers_data = None
            
        if layers_data:
            core_qrl = float(layers_data.get('core_qrl', qrl_balance * 0.7))
            swing_qrl = float(layers_data.get('swing_qrl', qrl_balance * 0.2))
            active_qrl = float(layers_data.get('active_qrl', qrl_balance * 0.1))
        else:
            # Default distribution if not set
            core_qrl = qrl_balance * 0.7
            swing_qrl = qrl_balance * 0.2
            active_qrl = qrl_balance * 0.1
        
        total_qrl = core_qrl + swing_qrl + active_qrl
        
        # Calculate percentages for display
        core_percent = (core_qrl / total_qrl * 100) if total_qrl > 0 else 70
        swing_percent = (swing_qrl / total_qrl * 100) if total_qrl > 0 else 20
        active_percent = (active_qrl / total_qrl * 100) if total_qrl > 0 else 10
        
        # Get cost tracking
        try:
            cost_data = redis_client.get_cost_tracking()
        except Exception as e:
            logger.warning(f"Dashboard: Cannot get cost tracking from Redis: {e}")
            cost_data = None
            
        if cost_data:
            avg_cost = float(cost_data.get('avg_cost', 0))
            realized_pnl = float(cost_data.get('realized_pnl', 0))
            unrealized_pnl = float(cost_data.get('unrealized_pnl', 0))
        else:
            avg_cost = 0
            realized_pnl = 0
            unrealized_pnl = 0
        
        # Calculate P&L percentage
        pnl_percent = None
        if avg_cost > 0 and latest_price > 0:
            pnl_percent = ((latest_price / avg_cost) - 1) * 100
        
        # Get real balance from MEXC API
        usdt_balance = 0
        try:
            mexc_balance = mexc_client.get_account_balance()
            if mexc_balance and mexc_balance.get('QRL', 0) > 0:
                qrl_balance_from_api = mexc_balance.get('QRL', 0)
                usdt_balance = mexc_balance.get('USDT', 0)
                
                # Update total_qrl with real data from API
                total_qrl = qrl_balance_from_api
                # Recalculate position layers based on actual balance
                if not layers_data:
                    core_qrl = total_qrl * 0.7
                    swing_qrl = total_qrl * 0.2
                    active_qrl = total_qrl * 0.1
                    core_percent = 70
                    swing_percent = 20
                    active_percent = 10
                logger.info(f"Dashboard: Using real MEXC balance - QRL: {qrl_balance_from_api}, USDT: {usdt_balance}")
            else:
                # Fallback to mock data if API fails or returns no balance
                usdt_balance = 500
                logger.warning("Dashboard: Using fallback mock data for balance")
        except Exception as e:
            logger.error(f"Dashboard: Error fetching MEXC balance: {e}")
            usdt_balance = 500
        
        # Get real price from MEXC API (use correct symbol format with slash)
        try:
            mexc_price = mexc_client.get_ticker_price('QRL/USDT')
            if mexc_price and mexc_price > 0:
                latest_price = mexc_price
                # Update price in Redis for other components
                try:
                    redis_client.set_latest_price(latest_price)
                except Exception as e:
                    logger.warning(f"Dashboard: Cannot update price in Redis: {e}")
                logger.info(f"Dashboard: Using real MEXC price: {latest_price}")
            else:
                logger.warning(f"Dashboard: MEXC price not available, using Redis price: {latest_price}")
        except Exception as e:
            logger.error(f"Dashboard: Error fetching MEXC price: {e}")
            logger.warning(f"Dashboard: Using Redis price: {latest_price}")
        
        total_value = (total_qrl * latest_price) + usdt_balance if latest_price > 0 else usdt_balance
        usdt_reserve_percent = (usdt_balance / total_value * 100) if total_value > 0 else 0
        
        # Prepare template data
        template_data = {
            'bot_status': bot_status,
            'balance': {
                'qrl': total_qrl,
                'usdt': usdt_balance,
                'total_value': total_value
            },
            'price': {
                'current': latest_price,
                'avg_cost': avg_cost,
                'pnl_percent': pnl_percent
            },
            'layers': {
                'core_qrl': core_qrl,
                'swing_qrl': swing_qrl,
                'active_qrl': active_qrl,
                'core_percent': core_percent,
                'swing_percent': swing_percent,
                'active_percent': active_percent
            },
            'daily_trades': daily_trades,
            'max_daily_trades': config.MAX_DAILY_TRADES,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'usdt_reserve_percent': usdt_reserve_percent,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render_template('dashboard.html', **template_data)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        # Return a simple error page instead of 500
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>QRL Trading Bot - Error</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .error {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; }}
                h1 {{ color: #d32f2f; }}
                pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>⚠️ 服務暫時無法使用</h1>
                <p>儀表板載入失敗，可能原因：</p>
                <ul>
                    <li>Redis 連接失敗</li>
                    <li>MEXC API 連接失敗</li>
                    <li>環境變數未正確配置</li>
                </ul>
                <h3>錯誤詳情：</h3>
                <pre>{str(e)}</pre>
                <p><a href="/">← 返回首頁</a></p>
            </div>
        </body>
        </html>
        """
        return error_html, 503


@app.route('/favicon.ico')
def favicon():
    """
    Favicon endpoint - return empty response to prevent 404/503 errors
    """
    return '', 204


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint for Cloud Run
    Verifies Redis connection and bot status
    """
    try:
        redis_healthy = redis_client.health_check()
        bot_status = redis_client.get_bot_status()
        
        health_status = {
            'status': 'healthy' if redis_healthy else 'unhealthy',
            'redis': 'connected' if redis_healthy else 'disconnected',
            'bot_status': bot_status or 'unknown',
            'timestamp': int(time.time()) if 'time' in dir() else 0
        }
        
        status_code = 200 if redis_healthy else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@app.route('/execute', methods=['POST'])
def execute_trading():
    """
    Main trading execution endpoint
    Triggered by Cloud Scheduler
    """
    try:
        logger.info("Trading execution triggered")
        
        # Verify request (optional: check for Cloud Scheduler headers)
        # In production, validate the request comes from Cloud Scheduler
        
        # Execute trading bot
        result = trading_bot.run()
        
        response = {
            'success': result['success'],
            'message': result['message'],
            'phase': result['phase'],
            'execution_time': result['execution_time']
        }
        
        status_code = 200 if result['success'] else 500
        logger.info(f"Trading execution completed: {response}")
        
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Trading execution failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/status', methods=['GET'])
def get_status():
    """
    Get current bot status and statistics
    """
    try:
        status = redis_client.get_bot_status()
        position = redis_client.get_position()
        latest_price = redis_client.get_latest_price()
        daily_trades = redis_client.get_daily_trades()
        last_trade_time = redis_client.get_last_trade_time()
        
        return jsonify({
            'bot_status': status or 'unknown',
            'position': position,
            'latest_price': latest_price,
            'daily_trades': daily_trades,
            'last_trade_time': last_trade_time,
            'max_daily_trades': config.MAX_DAILY_TRADES
        })
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/control', methods=['POST'])
def control_bot():
    """
    Control bot status (start/pause/stop)
    """
    try:
        data = request.get_json()
        action = data.get('action', '').lower()
        
        if action not in ['start', 'pause', 'stop']:
            return jsonify({
                'error': 'Invalid action. Use: start, pause, or stop'
            }), 400
        
        # Map actions to status
        status_map = {
            'start': 'running',
            'pause': 'paused',
            'stop': 'stopped'
        }
        
        new_status = status_map[action]
        redis_client.set_bot_status(new_status)
        
        logger.info(f"Bot status changed to: {new_status}")
        
        return jsonify({
            'success': True,
            'status': new_status,
            'message': f'Bot {action}ed successfully'
        })
        
    except Exception as e:
        logger.error(f"Control action failed: {e}")
        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    logger.info(f"Starting QRL Trading Bot on port {config.PORT}")
    logger.info(f"Trading pair: {config.TRADING_PAIR}")
    logger.info(f"Redis: {config.REDIS_URL}")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.DEBUG
    )

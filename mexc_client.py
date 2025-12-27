"""
MEXC API Client for QRL Trading Bot using CCXT
Handles market data and account information retrieval
"""
import ccxt
import logging
import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Any
from config import config

logger = logging.getLogger(__name__)


class MEXCClient:
    """
    MEXC API Client using CCXT library
    Provides reliable exchange connectivity with built-in error handling
    """
    
    def __init__(self):
        """Initialize MEXC client with CCXT"""
        try:
            self.exchange = ccxt.mexc({
                'apiKey': config.MEXC_API_KEY,
                'secret': config.MEXC_API_SECRET,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })
            
            # Set subaccount if configured
            if config.MEXC_SUBACCOUNT:
                self.exchange.headers = {
                    **self.exchange.headers,
                    'MX-BROKER-ID': config.MEXC_SUBACCOUNT
                }
            
            self.symbol = 'QRL/USDT'
            self.markets_loaded = False
            
            logger.info("MEXC client initialized successfully with CCXT")
            
        except Exception as e:
            logger.error(f"Failed to initialize MEXC client: {e}")
            self.exchange = None
    
    def _ensure_markets_loaded(self) -> bool:
        """
        Ensure markets are loaded before making requests
        
        Returns:
            bool: True if markets loaded successfully
        """
        if not self.exchange:
            return False
            
        if not self.markets_loaded:
            try:
                self.exchange.load_markets()
                self.markets_loaded = True
                logger.info("Markets loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load markets: {e}")
                return False
        
        return True
    
    def get_account_balance(self) -> Optional[Dict[str, float]]:
        """
        Get account balances for QRL and USDT using CCXT
        
        Returns:
            dict: {'QRL': amount, 'USDT': amount} or None if failed
        """
        try:
            if not self.exchange:
                logger.warning("MEXC exchange not initialized")
                return {'QRL': 0.0, 'USDT': 0.0}
            
            if not self._ensure_markets_loaded():
                return {'QRL': 0.0, 'USDT': 0.0}
            
            # Fetch balance using CCXT
            balance = self.exchange.fetch_balance()
            
            # Extract QRL and USDT balances (total = free + used)
            qrl_balance = balance.get('QRL', {})
            usdt_balance = balance.get('USDT', {})
            
            result = {
                'QRL': float(qrl_balance.get('total', 0)),
                'USDT': float(usdt_balance.get('total', 0))
            }
            
            logger.info(f"Account balance - QRL: {result['QRL']:.4f}, USDT: {result['USDT']:.2f}")
            return result
            
        except ccxt.AuthenticationError as e:
            logger.error(f"Authentication error fetching balance: {e}")
            return None
        except ccxt.NetworkError as e:
            logger.error(f"Network error fetching balance: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return None
    
    def get_ticker_price(self, symbol: str = None) -> Optional[float]:
        """
        Get current ticker price using CCXT
        
        Args:
            symbol: Trading pair symbol (default: QRL/USDT)
            
        Returns:
            float: Current price or None if failed
        """
        try:
            if not self.exchange:
                logger.warning("MEXC exchange not initialized")
                return None
            
            if not self._ensure_markets_loaded():
                return None
            
            symbol = symbol or self.symbol
            
            # Fetch ticker using CCXT
            ticker = self.exchange.fetch_ticker(symbol)
            price = float(ticker.get('last', 0))
            
            logger.info(f"Ticker price for {symbol}: {price}")
            return price
            
        except ccxt.NetworkError as e:
            logger.error(f"Network error fetching ticker: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting ticker price: {e}")
            return None
    
    def get_klines(self, symbol: str = None, timeframe: str = '1h', limit: int = 100) -> Optional[List[float]]:
        """
        Get candlestick/kline data using CCXT
        
        Args:
            symbol: Trading pair symbol (default: QRL/USDT)
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of klines to fetch (max 1000)
            
        Returns:
            list: List of closing prices or None if failed
        """
        try:
            if not self.exchange:
                logger.warning("MEXC exchange not initialized")
                return None
            
            if not self._ensure_markets_loaded():
                return None
            
            symbol = symbol or self.symbol
            
            # Fetch OHLCV data using CCXT
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Extract closing prices (index 4 in OHLCV)
            # OHLCV format: [timestamp, open, high, low, close, volume]
            prices = [float(candle[4]) for candle in ohlcv]
            
            logger.info(f"Fetched {len(prices)} klines for {symbol} ({timeframe})")
            return prices
            
        except ccxt.NetworkError as e:
            logger.error(f"Network error fetching klines: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting klines: {e}")
            return None
    
    def get_ohlcv_dataframe(self, symbol: str = None, timeframe: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Get OHLCV data as pandas DataFrame for technical analysis
        
        Args:
            symbol: Trading pair symbol (default: QRL/USDT)
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of candles to fetch
            
        Returns:
            DataFrame: OHLCV data or None if failed
        """
        try:
            if not self.exchange:
                logger.warning("MEXC exchange not initialized")
                return None
            
            if not self._ensure_markets_loaded():
                return None
            
            symbol = symbol or self.symbol
            
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"Fetched {len(df)} OHLCV rows for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error getting OHLCV dataframe: {e}")
            return None
    
    def calculate_moving_average(self, period: int = 20) -> Optional[float]:
        """
        Calculate moving average for the symbol
        
        Args:
            period: MA period (default: 20)
            
        Returns:
            float: Moving average or None if failed
        """
        try:
            prices = self.get_klines(limit=period + 10)
            if not prices or len(prices) < period:
                logger.warning(f"Insufficient data for MA({period})")
                return None
            
            # Calculate MA using numpy
            ma = np.mean(prices[-period:])
            logger.info(f"MA({period}): {ma:.6f}")
            return float(ma)
            
        except Exception as e:
            logger.error(f"Error calculating MA: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Check if MEXC API is accessible
        
        Returns:
            bool: True if API is healthy
        """
        try:
            if not self.exchange:
                return False
            
            # Try to fetch ticker (public endpoint)
            ticker = self.exchange.fetch_ticker(self.symbol)
            return ticker is not None
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_exchange_info(self) -> Optional[Dict]:
        """
        Get exchange and market information
        
        Returns:
            dict: Exchange info or None if failed
        """
        try:
            if not self.exchange:
                return None
            
            if not self._ensure_markets_loaded():
                return None
            
            market = self.exchange.market(self.symbol)
            
            info = {
                'symbol': self.symbol,
                'base': market.get('base'),
                'quote': market.get('quote'),
                'active': market.get('active'),
                'precision': market.get('precision'),
                'limits': market.get('limits')
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting exchange info: {e}")
            return None


# Create singleton instance
mexc_client = MEXCClient()

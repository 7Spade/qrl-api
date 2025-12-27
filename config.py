"""
Configuration module for QRL Trading Bot
Manages environment variables and application settings
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""
    
    # Flask settings
    PORT = int(os.getenv('PORT', '8080'))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Redis settings
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    
    # Trading settings
    TRADING_PAIR = os.getenv('TRADING_PAIR', 'QRL-USDT')
    MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', '5'))
    MAX_POSITION_PERCENT = float(os.getenv('MAX_POSITION_PERCENT', '10.0'))
    
    # MEXC API settings (stored in Secret Manager in production)
    MEXC_API_KEY = os.getenv('MEXC_API_KEY', '')
    MEXC_API_SECRET = os.getenv('MEXC_API_SECRET', '')
    MEXC_BASE_URL = os.getenv('MEXC_BASE_URL', 'https://api.mexc.com')
    
    # Strategy settings
    SHORT_MA_PERIOD = int(os.getenv('SHORT_MA_PERIOD', '5'))
    LONG_MA_PERIOD = int(os.getenv('LONG_MA_PERIOD', '20'))
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERSOLD = float(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT = float(os.getenv('RSI_OVERBOUGHT', '70'))
    
    # Risk management
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '3.0'))
    TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', '5.0'))
    MAX_DAILY_LOSS_PERCENT = float(os.getenv('MAX_DAILY_LOSS_PERCENT', '5.0'))


# Create a singleton config instance
config = Config()

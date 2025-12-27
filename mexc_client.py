"""
MEXC API Client for QRL Trading Bot
Handles market data and account information retrieval
"""
import hashlib
import hmac
import time
import requests
import logging
from typing import Dict, Optional, Any
from config import config

logger = logging.getLogger(__name__)


class MEXCClient:
    """
    MEXC API Client for spot trading
    Supports subaccount operations
    """
    
    def __init__(self):
        """Initialize MEXC client with API credentials"""
        self.api_key = config.MEXC_API_KEY
        self.api_secret = config.MEXC_API_SECRET
        self.subaccount = config.MEXC_SUBACCOUNT
        self.base_url = config.MEXC_BASE_URL
        
        # API endpoints
        self.endpoints = {
            'account': '/api/v3/account',
            'ticker': '/api/v3/ticker/price',
            'klines': '/api/v3/klines',
        }
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate HMAC SHA256 signature for authenticated requests
        
        Args:
            params: Request parameters
            
        Returns:
            str: HMAC signature
        """
        query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, signed: bool = False) -> Optional[Dict]:
        """
        Make HTTP request to MEXC API
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            signed: Whether request requires signature
            
        Returns:
            dict: API response or None if failed
        """
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                'X-MEXC-APIKEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            if params is None:
                params = {}
            
            if signed:
                params['timestamp'] = int(time.time() * 1000)
                params['recvWindow'] = 5000
                params['signature'] = self._generate_signature(params)
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling MEXC API: {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling MEXC API {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in MEXC API call: {e}")
            return None
    
    def get_account_balance(self) -> Optional[Dict[str, float]]:
        """
        Get account balances for QRL and USDT
        
        Returns:
            dict: {'QRL': amount, 'USDT': amount} or None if failed
        """
        try:
            # Check if API credentials are configured
            if not self.api_key or not self.api_secret:
                logger.warning("MEXC API credentials not configured")
                return {'QRL': 0.0, 'USDT': 0.0}
            
            account_data = self._make_request(self.endpoints['account'], signed=True)
            
            if not account_data:
                logger.error("Failed to fetch account data")
                return None
            
            balances = {}
            for balance in account_data.get('balances', []):
                asset = balance.get('asset')
                if asset in ['QRL', 'USDT']:
                    free = float(balance.get('free', 0))
                    locked = float(balance.get('locked', 0))
                    balances[asset] = free + locked
            
            # Ensure both assets exist in response
            balances.setdefault('QRL', 0.0)
            balances.setdefault('USDT', 0.0)
            
            logger.info(f"Account balance - QRL: {balances['QRL']}, USDT: {balances['USDT']}")
            return balances
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return None
    
    def get_ticker_price(self, symbol: str = 'QRLUSDT') -> Optional[float]:
        """
        Get current ticker price for a symbol
        
        Args:
            symbol: Trading pair symbol (default: QRLUSDT)
            
        Returns:
            float: Current price or None if failed
        """
        try:
            params = {'symbol': symbol}
            ticker_data = self._make_request(self.endpoints['ticker'], params=params, signed=False)
            
            if not ticker_data:
                logger.error(f"Failed to fetch ticker price for {symbol}")
                return None
            
            price = float(ticker_data.get('price', 0))
            logger.info(f"Ticker price for {symbol}: {price}")
            return price
            
        except Exception as e:
            logger.error(f"Error getting ticker price: {e}")
            return None
    
    def get_klines(self, symbol: str = 'QRLUSDT', interval: str = '1h', limit: int = 100) -> Optional[list]:
        """
        Get candlestick/kline data for price history
        
        Args:
            symbol: Trading pair symbol
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of klines to fetch (max 1000)
            
        Returns:
            list: List of kline data or None if failed
        """
        try:
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': min(limit, 1000)
            }
            
            klines_data = self._make_request(self.endpoints['klines'], params=params, signed=False)
            
            if not klines_data:
                logger.error(f"Failed to fetch klines for {symbol}")
                return None
            
            # Parse klines data
            # Each kline: [timestamp, open, high, low, close, volume, ...]
            prices = [float(kline[4]) for kline in klines_data]  # Close prices
            
            logger.info(f"Fetched {len(prices)} klines for {symbol}")
            return prices
            
        except Exception as e:
            logger.error(f"Error getting klines: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Check if MEXC API is accessible
        
        Returns:
            bool: True if API is healthy
        """
        try:
            # Try to fetch ticker price (public endpoint, no auth required)
            ticker_data = self._make_request(self.endpoints['ticker'], params={'symbol': 'QRLUSDT'}, signed=False)
            return ticker_data is not None
        except Exception:
            return False


# Create singleton instance
mexc_client = MEXCClient()

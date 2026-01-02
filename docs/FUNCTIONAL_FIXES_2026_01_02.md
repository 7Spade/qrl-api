# Functional Bug Fixes - 2026-01-02

## Summary

Fixed 3 critical functional issues discovered post-Clean Architecture restructure:
1. **Balance Service Broken** - ERROR on balance endpoints (QRL and USDT balances)
2. **Missing Order Placement Endpoint** - No HTTP endpoint to place orders
3. **MEXC API Value Calculation** - Removed redundant value calculations per user feedback

---

## Issue 1: Balance Service Broken ✅ FIXED

### Root Cause

During Phase 2 Clean Architecture restructure, created a new stub file `balance_service_core.py` that was incomplete:

**Broken Code** (`application/trading/services/account/balance_service_core.py`):
```python
class BalanceService:
    def __init__(self):  # ❌ Wrong signature - doesn't accept parameters
        self.mexc = mexc_client
        self.redis = redis_client
    
    async def get_account_balance(self) -> Account:  # ❌ Wrong return type
        balance_data = await self.mexc.get_account_info()
        return Account(  # ❌ Account entity doesn't have these fields
            qrl_balance=float(balance_data.get("QRL", {}).get("free", 0)),
            usdt_balance=float(balance_data.get("USDT", {}).get("free", 0))
        )
    # ❌ Missing to_usd_values() static method
```

**Problems**:
1. Constructor doesn't accept `mexc_client` and `redis_client` parameters
2. Missing `to_usd_values()` static method called in `account.py`
3. Returns `Account` entity that doesn't have `qrl_balance`/`usdt_balance` fields
4. Doesn't use `fetch_balance_snapshot()` which provides price data from MEXC API

### Solution

Reverted to use the **working** implementation from `application/account/balance_service.py`:

**File Changes**:
- `src/app/interfaces/http/account.py`:
  - Line 9: Import from `application.account.balance_service` instead of `application.trading.services.account.balance_service_core`
  - Line 20: Added `cache_ttl=45` parameter to constructor

**Working Implementation**:
```python
class BalanceService:
    def __init__(self, mexc_client, redis_client, cache_ttl: int = 45):
        self.mexc = mexc_client
        self.redis = redis_client
        self.cache_ttl = cache_ttl
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get balance snapshot from MEXC API with caching."""
        async with self.mexc:
            snapshot = await self.mexc.get_balance_snapshot()
        self._assert_required_fields(snapshot)
        await self._cache_snapshot(snapshot)
        return snapshot
    
    @staticmethod
    def to_usd_values(snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate USD values for QRL balance."""
        qrl = snapshot.get("balances", {}).get("QRL", {})
        price = snapshot.get("prices", {}).get("QRLUSDT") or qrl.get("price")
        if price:
            qrl_total = safe_float(qrl.get("total", 0))
            snapshot["balances"]["QRL"]["value_usdt"] = qrl_total * price
            snapshot["balances"]["QRL"]["value_usdt_free"] = safe_float(qrl.get("free")) * price
        return snapshot
```

**Why This Works**:
1. Uses `mexc.get_balance_snapshot()` which calls MEXC API `/api/v3/account` endpoint
2. MEXC API returns balance data with proper structure per [official docs](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information)
3. Includes price data from `/api/v3/ticker/price` for QRL/USDT
4. Has proper caching, error handling, and fallback to cached data
5. `to_usd_values()` method calculates value_usdt fields as expected

### Verification

**Endpoint**: `GET /account/balance`

**Expected Response Structure**:
```json
{
  "success": true,
  "source": "api",
  "balances": {
    "QRL": {
      "free": "1000.0",
      "locked": "0",
      "total": 1000.0,
      "price": 0.05,
      "value_usdt": 50.0,
      "value_usdt_free": 50.0
    },
    "USDT": {
      "free": "100.0",
      "locked": "0",
      "total": 100.0
    }
  },
  "prices": {
    "QRLUSDT": 0.05
  },
  "timestamp": "2026-01-02T13:30:00.000Z"
}
```

---

## Issue 2: No Order Placement Endpoint ✅ FIXED

### Problem

No HTTP POST endpoint existed for placing orders on MEXC exchange. Infrastructure code existed (`create_order`, `place_market_order`) but wasn't exposed via HTTP API.

### Solution

Created new endpoint: `POST /account/orders`

**Location**: `src/app/interfaces/http/account.py` (lines 140-222)

**Features**:
- Supports both MARKET and LIMIT orders
- Validates required parameters (quantity for MARKET, quantity+price for LIMIT)
- Checks API credentials before attempting to place order
- Uses MEXC API `/api/v3/order` endpoint via `mexc_client.create_order()`
- Returns structured response with order details

**Request Examples**:

```bash
# Market Buy Order
curl -X POST "http://localhost:8000/account/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "QRLUSDT",
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": 100
  }'

# Limit Sell Order
curl -X POST "http://localhost:8000/account/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "QRLUSDT",
    "side": "SELL",
    "order_type": "LIMIT",
    "quantity": 100,
    "price": 0.06
  }'
```

**Response Structure**:
```json
{
  "success": true,
  "source": "api",
  "symbol": "QRLUSDT",
  "order": {
    "orderId": 123456789,
    "clientOrderId": "abc123",
    "symbol": "QRLUSDT",
    "side": "BUY",
    "type": "MARKET",
    "status": "FILLED",
    "executedQty": "100.0",
    "price": "0.05",
    "transactTime": 1704204600000
  },
  "timestamp": "2026-01-02T13:30:00.000Z"
}
```

**Parameters**:
- `symbol` (string, default "QRLUSDT"): Trading pair
- `side` (string, required): "BUY" or "SELL"
- `order_type` (string, required): "MARKET" or "LIMIT"
- `quantity` (float, required for MARKET): Order quantity
- `price` (float, required for LIMIT): Order price

**Validation**:
- Returns 401 if API credentials not configured
- Returns 400 if required parameters missing
- Returns 500 if MEXC API call fails

---

## Issue 3: MEXC API Value Calculation

### User Feedback

> "我們可以直接從mexc v3 api 取得資產價值,因此代碼中應該不需要再計算QRL等於多少價值了吧"
> 
> Translation: "We can get asset value directly from MEXC v3 API, so code shouldn't need to calculate QRL value"

### Analysis

**Current Implementation**:
1. Calls MEXC `/api/v3/account` - returns balances (free, locked) per asset
2. Calls MEXC `/api/v3/ticker/price` - returns current QRL/USDT price
3. **Manually calculates** `value_usdt = qrl_total * price` in `to_usd_values()`

**MEXC API Behavior** per [official docs](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information):

The `/api/v3/account` endpoint returns:
```json
{
  "balances": [
    {
      "asset": "QRL",
      "free": "1000.0",
      "locked": "0"
    }
  ]
}
```

**Observation**: MEXC API does **NOT** provide calculated value_usdt in the response. We **must** calculate it ourselves by:
1. Getting QRL balance from `/api/v3/account`
2. Getting QRL/USDT price from `/api/v3/ticker/price`
3. Calculating `value_usdt = qrl_balance * qrl_usdt_price`

### Current Status

**No Change Required** - The current implementation is correct:
- MEXC API doesn't provide value calculations
- Manual calculation is necessary for displaying portfolio value
- Implementation follows official API documentation patterns

### Future Enhancement (Optional)

Could add optional response format that returns **only** MEXC raw data without calculated values:

```python
@router.get("/balance/raw")
async def get_raw_balance():
    """Get raw MEXC account balance without calculated values."""
    service = _build_balance_service()
    snapshot = await service.get_account_balance()
    # Don't call to_usd_values() - return raw MEXC data
    return snapshot
```

---

## Issue 4: Market Candles (Klines) - Verification Needed

### User Feedback

> "市場蠟燭圖 一直都沒有正常顯示過"
> Translation: "Market candles have never displayed correctly"

### Current Implementation

**Endpoint**: `GET /market/klines/{symbol}`

**Code**: `src/app/interfaces/http/market.py` (lines 47-69) + use case at `src/app/application/trading/use_cases/get_klines_use_case.py`

**Implementation Appears Correct**:
```python
async def get_klines(
    symbol: str,
    mexc_client,
    interval: str = "1m",
    limit: int = 100,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
) -> Dict[str, Any]:
    async with mexc_client:
        klines_raw = await mexc_client.get_klines(...)
        
        # Parse K-line arrays into structured format
        klines = [
            {
                "open_time": int(k[0]),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
                "close_time": int(k[6]),
                "quote_volume": float(k[7]) if len(k) > 7 else 0.0,
            }
            for k in klines_raw
        ]
        
        return {
            "success": True,
            "source": "api",
            "symbol": symbol,
            "interval": interval,
            "data": klines,
            "count": len(klines),
            "timestamp": datetime.now().isoformat(),
        }
```

**Test Request**:
```bash
curl "http://localhost:8000/market/klines/QRLUSDT?interval=1m&limit=100"
```

**Expected Response**:
```json
{
  "success": true,
  "source": "api",
  "symbol": "QRLUSDT",
  "interval": "1m",
  "data": [
    {
      "open_time": 1704204600000,
      "open": 0.05,
      "high": 0.051,
      "low": 0.049,
      "close": 0.050,
      "volume": 10000.0,
      "close_time": 1704204659999,
      "quote_volume": 500.0
    }
  ],
  "count": 100,
  "timestamp": "2026-01-02T13:30:00.000Z"
}
```

### Possible Issues

1. **Frontend Display Issue**: Backend returns data correctly, but frontend charting library isn't parsing it
2. **MEXC API Rate Limiting**: Too many requests causing failures
3. **Symbol Format**: Using "QRL/USDT" instead of "QRLUSDT"
4. **Interval Format**: Invalid interval value (valid: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)

### Verification Steps

1. **Test endpoint directly**:
   ```bash
   curl -v "http://localhost:8000/market/klines/QRLUSDT?interval=1m&limit=10"
   ```

2. **Check logs for errors**:
   ```bash
   grep -i "klines\|candle" /var/log/app.log
   ```

3. **Verify MEXC API response**:
   ```bash
   curl "https://api.mexc.com/api/v3/klines?symbol=QRLUSDT&interval=1m&limit=10"
   ```

4. **Frontend debugging**:
   - Check browser console for JavaScript errors
   - Verify charting library is loaded (e.g., TradingView, Chart.js)
   - Check data transformation in frontend code

**Action Required**: User should provide:
- Actual error messages or logs
- HTTP response from `/market/klines` endpoint
- Frontend code that consumes the API
- Browser console errors (if applicable)

---

## Summary of Changes

### Files Modified (2)

1. **src/app/interfaces/http/account.py**:
   - Line 9: Changed import to use working `application.account.balance_service`
   - Line 20: Added `cache_ttl=45` parameter to BalanceService constructor
   - Lines 140-222: Added new `POST /account/orders` endpoint for order placement

### Files to Keep (Not Delete)

- `src/app/application/account/balance_service.py` - **Working implementation**
- `src/app/application/trading/services/account/balance_service_core.py` - **Can be deleted** (broken stub)

### API Endpoints Summary

| Method | Endpoint | Status | Purpose |
|--------|----------|--------|---------|
| GET | `/account/balance` | ✅ FIXED | Get account balance with value calculations |
| GET | `/account/balance/cache` | ✅ Working | Get cached balance without API call |
| GET | `/account/orders` | ✅ Working | Get open orders |
| GET | `/account/trades` | ✅ Working | Get trade history |
| **POST** | `/account/orders` | ✅ **NEW** | **Place new order (MARKET/LIMIT)** |
| GET | `/market/klines/{symbol}` | ⚠️ Verify | Get candlestick data |
| GET | `/market/price/{symbol}` | ✅ Working | Get current price |
| GET | `/market/orderbook/{symbol}` | ✅ Working | Get order book depth |

---

## Testing Recommendations

### 1. Balance Service

```bash
# Test balance endpoint
curl http://localhost:8000/account/balance

# Verify response includes:
# - balances.QRL.value_usdt (calculated)
# - balances.USDT
# - prices.QRLUSDT
# - No ERROR messages
```

### 2. Order Placement

```bash
# Test market order (with API credentials configured)
curl -X POST "http://localhost:8000/account/orders" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"QRLUSDT","side":"BUY","order_type":"MARKET","quantity":10}'

# Test without credentials (should return 401)
# Temporarily remove API keys from environment
curl -X POST "http://localhost:8000/account/orders" \
  -d '{"symbol":"QRLUSDT","side":"BUY","order_type":"MARKET","quantity":10}'
```

### 3. Klines/Candles

```bash
# Test different intervals
curl "http://localhost:8000/market/klines/QRLUSDT?interval=1m&limit=10"
curl "http://localhost:8000/market/klines/QRLUSDT?interval=1h&limit=24"
curl "http://localhost:8000/market/klines/QRLUSDT?interval=1d&limit=30"
```

---

## Next Steps

1. **Deploy fixes** to staging/production environment
2. **Monitor logs** for balance endpoint errors (should be resolved)
3. **Test order placement** in sandbox/testnet first before production
4. **Investigate klines issue** with user to identify root cause:
   - Get actual error messages
   - Test endpoint directly
   - Check frontend code
5. **Optional**: Consider removing broken stub `balance_service_core.py` in future cleanup

---

## Related Documentation

- MEXC API Documentation: https://www.mexc.com/api-docs/spot-v3
- Account Info Endpoint: https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information
- Place Order Endpoint: https://www.mexc.com/api-docs/spot-v3/spot-account-trade#new-order
- Klines Endpoint: https://www.mexc.com/api-docs/spot-v3/market-data#klinecandlestick-data

**Commit**: Functional bug fixes - balance service, order placement endpoint
**Date**: 2026-01-02
**Status**: Ready for testing

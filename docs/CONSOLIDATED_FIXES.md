# QRL Trading API - Fixes & Issue Resolution

**Last Updated**: 2025-12-27  
**Purpose**: Consolidated documentation of all fixes, issues, and resolutions

## Table of Contents
- [Critical Fixes Overview](#critical-fixes-overview)
- [Redis & Data Persistence](#redis--data-persistence)
- [Cloud Scheduler Authentication](#cloud-scheduler-authentication)
- [Dashboard Logic](#dashboard-logic)
- [Position Display](#position-display)
- [Sub-Account Management](#sub-account-management)
- [Code Quality Improvements](#code-quality-improvements)

---

## Critical Fixes Overview

### Summary of All Fixes
| Issue | Problem | Solution | Status |
|-------|---------|----------|--------|
| #24 | Redis TTL data expiration | Removed TTL, dual-storage strategy | ✅ Fixed |
| #25 | Incomplete MEXC data storage | Store raw API responses | ✅ Fixed |
| N/A | Cloud Scheduler auth failure | Support OIDC authentication | ✅ Fixed |
| N/A | Dashboard data inconsistency | Remove Redis fallback for balance | ✅ Fixed |
| #12 | Position display incorrect | Fix data source logic | ✅ Fixed |
| #1 | Deprecated FastAPI patterns | Lifespan context manager | ✅ Fixed |
| N/A | Redis connection management | Connection pooling | ✅ Fixed |
| N/A | Redis close method | Use aclose() properly | ✅ Fixed |

---

## Redis & Data Persistence

### Issue #24: Redis TTL Causing Data Loss

**Problem Details**:
1. `set_latest_price()` used 30-second TTL
2. Cloud Scheduler runs every 3 minutes
3. Data expired before next scheduled update
4. Result: Scheduler found no data, causing failures

**Root Cause**:
```python
# Before - Data expires after 30 seconds
await self.client.set(key, json.dumps(data), ex=config.CACHE_TTL_PRICE)  # ex=30
```

**Solution Implemented**:
```python
# After - Permanent storage for scheduled tasks
await self.client.set(key, json.dumps(data))  # No TTL

# Separate cached layer for API queries
await self.client.set(cache_key, json.dumps(data), ex=30)  # 30s cache
```

**Dual-Storage Strategy**:
```
┌─────────────────────────┐     ┌─────────────────────────┐
│   Permanent Storage     │     │    Cached Storage       │
│   (No TTL)              │     │    (30s TTL)            │
├─────────────────────────┤     ├─────────────────────────┤
│ • Latest price          │     │ • Cached price          │
│ • Position data         │     │   (for API queries)     │
│ • Cost tracking         │     │ • Auto-fallback to      │
│ • Raw API responses     │     │   permanent if expired  │
└─────────────────────────┘     └─────────────────────────┘
```

**New Redis Methods**:
- `set_latest_price(price, volume)` - Permanent (no TTL)
- `set_cached_price(price, volume)` - Cached (30s TTL)
- `get_cached_price()` - Auto-fallback to permanent
- `set_raw_mexc_response()` - Store complete API responses
- `get_raw_mexc_response_history()` - Query historical data

**Impact**:
- ✅ Cloud Scheduler always finds valid data
- ✅ Historical price tracking enabled
- ✅ No data loss between scheduler runs
- ✅ Performance maintained with cache layer

---

### Issue #25: Incomplete MEXC Response Storage

**Problem Details**:
1. Only QRL/USDT balances stored from `/api/v3/account`
2. Lost important fields:
   - `makerCommission`, `takerCommission`
   - `canTrade`, `canWithdraw`, `canDeposit`
   - `accountType`, `permissions`
   - Other asset balances
3. No way to debug API issues without raw responses

**Solution Implemented**:

**1. Raw Response Storage**:
```python
# Store complete MEXC API response
await redis_client.set_raw_mexc_response(
    endpoint="account_info",
    response_data=mexc_response,  # Complete response
    metadata={"source": "cloud_scheduler", "task": "sync-balance"}
)
```

**2. Enhanced Position Data**:
```python
# Before - Only 2 fields
position = {
    "qrl_balance": "1000.0",
    "usdt_balance": "500.0"
}

# After - Complete data
position = {
    "qrl_balance": "1000.0",
    "usdt_balance": "500.0",
    "qrl_locked": "0.0",
    "usdt_locked": "10.0",
    "all_balances": json.dumps(all_assets),  # All assets
    "account_type": "SPOT",
    "can_trade": "True",
    "can_withdraw": "True",
    "can_deposit": "True",
    "maker_commission": "0.002",
    "taker_commission": "0.002",
    "permissions": json.dumps(["SPOT", "MARGIN"]),
    "update_time": "1735305600000"
}
```

**3. Enhanced Cloud Tasks**:
```python
# task_sync_balance now logs everything
logger.info(
    f"[Cloud Task] Balance synced - "
    f"QRL: {qrl_balance:.4f} (locked: {qrl_locked}), "
    f"USDT: {usdt_balance:.2f} (locked: {usdt_locked}), "
    f"Total assets: {len(all_balances)}, "
    f"Account type: {account_type}, "
    f"canTrade: {can_trade}, "
    f"Maker/Taker: {maker_commission}/{taker_commission}"
)
```

**Redis Keys Created**:
- `mexc:raw:account_info:latest` - Latest account response
- `mexc:raw:account_info:history` - Historical responses (up to 1000)
- `mexc:raw:ticker_24hr:latest` - Latest ticker response
- `mexc:raw:ticker_24hr:history` - Historical ticker data
- `mexc:raw:ticker_price:latest` - Latest price response

**Impact**:
- ✅ Complete visibility into MEXC API responses
- ✅ Easy debugging with raw data inspection
- ✅ Historical tracking for analysis
- ✅ All account fields preserved
- ✅ No guessing - inspect Redis directly

---

## Cloud Scheduler Authentication

### Issue: OIDC Authentication Not Working

**Problem**:
- Cloud Scheduler endpoints only accepted `X-CloudScheduler` header
- Google Cloud Scheduler with OIDC sends `Authorization: Bearer <token>` instead
- All OIDC-authenticated requests were rejected with 401

**Official Documentation**:
According to [Google Cloud Scheduler HTTP Target Auth](https://cloud.google.com/scheduler/docs/http-target-auth):
- OIDC authentication uses `Authorization` header with Bearer token
- `X-CloudScheduler` header is NOT guaranteed to be present
- OIDC is the recommended method

**Solution**:
```python
# Before - Only X-CloudScheduler
x_cloudscheduler = request.headers.get("X-CloudScheduler")
if not x_cloudscheduler:
    raise HTTPException(status_code=401)

# After - Accept both methods
x_cloudscheduler = request.headers.get("X-CloudScheduler")
authorization = request.headers.get("Authorization")

if not x_cloudscheduler and not authorization:
    raise HTTPException(status_code=401, 
        detail="Unauthorized - Cloud Scheduler only")

auth_method = "OIDC" if authorization else "X-CloudScheduler"
logger.info(f"[Cloud Task] Authenticated via {auth_method}")
```

**Updated Endpoints**:
- `/tasks/sync-balance` - Balance synchronization
- `/tasks/update-price` - Price updates
- `/tasks/update-cost` - Cost tracking

**Impact**:
- ✅ Works with OIDC authentication (recommended)
- ✅ Backward compatible with legacy X-CloudScheduler
- ✅ Logging shows which auth method used
- ✅ Follows Google best practices

---

## Dashboard Logic

### Issue: Data Source Inconsistency

**Problem**:
```javascript
// WRONG: Mixed real-time and stale data
if (balances && price) {
    // Real-time API balance (current)
    calculateTotalValue(balances.qrlTotal, balances.usdtTotal, price);
} else if (position && price) {
    // Fallback to Redis data (3 minutes old)
    const qrlBal = parseFloat(position.qrl_balance);
    const usdtBal = parseFloat(position.usdt_balance);
    calculateTotalValue(qrlBal, usdtBal, price);
}
```

**Issues**:
1. Mixed data sources create inconsistency
2. Redis position updated every 3 minutes (stale)
3. API balance is real-time
4. Result: Misleading total value calculations

**Solution**:
```javascript
// CORRECT: One data source only
if (balances && price) {
    // Use real-time API balance
    calculateTotalValue(balances.qrlTotal, balances.usdtTotal, price);
} else {
    // Show error instead of using stale data
    console.error('Failed to load real-time balance from API');
    document.getElementById('total-value').textContent = 'N/A (API Error)';
}

// Redis position data ONLY for bot analytics
if (position) {
    displayAvgCost(position.avg_cost);
    displayUnrealizedPnL(position.unrealized_pnl);
    displayPositionLayers(position.position_layers);
}
```

**Data Flow After Fix**:
```
Real-time API Balance ──────→ Dashboard Balance Display
                              (no fallback, show error if fails)

Redis Position Data ────────→ Bot Analytics Only
(Updated every 3 min)          • avg_cost
                              • unrealized_pnl
                              • position_layers
```

**Impact**:
- ✅ Consistent data sources
- ✅ Transparent error handling
- ✅ Clear separation of concerns
- ✅ Real-time accuracy for balances

---

## Position Display

### Issue #12: Position Display Incorrect

**Problem**:
- Position display mixed data from different sources
- Calculation errors due to inconsistent timestamps

**Solution**:
- Use API balance for current holdings
- Use Redis position for cost basis and PnL calculations
- Clear separation between real-time and analytical data

**Impact**:
- ✅ Accurate position display
- ✅ Correct PnL calculations
- ✅ Consistent data presentation

---

## Sub-Account Management

### Enhancement: Multi-Account Support

**Implementation**:
- Support for multiple MEXC sub-accounts
- Separate position tracking per account
- Consolidated reporting across accounts

**Redis Structure**:
```
bot:QRLUSDT:account:{account_id}:position
bot:QRLUSDT:account:{account_id}:balance
```

**Impact**:
- ✅ Multi-account trading support
- ✅ Isolated position management
- ✅ Aggregate reporting capability

---

## Code Quality Improvements

### FastAPI Lifespan Context Manager (Issue #1)

**Problem**:
- Used deprecated `@app.on_event("startup")` and `@app.on_event("shutdown")`
- Not following FastAPI 0.109+ best practices

**Solution**:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_client.connect()
    await mexc_client.ping()
    yield
    # Shutdown
    await redis_client.close()
    await mexc_client.close()

app = FastAPI(lifespan=lifespan)
```

**Impact**:
- ✅ Modern FastAPI pattern
- ✅ Better resource management
- ✅ Future-proof code

### Redis Connection Pool

**Problem**:
- No connection pooling
- Created new connection for each operation
- Higher latency

**Solution**:
```python
self.pool = redis.ConnectionPool.from_url(
    config.REDIS_URL,
    max_connections=20,
    health_check_interval=30,
    decode_responses=True
)
self.client = redis.Redis(connection_pool=self.pool)
```

**Impact**:
- ✅ Efficient connection reuse
- ✅ Automatic health checks
- ✅ Lower latency
- ✅ Better resource utilization

### Redis Close Method Fix

**Problem**:
```python
# WRONG - Used deprecated method
await self.client.close()  # Doesn't exist in redis.asyncio
```

**Solution**:
```python
# CORRECT - Proper async close
async def close(self):
    if self.client:
        await self.client.aclose()  # Correct async method
        self.connected = False
    if self.pool:
        await self.pool.aclose()    # Clean up pool
```

**Impact**:
- ✅ Proper resource cleanup
- ✅ No connection leaks
- ✅ Follows redis.asyncio API

---

## Verification & Testing

### Manual Verification Steps

**1. Redis TTL Check**:
```bash
# Should return -1 (no expiration)
redis-cli TTL "bot:QRLUSDT:price:latest"

# Should return ~30 or less (cached)
redis-cli TTL "bot:QRLUSDT:price:cached"
```

**2. Raw Response Check**:
```bash
# View latest raw responses
redis-cli GET "mexc:raw:account_info:latest"
redis-cli GET "mexc:raw:ticker_24hr:latest"

# Check history count
redis-cli LLEN "mexc:raw:account_info:history"
```

**3. Position Data Check**:
```bash
# Should have all new fields
redis-cli HGETALL "bot:QRLUSDT:position"
# Look for: qrl_locked, usdt_locked, all_balances, account_type, etc.
```

**4. Cloud Scheduler Logs**:
```bash
# Check authentication method
gcloud logging read "jsonPayload.message=~'authenticated via'" --limit=10

# Verify complete logging
gcloud logging read "jsonPayload.message=~'Balance synced'" --limit=5
```

### Test Scripts

**Available Tests**:
- `test_ttl_fix.py` - Redis TTL verification
- `test_cloud_tasks_storage.py` - Raw response storage
- `test_position_layers.py` - Position layer logic
- `validate_cloud_task_fixes.py` - Code structure validation
- `validate_fixes.py` - General fix validation

**Run All Tests**:
```bash
python test_ttl_fix.py
python test_cloud_tasks_storage.py
python validate_cloud_task_fixes.py
```

---

## Migration & Deployment

### Deployment Checklist

**Pre-deployment**:
- [x] All code changes implemented
- [x] Tests created and passing
- [x] Documentation updated
- [x] Backward compatibility verified

**Deployment**:
```bash
# Deploy to Cloud Run
gcloud builds submit --config cloudbuild.yaml

# Monitor deployment
gcloud run services describe qrl-api --region=us-central1
```

**Post-deployment Verification**:
1. Wait 3+ minutes (longer than old TTL)
2. Check Redis: `TTL bot:QRLUSDT:price:latest` should be `-1`
3. Verify logs show complete field logging
4. Trigger Cloud Scheduler manually
5. Confirm raw responses stored
6. Monitor for 24+ hours

### Rollback Plan

If issues occur:
```bash
# Revert to previous revision
gcloud run services update qrl-api \
  --image=<previous-image> \
  --region=us-central1
```

---

## Summary

All critical fixes implemented and tested:
- ✅ Redis TTL data persistence fixed
- ✅ Complete MEXC API response storage
- ✅ Cloud Scheduler OIDC authentication
- ✅ Dashboard data consistency
- ✅ Modern FastAPI patterns
- ✅ Redis connection pooling
- ✅ Proper resource cleanup

**Ready for production deployment** with comprehensive monitoring and validation in place.

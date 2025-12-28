# QRL Trading API - Implementation Guide

**Last Updated**: 2025-12-27  
**Purpose**: Consolidated guide covering all implementation aspects, fixes, and project status

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Key Implementations](#key-implementations)
- [Critical Fixes](#critical-fixes)
- [Deployment](#deployment)
- [Monitoring](#monitoring)

---

## Project Overview

### What This Project Does
Modern MEXC API trading bot for QRL/USDT using:
- **FastAPI** + **Uvicorn** (async web framework)
- **httpx** (async HTTP client)
- **redis.asyncio** (async state management)
- **Google Cloud Run** (serverless deployment)
- **Google Cloud Scheduler** (automated trading)

### Core Features
- ✅ 6-phase trading system (Startup → Data → Strategy → Risk → Execute → Report)
- ✅ MEXC API v3 integration (public + authenticated endpoints)
- ✅ Redis state management (positions, prices, history)
- ✅ Moving Average Crossover strategy
- ✅ Risk controls (daily limits, position protection, cooldowns)

---

## Architecture

### System Components
```
Cloud Scheduler → Cloud Run → MEXC API
      ↓              ↓
   Redis ←──────────┘
```

### Key Technologies
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | FastAPI + Uvicorn | Async API endpoints |
| HTTP Client | httpx | Async MEXC API calls |
| State Store | redis.asyncio | Position/price/history |
| Deployment | Cloud Run | Serverless hosting |
| Scheduling | Cloud Scheduler | Automated execution |

### Modern Async Architecture
- All I/O operations are async (MEXC API, Redis)
- Proper lifespan management using `asynccontextmanager`
- Connection pooling for Redis (max_connections=20)
- Efficient resource management

---

## Key Implementations

### 1. FastAPI Lifespan Pattern (Issue #1)

**Modern pattern** (FastAPI 0.109+):
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

**Benefits**:
- ✅ Replaces deprecated `@app.on_event` decorators
- ✅ Better resource management
- ✅ Future-proof

### 2. Redis Connection Pool

**Implementation**:
```python
self.pool = redis.ConnectionPool.from_url(
    config.REDIS_URL,
    max_connections=20,
    health_check_interval=30,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
)
self.client = redis.Redis(connection_pool=self.pool)
```

**Benefits**:
- ✅ Efficient connection reuse
- ✅ Automatic health checks
- ✅ Lower latency

### 3. Data Persistence Strategy (Issue #24)

**Dual-storage approach**:
```
Permanent Storage (no TTL) → Historical tracking, scheduled tasks
Cached Storage (30s TTL) → API queries, fast access
```

**Redis Keys**:
- `bot:QRLUSDT:price:latest` - Permanent price (no expiration)
- `bot:QRLUSDT:price:cached` - Cached price (30s TTL)
- `mexc:raw:account_info:*` - Raw MEXC responses
- `mexc:raw:ticker_24hr:*` - Raw ticker data

**Benefits**:
- ✅ Cloud Scheduler data persists between runs
- ✅ Complete MEXC API responses stored
- ✅ Historical tracking enabled

### 4. Cloud Scheduler Authentication

**Accepts both methods**:
```python
x_cloudscheduler = request.headers.get("X-CloudScheduler")
authorization = request.headers.get("Authorization")

if not x_cloudscheduler and not authorization:
    raise HTTPException(status_code=401)
```

**Benefits**:
- ✅ Works with OIDC authentication
- ✅ Backward compatible with legacy auth
- ✅ Logging shows which method used

### 5. Position Layers System

**Three-tier position management**:
```python
position_layers = {
    "core": {"percentage": 70, "min_qrl": 700},      # Never trade
    "swing": {"percentage": 20, "min_qrl": 200},     # Medium-term
    "active": {"percentage": 10, "min_qrl": 100}     # Active trading
}
```

**Benefits**:
- ✅ Core position protected (70%)
- ✅ Controlled risk management
- ✅ Clear position separation

---

## Critical Fixes

### Fix 1: Redis TTL Data Expiration (Issue #24)

**Problem**:
- Price data had 30s TTL
- Cloud Scheduler runs every 3 minutes
- Data expired before next update

**Solution**:
- Removed TTL from `set_latest_price()`
- Added separate cached layer for API queries
- Permanent storage for scheduled tasks

**Impact**:
- ✅ No more data loss between scheduler runs
- ✅ Historical price tracking enabled

### Fix 2: Incomplete MEXC Response Storage

**Problem**:
- Only QRL/USDT balances stored
- Lost commission rates, permissions, account type

**Solution**:
- Added `set_raw_mexc_response()` method
- Store complete API responses permanently
- Enhanced cloud task logging

**Impact**:
- ✅ Full MEXC data available for debugging
- ✅ Complete account information preserved

### Fix 3: Dashboard Data Inconsistency

**Problem**:
- Mixed real-time API data with 3-minute-old Redis cache
- Created inconsistent calculations

**Solution**:
- Removed Redis fallback for balance display
- Redis only used for bot analytics (avg_cost, PnL, layers)
- Show error when API fails instead of stale data

**Impact**:
- ✅ Consistent data sources
- ✅ Transparent error handling
- ✅ Real-time accuracy

### Fix 4: Redis Client Close Method

**Problem**:
- Used `await self.client.close()` (wrong method)
- Connection pool not cleaned up

**Solution**:
```python
async def close(self):
    if self.client:
        await self.client.aclose()  # Correct method
    if self.pool:
        await self.pool.aclose()    # Pool cleanup
```

**Impact**:
- ✅ Proper connection cleanup
- ✅ No resource leaks

---

## Deployment

### Quick Start
```bash
# 1. Local development
cp .env.example .env
# Edit .env with MEXC API keys
pip install -r requirements.txt
uvicorn main:app --reload

# 2. Docker
docker build -t qrl-api .
docker run -p 8080:8080 qrl-api

# 3. Cloud Run
gcloud builds submit --config cloudbuild.yaml
```

### Cloud Scheduler Setup
```bash
# Create OIDC service account
gcloud iam service-accounts create scheduler-sa

# Grant Cloud Run invoker role
gcloud run services add-iam-policy-binding qrl-api \
  --member="serviceAccount:scheduler-sa@PROJECT.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# Create scheduler jobs
gcloud scheduler jobs create http sync-balance \
  --schedule="*/3 * * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/sync-balance" \
  --oidc-service-account-email="scheduler-sa@PROJECT.iam.gserviceaccount.com"
```

### Environment Variables
```bash
# Required
MEXC_API_KEY=your_api_key
MEXC_SECRET_KEY=your_secret_key
REDIS_URL=redis://host:6379/0

# Optional
TRADING_SYMBOL=QRLUSDT
DRY_RUN=false
LOG_LEVEL=INFO
```

---

## Monitoring

### Health Checks
```bash
# Service health
curl https://qrl-api-xxx.run.app/health

# Bot status
curl https://qrl-api-xxx.run.app/status

# API documentation
open https://qrl-api-xxx.run.app/docs
```

### Redis Data Verification
```bash
# Check price data persistence
redis-cli TTL "bot:QRLUSDT:price:latest"  # Should return -1 (no expiration)

# View raw MEXC responses
redis-cli GET "mexc:raw:account_info:latest"
redis-cli GET "mexc:raw:ticker_24hr:latest"

# Check position data
redis-cli HGETALL "bot:QRLUSDT:position"
```

### Cloud Scheduler Logs
```bash
# View recent scheduler executions
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=50 --format=json

# Check for authentication issues
gcloud logging read "severity>=ERROR" --limit=20

# Monitor specific task
gcloud logging read "jsonPayload.message=~'Cloud Task'" --limit=20
```

### Key Metrics to Monitor
- Cloud Scheduler success rate (>98%)
- Redis connection health
- MEXC API response time (<1s)
- Daily trade count (respects limits)
- Position layer distribution

---

## Testing

### Manual Testing
```bash
# Test MEXC API connection
python -c "from mexc_client import mexc_client; import asyncio; asyncio.run(mexc_client.ping())"

# Test Redis connection
python -c "from redis_client import redis_client; import asyncio; asyncio.run(redis_client.health_check())"

# Run test suite
python test_api.py
python test_position_layers.py
python test_cloud_tasks_storage.py
```

### Validation
```bash
# Validate code structure
python validate_cloud_task_fixes.py

# Check for common issues
python validate_fixes.py
```

---

## Additional Resources

### Documentation Files
- **INDEX.md** - Documentation navigation
- **README.md** - Detailed setup and usage (same as docs/README.md)
- **1-qrl-accumulation-strategy.md** - Trading strategy analysis
- **2-bot.md** - Original bot design document
- **3-cost.md** - Cost analysis
- **4-scheduler.md** - Scheduler configuration
- **5-SCHEDULED_TASKS_DESIGN.md** - Task system design
- **6-ARCHITECTURE_CHANGES.md** - Architecture diagrams

### API Documentation
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- MEXC API: https://www.mexc.com/zh-MY/api-docs/spot-v3

---

## Summary

This project is a **production-ready** async trading bot with:
- ✅ Modern FastAPI architecture
- ✅ Comprehensive MEXC API integration
- ✅ Robust data persistence
- ✅ Clear separation of concerns
- ✅ Full monitoring and logging
- ✅ Cloud-native deployment

All critical fixes have been implemented and tested. Ready for production use with proper API keys and monitoring.

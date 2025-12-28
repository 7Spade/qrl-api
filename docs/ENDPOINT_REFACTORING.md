# QRL API Endpoint Refactoring

## Summary of Changes

This update refactors the QRL Trading API to use time-based endpoint naming and fixes QRL/USDT price display issues.

## 1. Endpoint Renaming (Time-Based System)

### Old Endpoints → New Endpoints

| Old Endpoint | New Endpoint | Schedule | Description |
|--------------|--------------|----------|-------------|
| `/tasks/sync-balance` | `/tasks/01-min-job` | Every 1 minute | Sync MEXC account balance to Redis |
| `/tasks/update-price` | `/tasks/05-min-job` | Every 5 minutes | Update QRL/USDT price from MEXC |
| `/tasks/update-cost` | `/tasks/15-min-job` | Every 15 minutes | Update cost and PnL calculations |

### Benefits

- **Clear naming convention**: Job frequency is immediately visible from the endpoint name
- **Better organization**: Time-based grouping makes it easier to understand the system
- **Reduced confusion**: No ambiguity about what each job does

### Files Updated

- `infrastructure/cloud_tasks.py` - Renamed endpoint handlers
- `scheduler-config.yaml` - Updated Cloud Scheduler job configurations
- `cloudbuild-scheduler.yaml` - Updated deployment configuration

## 2. Price Display Fix

### Problem
Market routes were calling Redis caching methods that didn't exist, causing price data to fail silently.

### Solution
Added comprehensive market data caching methods to Redis client:

- `set_ticker_24hr()` / `get_ticker_24hr()` - Cache 24-hour ticker data
- `set_klines()` / `get_klines()` - Cache candlestick/kline data
- `set_order_book()` / `get_order_book()` - Cache order book data
- `set_recent_trades()` / `get_recent_trades()` - Cache recent trades data

### Files Updated

- `infrastructure/external/redis_client.py` - Added market data caching methods
- `api/market_routes.py` - Fixed method call (get_orderbook → get_order_book)

## 3. Price Trend Display Enhancement

### Supported Intervals

The klines endpoint now supports all MEXC intervals with validation:

| Interval | Description | Cache TTL |
|----------|-------------|-----------|
| `1m` | 1 minute | 60 seconds |
| `5m` | 5 minutes | 120 seconds |
| `15m` | 15 minutes | 300 seconds |
| `30m` | 30 minutes | 600 seconds |
| `60m` | 60 minutes | 900 seconds |
| `4h` | 4 hours | 1800 seconds |
| `1d` | 1 day | 3600 seconds |
| `1W` | 1 week | 7200 seconds |
| `1M` | 1 month | 14400 seconds |

### Features

- **Interval validation**: Returns clear error if invalid interval is provided
- **Adaptive caching**: Different TTL for different intervals (longer intervals = longer cache)
- **Comprehensive documentation**: Data format and structure clearly documented

### Files Updated

- `api/market_routes.py` - Enhanced klines endpoint
- `infrastructure/external/mexc_client.py` - Improved documentation

## API Usage Examples

### Get Price Data
```bash
GET /market/price/QRLUSDT
```

### Get 24hr Ticker
```bash
GET /market/ticker/QRLUSDT
```

### Get Klines (Candlestick Data)
```bash
GET /market/klines/QRLUSDT?interval=1m&limit=100
GET /market/klines/QRLUSDT?interval=15m&limit=500
GET /market/klines/QRLUSDT?interval=1d&limit=30
```

### Get Order Book
```bash
GET /market/orderbook/QRLUSDT?limit=100
```

### Get Recent Trades
```bash
GET /market/trades/QRLUSDT?limit=500
```

## Cloud Scheduler Jobs

### Trigger Manually
```bash
# 01-min-job (Balance Sync)
gcloud scheduler jobs run qrl-01-min-job --location=asia-southeast1

# 05-min-job (Price Update)
gcloud scheduler jobs run qrl-05-min-job --location=asia-southeast1

# 15-min-job (Cost Update)
gcloud scheduler jobs run qrl-15-min-job --location=asia-southeast1
```

### View Logs
```bash
gcloud logging read "resource.type=cloud_scheduler_job" --limit=50 --format=json
```

## Migration Notes

### For Existing Deployments

1. The old job names are automatically cleaned up during deployment
2. New jobs are created with the new naming convention
3. No data migration needed - Redis keys remain the same
4. Backward compatible - existing code will continue to work

### Cloud Scheduler Update

Run the Cloud Build deployment to update schedulers:
```bash
gcloud builds submit --config=cloudbuild-scheduler.yaml
```

Or apply the scheduler configuration directly:
```bash
kubectl apply -f scheduler-config.yaml
```

## Testing

### Test Market Endpoints
```bash
# Test price endpoint
curl https://qrl-trading-api-545492969490.asia-southeast1.run.app/market/price/QRLUSDT

# Test klines endpoint
curl "https://qrl-trading-api-545492969490.asia-southeast1.run.app/market/klines/QRLUSDT?interval=1m&limit=10"

# Test ticker endpoint
curl https://qrl-trading-api-545492969490.asia-southeast1.run.app/market/ticker/QRLUSDT
```

### Test Cloud Tasks
```bash
# Test 01-min-job
curl -X POST https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/01-min-job \
  -H "X-CloudScheduler: true" \
  -H "Content-Type: application/json" \
  -d '{}'

# Test 05-min-job
curl -X POST https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/05-min-job \
  -H "X-CloudScheduler: true" \
  -H "Content-Type: application/json" \
  -d '{}'

# Test 15-min-job
curl -X POST https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/15-min-job \
  -H "X-CloudScheduler: true" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## References

- [MEXC API Documentation - Kline/Candlestick Data](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#klinecandlestick-data)
- [MEXC API Documentation - 24hr Ticker](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#24hr-ticker-price-change-statistics)
- [MEXC API Documentation - Order Book](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#order-book)

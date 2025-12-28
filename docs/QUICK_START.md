# Quick Start Guide

**Purpose**: Get the QRL Trading API running in 5 minutes

---

## 🚀 Fastest Path to Running

### Option 1: Local Development (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/7Spade/qrl-api.git
cd qrl-api

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env: Add your MEXC API keys and Redis URL

# 4. Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# 5. Run
uvicorn main:app --reload

# 6. Test
open http://localhost:8080/docs
```

### Option 2: Docker (3 minutes)

```bash
# Clone and build
git clone https://github.com/7Spade/qrl-api.git
cd qrl-api
docker build -t qrl-api .

# Run
docker run -p 8080:8080 \
  -e MEXC_API_KEY=your_key \
  -e MEXC_SECRET_KEY=your_secret \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  qrl-api

# Test
open http://localhost:8080/docs
```

---

## 📝 Required Configuration

### Minimal .env File
```bash
# MEXC API (Get from https://www.mexc.com)
MEXC_API_KEY=your_mexc_api_key
MEXC_SECRET_KEY=your_mexc_secret_key

# Redis (local or remote)
REDIS_URL=redis://localhost:6379/0
```

### Optional Settings
```bash
TRADING_SYMBOL=QRLUSDT
DRY_RUN=true              # Set to false for real trading
LOG_LEVEL=INFO
MAX_TRADES_PER_DAY=5
```

---

## ✅ Verification Checklist

After starting the application:

```bash
# 1. Health check
curl http://localhost:8080/health
# Expected: {"status": "healthy"}

# 2. MEXC API connection
curl http://localhost:8080/market/price/QRLUSDT
# Expected: {"symbol": "QRLUSDT", "price": "0.0xxx"}

# 3. Bot status
curl http://localhost:8080/status
# Expected: Bot state information

# 4. View API documentation
open http://localhost:8080/docs
```

---

## 🎯 Common First Commands

### View Current Price
```bash
curl http://localhost:8080/market/price/QRLUSDT
```

### Check Account Balance
```bash
curl http://localhost:8080/account/balance
```

### Get Bot Status
```bash
curl http://localhost:8080/status
```

### Start Trading (Dry Run)
```bash
curl -X POST http://localhost:8080/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

### Execute One Trade (Manual)
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"dry_run": true}'
```

---

## ⚠️ Common Issues

### Redis Connection Failed
```bash
# Check Redis is running
docker ps | grep redis

# Test Redis connection
redis-cli ping
# Expected: PONG
```

### MEXC API Authentication Failed
```bash
# Verify API keys in .env
cat .env | grep MEXC

# Test MEXC API directly
curl http://localhost:8080/market/price/QRLUSDT
```

### Port Already in Use
```bash
# Use different port
uvicorn main:app --port 8081

# Or kill process on port 8080
lsof -ti:8080 | xargs kill -9
```

---

## 📚 Next Steps

Once running successfully:

1. **Read full documentation**: See [README.md](README.md)
2. **Understand architecture**: See [CONSOLIDATED_IMPLEMENTATION_GUIDE.md](CONSOLIDATED_IMPLEMENTATION_GUIDE.md)
3. **Deploy to cloud**: See [CONSOLIDATED_DEPLOYMENT.md](CONSOLIDATED_DEPLOYMENT.md)
4. **Configure trading strategy**: See [1-qrl-accumulation-strategy.md](1-qrl-accumulation-strategy.md)

---

## 🔗 Essential Links

- **API Documentation**: http://localhost:8080/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health
- **Bot Status**: http://localhost:8080/status

---

## 💡 Pro Tips

- **Always start with DRY_RUN=true** to test without real trades
- **Monitor logs** for errors: check the console output
- **Use Redis CLI** to inspect stored data: `redis-cli`
- **Test API endpoints** using the interactive docs at `/docs`

---

**Ready to start!** Follow Option 1 or Option 2 above and you'll be running in minutes.

For detailed information, see [CONSOLIDATED_DEPLOYMENT.md](CONSOLIDATED_DEPLOYMENT.md).

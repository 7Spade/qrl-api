# QRL Trading API - Deployment Guide

**Last Updated**: 2025-12-27  
**Purpose**: Complete deployment guide for local, Docker, and Google Cloud Run

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Google Cloud Run Deployment](#google-cloud-run-deployment)
- [Cloud Scheduler Setup](#cloud-scheduler-setup)
- [Redis Setup](#redis-setup)
- [Monitoring & Verification](#monitoring--verification)

---

## Prerequisites

### Required Accounts
- ✅ MEXC account with API key (trading permissions only, no withdrawal)
- ✅ Google Cloud Platform account (for Cloud Run deployment)
- ✅ Redis instance (local, Redis Cloud, or Google Memorystore)

### Required Software (Local Development)
- Python 3.11+
- Redis 7.0+ (local or remote)
- Git
- Docker (optional, for containerized deployment)

### API Keys
1. **MEXC API Key**:
   - Login to MEXC → API Management → Create API
   - Enable **Spot Trading** permission
   - Disable **Withdrawal** permission (security)
   - Save API Key and Secret Key securely

2. **Google Cloud**:
   - Create GCP project
   - Enable billing
   - Enable required APIs (Cloud Run, Cloud Scheduler, Secret Manager)

---

## Local Development

### Step 1: Clone Repository
```bash
git clone https://github.com/7Spade/qrl-api.git
cd qrl-api
```

### Step 2: Create Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy example
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use any editor
```

**Required Environment Variables**:
```bash
# MEXC API Credentials (REQUIRED)
MEXC_API_KEY=your_mexc_api_key_here
MEXC_SECRET_KEY=your_mexc_secret_key_here

# Redis Connection (REQUIRED)
REDIS_URL=redis://localhost:6379/0
# or for Redis Cloud:
# REDIS_URL=redis://:password@redis-xxxxx.redis.cloud:12345/0

# Trading Configuration (OPTIONAL)
TRADING_SYMBOL=QRLUSDT
DRY_RUN=true  # Set to false for real trading
LOG_LEVEL=INFO

# Bot Configuration (OPTIONAL)
MAX_TRADES_PER_DAY=5
MIN_TRADE_INTERVAL=300
USDT_RESERVE_RATIO=0.20
CORE_POSITION_RATIO=0.70
```

### Step 5: Start Redis
```bash
# Option 1: Docker
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Option 2: Local install
redis-server

# Option 3: Use Redis Cloud (configure REDIS_URL in .env)
```

### Step 6: Run Application
```bash
# Development mode (auto-reload)
uvicorn main:app --reload --port 8080

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 1
```

### Step 7: Verify Installation
```bash
# Check health
curl http://localhost:8080/health

# View API docs
open http://localhost:8080/docs

# Test MEXC connection
curl http://localhost:8080/market/price/QRLUSDT
```

---

## Docker Deployment

### Step 1: Build Image
```bash
# Build
docker build -t qrl-trading-api .

# Verify
docker images | grep qrl-trading-api
```

### Step 2: Run Container
```bash
docker run -d \
  -p 8080:8080 \
  -e MEXC_API_KEY=your_api_key \
  -e MEXC_SECRET_KEY=your_secret_key \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  --name qrl-api \
  qrl-trading-api
```

### Step 3: Use Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  qrl-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - MEXC_API_KEY=${MEXC_API_KEY}
      - MEXC_SECRET_KEY=${MEXC_SECRET_KEY}
      - REDIS_URL=redis://redis:6379/0
      - DRY_RUN=true
    depends_on:
      - redis

volumes:
  redis_data:
```

```bash
# Run with compose
docker-compose up -d

# Check logs
docker-compose logs -f qrl-api

# Stop
docker-compose down
```

---

## Google Cloud Run Deployment

### Step 1: Install Google Cloud SDK
```bash
# Install gcloud CLI
# Follow: https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Enable Required APIs
```bash
gcloud services enable \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  redis.googleapis.com
```

### Step 3: Create Secrets
```bash
# Create API key secrets
echo -n "your_mexc_api_key" | \
  gcloud secrets create mexc-api-key --data-file=-

echo -n "your_mexc_secret_key" | \
  gcloud secrets create mexc-secret-key --data-file=-

# Grant Cloud Run access
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')

gcloud secrets add-iam-policy-binding mexc-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding mexc-secret-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 4: Deploy to Cloud Run
```bash
# Using cloudbuild.yaml
gcloud builds submit --config cloudbuild.yaml

# Or manually
gcloud run deploy qrl-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60s \
  --min-instances 0 \
  --max-instances 1 \
  --set-env-vars="TRADING_SYMBOL=QRLUSDT,DRY_RUN=false" \
  --set-secrets="MEXC_API_KEY=mexc-api-key:latest,MEXC_SECRET_KEY=mexc-secret-key:latest" \
  --no-allow-unauthenticated
```

### Step 5: Get Service URL
```bash
SERVICE_URL=$(gcloud run services describe qrl-api \
  --region=us-central1 \
  --format='value(status.url)')

echo "Service URL: $SERVICE_URL"
```

### Step 6: Test Deployment
```bash
# Health check
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  ${SERVICE_URL}/health

# API docs
open ${SERVICE_URL}/docs
```

---

## Cloud Scheduler Setup

### Step 1: Create Service Account
```bash
# Create service account
gcloud iam service-accounts create scheduler-sa \
  --display-name="Cloud Scheduler Service Account"

# Grant Cloud Run Invoker role
gcloud run services add-iam-policy-binding qrl-api \
  --region=us-central1 \
  --member="serviceAccount:scheduler-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### Step 2: Create Scheduler Jobs

**Job 1: Sync Balance (Every 3 minutes)**
```bash
gcloud scheduler jobs create http sync-balance \
  --location=us-central1 \
  --schedule="*/3 * * * *" \
  --uri="${SERVICE_URL}/tasks/sync-balance" \
  --http-method=POST \
  --oidc-service-account-email="scheduler-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --oidc-token-audience="${SERVICE_URL}" \
  --headers="Content-Type=application/json" \
  --message-body='{}'
```

**Job 2: Update Price (Every minute)**
```bash
gcloud scheduler jobs create http update-price \
  --location=us-central1 \
  --schedule="* * * * *" \
  --uri="${SERVICE_URL}/tasks/update-price" \
  --http-method=POST \
  --oidc-service-account-email="scheduler-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --oidc-token-audience="${SERVICE_URL}" \
  --headers="Content-Type=application/json" \
  --message-body='{}'
```

**Job 3: Update Cost (Every 5 minutes)**
```bash
gcloud scheduler jobs create http update-cost \
  --location=us-central1 \
  --schedule="*/5 * * * *" \
  --uri="${SERVICE_URL}/tasks/update-cost" \
  --http-method=POST \
  --oidc-service-account-email="scheduler-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --oidc-token-audience="${SERVICE_URL}" \
  --headers="Content-Type=application/json" \
  --message-body='{}'
```

### Step 3: Test Scheduler
```bash
# Manually trigger job
gcloud scheduler jobs run sync-balance --location=us-central1

# Check execution logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=20 --format=json
```

---

## Redis Setup

### Option 1: Local Redis
```bash
# Docker
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Set REDIS_URL
REDIS_URL=redis://localhost:6379/0
```

### Option 2: Redis Cloud
```bash
# 1. Sign up at https://redis.com/cloud
# 2. Create free database (30MB)
# 3. Get connection string

# Set REDIS_URL
REDIS_URL=redis://:password@redis-xxxxx.redis.cloud:12345/0
```

### Option 3: Google Memorystore (Production)
```bash
# Create Redis instance
gcloud redis instances create qrl-redis \
  --size=1 \
  --region=us-central1 \
  --zone=us-central1-a \
  --redis-version=redis_7_0 \
  --tier=basic \
  --enable-auth

# Get connection info
gcloud redis instances describe qrl-redis \
  --region=us-central1

# For Cloud Run, use VPC connector
gcloud compute networks vpc-access connectors create redis-connector \
  --region=us-central1 \
  --network=default \
  --range=10.8.0.0/28

# Update Cloud Run with VPC connector
gcloud run services update qrl-api \
  --vpc-connector=redis-connector \
  --vpc-egress=private-ranges-only \
  --region=us-central1
```

---

## Monitoring & Verification

### Health Checks
```bash
# Service health
curl ${SERVICE_URL}/health

# Bot status
curl ${SERVICE_URL}/status

# Market price
curl ${SERVICE_URL}/market/price/QRLUSDT
```

### Redis Verification
```bash
# Connect to Redis
redis-cli -h <redis_host> -p <redis_port> -a <password>

# Check price data (should have no expiration)
TTL bot:QRLUSDT:price:latest  # Should return -1

# View position data
HGETALL bot:QRLUSDT:position

# Check raw MEXC responses
GET mexc:raw:account_info:latest
GET mexc:raw:ticker_24hr:latest
```

### Cloud Logging
```bash
# Recent logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=50 \
  --format=json

# Error logs
gcloud logging read "severity>=ERROR" \
  --limit=20

# Specific task logs
gcloud logging read "jsonPayload.message=~'Cloud Task'" \
  --limit=20

# Authentication logs
gcloud logging read "jsonPayload.message=~'authenticated via'" \
  --limit=10
```

### Monitoring Dashboard
```bash
# Open Cloud Console
open https://console.cloud.google.com/run/detail/us-central1/qrl-api/metrics

# Key metrics to watch:
# - Request count
# - Request latency
# - Error rate
# - Instance count
# - Memory usage
```

---

## Troubleshooting

### Common Issues

**1. MEXC API Authentication Failed**
```bash
# Check API key in secrets
gcloud secrets versions access latest --secret=mexc-api-key

# Verify API permissions in MEXC console
# Ensure "Spot Trading" is enabled
```

**2. Redis Connection Failed**
```bash
# Test Redis connection
redis-cli -h <host> -p <port> -a <password> PING

# Check REDIS_URL format
echo $REDIS_URL
```

**3. Cloud Scheduler 401 Unauthorized**
```bash
# Verify service account has Cloud Run Invoker role
gcloud run services get-iam-policy qrl-api --region=us-central1

# Check OIDC token audience matches service URL
```

**4. Data Not Persisting**
```bash
# Check Redis TTL
redis-cli TTL bot:QRLUSDT:price:latest  # Should be -1

# Verify Cloud Scheduler is running
gcloud scheduler jobs list --location=us-central1
```

---

## Cost Estimation (Monthly)

### Google Cloud Run
- **Requests**: 43,200/month (1 req/min) → **$0** (under free tier)
- **CPU Time**: 240 vCPU-hours → **~$21**
- **Memory**: 432 GB-seconds → **~$1**

### Google Memorystore Redis
- **Basic 1GB**: **~$35/month**

### Cloud Scheduler
- **3 jobs**: **$0** (under free tier)

**Total**: **~$57/month** (with managed Redis)

**Savings**:
- Use Redis Cloud free tier: **~$22/month**
- Use lower frequency (5 min): **~$40/month**

---

## Security Best Practices

### API Keys
- ✅ Store in Secret Manager, never in code
- ✅ Enable only required permissions (Spot trading only)
- ✅ Disable withdrawal permissions
- ✅ Rotate keys every 30-90 days
- ✅ Use IP whitelist when possible

### Cloud Resources
- ✅ Use service accounts with minimal permissions
- ✅ Enable OIDC authentication for Cloud Scheduler
- ✅ Use VPC connectors for Redis connections
- ✅ Enable Cloud Armor for DDoS protection (if needed)
- ✅ Set up Cloud Monitoring alerts

### Redis
- ✅ Enable authentication
- ✅ Use TLS for connections (production)
- ✅ Regular backups (if using Memorystore)
- ✅ Limit access to VPC only

---

## Next Steps

After deployment:
1. ✅ Monitor logs for first 24 hours
2. ✅ Verify Cloud Scheduler executions
3. ✅ Check Redis data persistence
4. ✅ Set up alerts for failures
5. ✅ Test manual trading execution (DRY_RUN=true first)
6. ✅ Review and optimize costs
7. ✅ Document any custom configurations

---

## Support

For issues or questions:
- Check logs: `gcloud logging read` commands above
- Review documentation: `/docs` directory
- Test locally first: `uvicorn main:app --reload`
- Validate fixes: Run test scripts in repository

---

**Deployment complete!** Monitor the system and adjust configurations as needed.

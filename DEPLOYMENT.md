# QRL Trading API - Complete Deployment Guide

This guide walks you through deploying the QRL Trading API to Google Cloud Platform using Cloud Build, Artifact Registry, and Cloud Run.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Manual Deployment](#manual-deployment)
- [Pipeline Architecture](#pipeline-architecture)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## 🌟 Overview

The deployment pipeline follows this workflow:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│ Dockerfile  │ ──> │ Cloud Build  │ ──> │ Artifact        │ ──> │ Cloud Run    │
│             │     │ - Validate   │     │ Registry        │     │ - Deploy     │
│             │     │ - Build      │     │ - Store image   │     │ - Serve      │
│             │     │ - Test       │     │                 │     │              │
└─────────────┘     └──────────────┘     └─────────────────┘     └──────────────┘
```

### Key Features

- ✅ **Automated CI/CD**: One command deployment
- ✅ **Multi-stage validation**: Dockerfile validation, linting, testing
- ✅ **Image optimization**: Multi-tag support (latest + git commit)
- ✅ **Zero-downtime deployment**: Traffic management and health checks
- ✅ **Secret management**: Secure credential storage
- ✅ **Auto-scaling**: 0-10 instances based on traffic

## 🔧 Prerequisites

### Required Tools

1. **Google Cloud SDK (gcloud)**
   ```bash
   # Install gcloud CLI
   # macOS
   brew install google-cloud-sdk
   
   # Linux
   curl https://sdk.cloud.google.com | bash
   
   # Windows
   # Download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Docker** (optional, for local testing)
   ```bash
   # macOS
   brew install docker
   
   # Linux
   sudo apt-get install docker.io
   
   # Windows
   # Download from: https://www.docker.com/products/docker-desktop
   ```

### Google Cloud Project Setup

1. **Create or select a project**
   ```bash
   # List existing projects
   gcloud projects list
   
   # Create new project
   gcloud projects create qrl-api --name="QRL Trading API"
   
   # Set as default
   gcloud config set project qrl-api
   ```

2. **Enable billing**
   - Visit: https://console.cloud.google.com/billing
   - Link your project to a billing account

3. **Authenticate**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

### MEXC API Credentials

1. Log in to [MEXC](https://www.mexc.com)
2. Navigate to API Management
3. Create a new API key with **Spot Trading** permission only
4. Save your API Key and Secret Key securely

### Redis Setup

**Option 1: Redis Cloud (Recommended for production)**
- Sign up at [Redis Cloud](https://redis.com/try-free/)
- Create a free database
- Copy the connection URL

**Option 2: Google Cloud Memorystore**
```bash
gcloud redis instances create qrl-redis \
    --size=1 \
    --region=asia-southeast1 \
    --tier=basic
```

**Option 3: Local Redis (Development only)**
```bash
docker run -d -p 6379:6379 redis:7-alpine
# Connection URL: redis://localhost:6379/0
```

## 🚀 Quick Start

### One-Command Deployment

```bash
# 1. Clone the repository
git clone https://github.com/7Spade/qrl-api.git
cd qrl-api

# 2. Complete first-time setup (see Manual Deployment section below)

# 3. Deploy with Cloud Build
gcloud builds submit --config=cloudbuild.yaml .
```

The Cloud Build pipeline will:
- Validate Dockerfile and Python code
- Build Docker image
- Test the image
- Push to Artifact Registry
- Deploy to Cloud Run
- Verify deployment
- Optionally deploy Cloud Scheduler jobs

## 📖 Manual Deployment

If you prefer manual control, follow these steps:

### Step 1: Enable Required APIs

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    cloudscheduler.googleapis.com
```

### Step 2: Create Artifact Registry Repository

```bash
gcloud artifacts repositories create qrl-trading-api \
    --repository-format=docker \
    --location=asia-southeast1 \
    --description="Docker repository for QRL Trading API"
```

### Step 3: Create Secrets in Secret Manager

```bash
# Create secrets
echo -n "your_mexc_api_key" | gcloud secrets create mexc-api-key --data-file=-
echo -n "your_mexc_secret_key" | gcloud secrets create mexc-secret-key --data-file=-
echo -n "redis://your-redis-url:6379/0" | gcloud secrets create redis-url --data-file=-

# Get project number
PROJECT_NUMBER=$(gcloud projects describe qrl-api --format='value(projectNumber)')

# Grant access to Cloud Run service account
for secret in mexc-api-key mexc-secret-key redis-url; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
done
```

### Step 4: Run Cloud Build

```bash
gcloud builds submit --config=cloudbuild.yaml .
```

### Step 5: Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe qrl-trading-api \
    --region=asia-southeast1 \
    --format='value(status.url)')

echo "Service URL: $SERVICE_URL"

# Test health endpoint
curl "$SERVICE_URL/health"

# Test status endpoint
curl "$SERVICE_URL/status"

# View API documentation
open "$SERVICE_URL/docs"
```

### Step 6: Deploy Cloud Scheduler Jobs (Optional)

```bash
gcloud builds submit --config=cloudbuild-scheduler.yaml .
```

## 🏗️ Pipeline Architecture

### Cloud Build Steps

The `cloudbuild.yaml` defines the following steps:

1. **Pre-Build Validation**
   - Validate Dockerfile syntax
   - Lint Python code
   - Check for syntax errors

2. **Build Stage**
   - Build Docker image with labels
   - Tag with `latest` and git commit SHA
   - Optimize layers for caching

3. **Test Stage**
   - Verify image was built correctly
   - Check image size
   - Validate health check configuration

4. **Push Stage**
   - Push to Artifact Registry with multiple tags
   - `latest`: Always points to newest build
   - `${SHORT_SHA}`: Specific git commit

5. **Deploy Stage**
   - Deploy to Cloud Run
   - Configure resources (512Mi RAM, 1 CPU)
   - Set environment variables from Secret Manager
   - Configure auto-scaling (0-10 instances)

6. **Post-Deploy Validation**
   - Verify deployment success
   - Test health endpoint
   - Update traffic to new revision

### Substitution Variables

You can customize the build with substitutions:

```bash
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_SERVICE_NAME=my-api,_REGION=us-central1 \
    .
```

Available substitutions:
- `_SERVICE_NAME`: Cloud Run service name (default: qrl-trading-api)
- `_REGION`: Deployment region (default: asia-southeast1)
- `_REPOSITORY`: Artifact Registry repository (default: qrl-trading-api)
- `_IMAGE_NAME`: Image name (default: qrl-trading-api)
- `_IMAGE_TAG`: Image tag (default: latest)

## ⚙️ Configuration

### Environment Variables

The following environment variables are automatically set from Secret Manager:

| Variable | Source | Description |
|----------|--------|-------------|
| `MEXC_API_KEY` | mexc-api-key secret | MEXC API authentication key |
| `MEXC_SECRET_KEY` | mexc-secret-key secret | MEXC API secret for signing |
| `REDIS_URL` | redis-url secret | Redis connection string |
| `ENV` | Set in cloudbuild.yaml | Environment (production) |
| `LOG_LEVEL` | Set in cloudbuild.yaml | Logging level (INFO) |
| `LOG_FORMAT` | Set in cloudbuild.yaml | Log format (json) |

### Resource Limits

Default Cloud Run configuration:

```yaml
Memory: 512Mi
CPU: 1
Min Instances: 0 (scales to zero)
Max Instances: 10
Concurrency: 80 requests per instance
Timeout: 300s (5 minutes)
```

To modify, edit the `cloudbuild.yaml` deployment step.

## ✅ Verification

### Health Check

```bash
SERVICE_URL=$(gcloud run services describe qrl-trading-api \
    --region=asia-southeast1 \
    --format='value(status.url)')

curl "$SERVICE_URL/health"
# Expected: {"status":"healthy","redis":"connected","mexc":"connected"}
```

### API Status

```bash
curl "$SERVICE_URL/status" | jq
# Expected: Bot status, position, latest price
```

### View Logs

```bash
# Real-time logs
gcloud run services logs tail qrl-trading-api --region=asia-southeast1

# Recent logs
gcloud run services logs read qrl-trading-api --region=asia-southeast1 --limit=50
```

### Monitor Metrics

Visit Cloud Console:
```
https://console.cloud.google.com/run/detail/asia-southeast1/qrl-trading-api/metrics
```

## 🔍 Troubleshooting

### Build Fails

**Problem**: Cloud Build fails with permission errors

```bash
# Grant Cloud Build service account necessary permissions
PROJECT_NUMBER=$(gcloud projects describe qrl-api --format='value(projectNumber)')

gcloud projects add-iam-policy-binding qrl-api \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud iam service-accounts add-iam-policy-binding \
    ${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"
```

### Deployment Succeeds but Service Crashes

**Problem**: Service deploys but immediately crashes

```bash
# Check logs for errors
gcloud run services logs read qrl-trading-api --region=asia-southeast1 --limit=100

# Common issues:
# 1. Redis connection failed - verify REDIS_URL secret
# 2. MEXC API credentials invalid - verify API key secrets
# 3. Missing dependencies - check requirements.txt
```

### Secret Access Denied

**Problem**: Service can't access secrets

```bash
# Verify IAM permissions
for secret in mexc-api-key mexc-secret-key redis-url; do
    echo "Checking $secret..."
    gcloud secrets get-iam-policy $secret
done

# Re-grant if needed
PROJECT_NUMBER=$(gcloud projects describe qrl-api --format='value(projectNumber)')
for secret in mexc-api-key mexc-secret-key redis-url; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
done
```

### Build is Slow

**Problem**: Build takes too long

```bash
# Check build history
gcloud builds list --limit=10

# Optimize:
# 1. Check .gcloudignore excludes unnecessary files
# 2. Use higher machine type (already configured: N1_HIGHCPU_8)
# 3. Review Dockerfile layer caching
```

### Can't Access Service URL

**Problem**: Service URL returns 403 or 404

```bash
# Check service is deployed and healthy
gcloud run services describe qrl-trading-api --region=asia-southeast1

# Verify traffic routing
gcloud run services update-traffic qrl-trading-api \
    --region=asia-southeast1 \
    --to-latest

# Check IAM allow unauthenticated (if public)
gcloud run services add-iam-policy-binding qrl-trading-api \
    --region=asia-southeast1 \
    --member="allUsers" \
    --role="roles/run.invoker"
```

## 📚 Additional Resources

- [Google Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [MEXC API Documentation](https://mexcdevelop.github.io/apidocs/spot_v3_en/)

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Cloud Run logs: `gcloud run services logs read qrl-trading-api`
3. Check Cloud Build history: `gcloud builds list`
4. Open an issue on [GitHub](https://github.com/7Spade/qrl-api/issues)

## 🔐 Security Best Practices

- ✅ Never commit secrets to git
- ✅ Use Secret Manager for all credentials
- ✅ Rotate API keys regularly
- ✅ Set IP restrictions on MEXC API keys
- ✅ Limit API permissions (Spot Trading only)
- ✅ Monitor logs for suspicious activity
- ✅ Use private Artifact Registry repositories
- ✅ Implement authentication for Cloud Scheduler jobs

## 📝 License

MIT License - see LICENSE file for details

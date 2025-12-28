# 🚀 Quick Deployment Guide

> **TL;DR**: Deploy QRL Trading API to Google Cloud with direct gcloud commands

## Prerequisites

- Google Cloud account with billing enabled
- MEXC API credentials (API Key + Secret)
- Redis instance (local, Redis Cloud, or Memorystore)
- gcloud CLI installed and authenticated

## One-Command Deployment

```bash
gcloud builds submit --config=cloudbuild.yaml .
```

**That's it!** The Cloud Build pipeline will:
- Validate Dockerfile and Python code
- Build Docker image
- Test the image
- Push to Artifact Registry
- Deploy to Cloud Run
- Verify deployment

## First-Time Setup

Before your first deployment, complete these one-time setup steps:

### 1. Enable Required APIs

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com
```

### 2. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create qrl-trading-api \
    --repository-format=docker \
    --location=asia-southeast1 \
    --description="Docker repository for QRL Trading API"
```

### 3. Create Secret Manager Secrets

```bash
# Create secrets (replace with your actual values)
echo -n "your_mexc_api_key" | gcloud secrets create mexc-api-key --data-file=-
echo -n "your_mexc_secret_key" | gcloud secrets create mexc-secret-key --data-file=-
echo -n "redis://your-redis-host:6379/0" | gcloud secrets create redis-url --data-file=-
```

### 4. Grant Secret Access to Cloud Run

```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')

# Grant access to each secret
for secret in mexc-api-key mexc-secret-key redis-url; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
done
```

### 5. Grant Cloud Build Permissions (if needed)

```bash
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')

# Grant Cloud Build permission to deploy to Cloud Run
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"

# Grant Cloud Build permission to act as Cloud Run service account
gcloud iam service-accounts add-iam-policy-binding \
    ${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"
```

## Deploy

After completing the one-time setup, deploy with:

```bash
gcloud builds submit --config=cloudbuild.yaml .
```

## Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe qrl-trading-api \
    --region=asia-southeast1 \
    --format='value(status.url)')

echo "Service URL: $SERVICE_URL"

# Test health endpoint
curl "$SERVICE_URL/health"

# View API documentation
open "$SERVICE_URL/docs"
```

## What Gets Deployed

### Cloud Run Service
- **Name**: qrl-trading-api
- **Region**: asia-southeast1
- **Memory**: 512Mi
- **CPU**: 1
- **Auto-scaling**: 0-10 instances
- **Timeout**: 300s

### Container Image
- **Registry**: asia-southeast1-docker.pkg.dev
- **Tags**: 
  - `latest` (always newest)
  - `{git-sha}` (specific version)

### Environment Variables
- `MEXC_API_KEY` (from Secret Manager)
- `MEXC_SECRET_KEY` (from Secret Manager)
- `REDIS_URL` (from Secret Manager)
- `ENV=production`
- `LOG_LEVEL=INFO`
- `LOG_FORMAT=json`

## Cost Estimation

**Free Tier (within limits):**
- Cloud Run: 2M requests/month, 360K GB-seconds/month
- Cloud Build: 120 build-minutes/day
- Artifact Registry: 0.5 GB storage
- Secret Manager: 6 secrets, 10K access operations/month

**Estimated Monthly Cost (beyond free tier):**
- ~$0-5 for typical usage
- Redis Cloud Free: $0
- Cloud Scheduler: ~$0.10/job/month

## Common Issues

### Build Fails with Permission Error

```bash
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"
```

### Service Crashes on Start

```bash
# Check logs
gcloud run services logs read qrl-trading-api --region=asia-southeast1

# Common causes:
# - Invalid Redis URL
# - Invalid MEXC credentials
# - Missing dependencies
```

### Can't Access Service

```bash
# Make service public
gcloud run services add-iam-policy-binding qrl-trading-api \
    --region=asia-southeast1 \
    --member="allUsers" \
    --role="roles/run.invoker"
```

## Next Steps

1. **View API Documentation**: `{SERVICE_URL}/docs`
2. **Monitor Logs**: `gcloud run services logs tail qrl-trading-api`
3. **Deploy Scheduler**: `gcloud builds submit --config=cloudbuild-scheduler.yaml .`
4. **Setup Monitoring**: Cloud Console → Cloud Run → Metrics

## Additional Resources

- Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- API documentation: [README.md](README.md)
- Troubleshooting: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Support

- GitHub Issues: https://github.com/7Spade/qrl-api/issues
- MEXC API Docs: https://mexcdevelop.github.io/apidocs/spot_v3_en/
- Cloud Run Docs: https://cloud.google.com/run/docs

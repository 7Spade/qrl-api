#!/bin/bash

# Cloud Scheduler Setup Script for QRL Trading API
# This script creates 3 Cloud Scheduler jobs to trigger scheduled tasks

# Configuration
PROJECT_ID="your-project-id"  # Replace with your GCP project ID
REGION="asia-southeast1"
SERVICE_URL="https://qrl-trading-api-545492969490.asia-southeast1.run.app"
SERVICE_ACCOUNT="cloud-scheduler@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🚀 Setting up Cloud Scheduler for QRL Trading API"
echo "=================================================="
echo "Service URL: $SERVICE_URL"
echo "Region: $REGION"
echo ""

# Enable Cloud Scheduler API
echo "📋 Step 1: Enabling Cloud Scheduler API..."
gcloud services enable cloudscheduler.googleapis.com --project=$PROJECT_ID

# Create App Engine app (required for Cloud Scheduler)
echo "📋 Step 2: Creating App Engine app (if not exists)..."
gcloud app create --region=$REGION --project=$PROJECT_ID 2>/dev/null || echo "App Engine app already exists"

echo ""
echo "📋 Step 3: Creating Cloud Scheduler Jobs..."
echo ""

# Job 1: Balance Sync (every minute)
echo "🔄 Creating Job 1: sync-balance-job (every 1 minute)"
gcloud scheduler jobs create http sync-balance-job \
    --location=$REGION \
    --schedule="* * * * *" \
    --uri="${SERVICE_URL}/tasks/sync-balance" \
    --http-method=POST \
    --headers="X-CloudScheduler=true" \
    --oidc-service-account-email=$SERVICE_ACCOUNT \
    --time-zone="Asia/Taipei" \
    --description="Sync MEXC account balance to Redis every minute" \
    --project=$PROJECT_ID \
    || echo "Job already exists, updating..."

# If job exists, update it
gcloud scheduler jobs update http sync-balance-job \
    --location=$REGION \
    --schedule="* * * * *" \
    --uri="${SERVICE_URL}/tasks/sync-balance" \
    --http-method=POST \
    --headers="X-CloudScheduler=true" \
    --time-zone="Asia/Taipei" \
    --project=$PROJECT_ID \
    2>/dev/null

echo "✅ sync-balance-job created/updated"
echo ""

# Job 2: Price Update (every minute)
echo "💰 Creating Job 2: update-price-job (every 1 minute)"
gcloud scheduler jobs create http update-price-job \
    --location=$REGION \
    --schedule="* * * * *" \
    --uri="${SERVICE_URL}/tasks/update-price" \
    --http-method=POST \
    --headers="X-CloudScheduler=true" \
    --oidc-service-account-email=$SERVICE_ACCOUNT \
    --time-zone="Asia/Taipei" \
    --description="Update QRL/USDT price every minute" \
    --project=$PROJECT_ID \
    || echo "Job already exists, updating..."

gcloud scheduler jobs update http update-price-job \
    --location=$REGION \
    --schedule="* * * * *" \
    --uri="${SERVICE_URL}/tasks/update-price" \
    --http-method=POST \
    --headers="X-CloudScheduler=true" \
    --time-zone="Asia/Taipei" \
    --project=$PROJECT_ID \
    2>/dev/null

echo "✅ update-price-job created/updated"
echo ""

# Job 3: Cost Update (every 5 minutes)
echo "📊 Creating Job 3: update-cost-job (every 5 minutes)"
gcloud scheduler jobs create http update-cost-job \
    --location=$REGION \
    --schedule="*/5 * * * *" \
    --uri="${SERVICE_URL}/tasks/update-cost" \
    --http-method=POST \
    --headers="X-CloudScheduler=true" \
    --oidc-service-account-email=$SERVICE_ACCOUNT \
    --time-zone="Asia/Taipei" \
    --description="Update cost and PnL data every 5 minutes" \
    --project=$PROJECT_ID \
    || echo "Job already exists, updating..."

gcloud scheduler jobs update http update-cost-job \
    --location=$REGION \
    --schedule="*/5 * * * *" \
    --uri="${SERVICE_URL}/tasks/update-cost" \
    --http-method=POST \
    --headers="X-CloudScheduler=true" \
    --time-zone="Asia/Taipei" \
    --project=$PROJECT_ID \
    2>/dev/null

echo "✅ update-cost-job created/updated"
echo ""

# List all jobs
echo "📋 All Cloud Scheduler Jobs:"
gcloud scheduler jobs list --location=$REGION --project=$PROJECT_ID

echo ""
echo "=================================================="
echo "✅ Cloud Scheduler setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Verify jobs in Cloud Console: https://console.cloud.google.com/cloudscheduler"
echo "2. Test jobs manually:"
echo "   gcloud scheduler jobs run sync-balance-job --location=$REGION"
echo "   gcloud scheduler jobs run update-price-job --location=$REGION"
echo "   gcloud scheduler jobs run update-cost-job --location=$REGION"
echo "3. Monitor logs:"
echo "   gcloud logging read 'resource.type=cloud_scheduler_job' --limit=50"
echo ""
echo "💰 Cost estimate: ~\$0.20/month (first 3 jobs are free)"
echo "=================================================="

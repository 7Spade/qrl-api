#!/bin/bash
# deploy.sh - Complete deployment script for QRL Trading API
# This script handles the entire deployment pipeline to Google Cloud

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-qrl-api}"
REGION="${GCP_REGION:-asia-southeast1}"
SERVICE_NAME="${SERVICE_NAME:-qrl-trading-api}"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check gcloud CLI
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "gcloud CLI installed"
    
    # Check docker (optional)
    if command -v docker &> /dev/null; then
        print_success "Docker installed"
    else
        print_warning "Docker not found (optional for local testing)"
    fi
    
    # Check authentication
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
        print_success "Authenticated as: $ACCOUNT"
    else
        print_error "Not authenticated. Run: gcloud auth login"
        exit 1
    fi
    
    # Check project
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$CURRENT_PROJECT" ]; then
        print_warning "No project set. Setting to: $PROJECT_ID"
        gcloud config set project "$PROJECT_ID"
    else
        print_info "Current project: $CURRENT_PROJECT"
        if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
            read -p "Switch to project $PROJECT_ID? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                gcloud config set project "$PROJECT_ID"
            fi
        fi
    fi
}

enable_apis() {
    print_header "Enabling Required APIs"
    
    APIS=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "artifactregistry.googleapis.com"
        "secretmanager.googleapis.com"
        "cloudscheduler.googleapis.com"
    )
    
    for api in "${APIS[@]}"; do
        echo "Enabling $api..."
        gcloud services enable "$api" --quiet
    done
    
    print_success "All required APIs enabled"
}

setup_artifact_registry() {
    print_header "Setting Up Artifact Registry"
    
    # Check if repository exists
    if gcloud artifacts repositories describe qrl-trading-api \
        --location="$REGION" &> /dev/null; then
        print_success "Artifact Registry repository already exists"
    else
        print_info "Creating Artifact Registry repository..."
        gcloud artifacts repositories create qrl-trading-api \
            --repository-format=docker \
            --location="$REGION" \
            --description="Docker repository for QRL Trading API"
        print_success "Artifact Registry repository created"
    fi
}

setup_secrets() {
    print_header "Checking Secret Manager Secrets"
    
    REQUIRED_SECRETS=("mexc-api-key" "mexc-secret-key" "redis-url")
    MISSING_SECRETS=()
    
    for secret in "${REQUIRED_SECRETS[@]}"; do
        if gcloud secrets describe "$secret" &> /dev/null; then
            print_success "Secret '$secret' exists"
        else
            print_warning "Secret '$secret' does not exist"
            MISSING_SECRETS+=("$secret")
        fi
    done
    
    if [ ${#MISSING_SECRETS[@]} -gt 0 ]; then
        print_warning "Missing secrets: ${MISSING_SECRETS[*]}"
        print_info "Please create them manually or run setup-secrets.sh"
        read -p "Continue without creating secrets? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "All required secrets exist"
    fi
}

run_cloud_build() {
    print_header "Running Cloud Build"
    
    print_info "Starting build process..."
    print_info "This will:"
    print_info "  1. Validate Dockerfile and Python code"
    print_info "  2. Build Docker image"
    print_info "  3. Test the image"
    print_info "  4. Push to Artifact Registry"
    print_info "  5. Deploy to Cloud Run"
    print_info "  6. Verify deployment"
    
    # Submit build
    gcloud builds submit \
        --config=cloudbuild.yaml \
        --substitutions=_SERVICE_NAME="$SERVICE_NAME",_REGION="$REGION" \
        .
    
    if [ $? -eq 0 ]; then
        print_success "Cloud Build completed successfully!"
    else
        print_error "Cloud Build failed"
        exit 1
    fi
}

get_service_url() {
    print_header "Getting Service Information"
    
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format='value(status.url)' 2>/dev/null)
    
    if [ -n "$SERVICE_URL" ]; then
        print_success "Service URL: $SERVICE_URL"
        echo ""
        print_info "Available endpoints:"
        echo "  📊 API Documentation: $SERVICE_URL/docs"
        echo "  🏥 Health Check: $SERVICE_URL/health"
        echo "  📈 Status: $SERVICE_URL/status"
        echo ""
        
        # Try to hit health endpoint
        print_info "Testing health endpoint..."
        if curl -sf "$SERVICE_URL/health" > /dev/null; then
            print_success "Service is healthy!"
        else
            print_warning "Health check failed - service may still be starting"
        fi
    else
        print_warning "Could not get service URL"
    fi
}

deploy_scheduler_jobs() {
    print_header "Deploying Cloud Scheduler Jobs"
    
    read -p "Deploy Cloud Scheduler jobs? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deploying scheduler jobs..."
        gcloud builds submit \
            --config=cloudbuild-scheduler.yaml \
            .
        
        if [ $? -eq 0 ]; then
            print_success "Scheduler jobs deployed successfully!"
        else
            print_warning "Scheduler deployment had issues"
        fi
    else
        print_info "Skipping scheduler deployment"
    fi
}

# Main execution
main() {
    clear
    print_header "QRL Trading API - Cloud Deployment Script"
    echo ""
    print_info "Project: $PROJECT_ID"
    print_info "Region: $REGION"
    print_info "Service: $SERVICE_NAME"
    echo ""
    
    read -p "Continue with deployment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
    
    check_prerequisites
    enable_apis
    setup_artifact_registry
    setup_secrets
    run_cloud_build
    get_service_url
    deploy_scheduler_jobs
    
    echo ""
    print_header "Deployment Complete! 🎉"
    print_success "QRL Trading API has been deployed successfully"
    echo ""
    print_info "Next steps:"
    echo "  1. Visit the API documentation at: $SERVICE_URL/docs"
    echo "  2. Check the logs: gcloud run services logs read $SERVICE_NAME --region=$REGION"
    echo "  3. Monitor in Cloud Console: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME"
}

# Run main function
main "$@"

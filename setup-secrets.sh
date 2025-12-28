#!/bin/bash
# setup-secrets.sh - Helper script to create Secret Manager secrets
# This script helps you securely store API keys and credentials in Google Cloud Secret Manager

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="${GCP_PROJECT_ID:-qrl-api}"

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

create_secret() {
    local secret_name=$1
    local secret_description=$2
    local prompt_message=$3
    
    echo ""
    print_header "Creating Secret: $secret_name"
    
    # Check if secret already exists
    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &> /dev/null; then
        print_info "Secret '$secret_name' already exists"
        read -p "Do you want to update it? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Skipping $secret_name"
            return
        fi
        UPDATE=true
    else
        UPDATE=false
    fi
    
    # Get secret value
    read -sp "$prompt_message: " secret_value
    echo
    
    if [ -z "$secret_value" ]; then
        print_error "Secret value cannot be empty. Skipping."
        return
    fi
    
    # Create or update secret
    if [ "$UPDATE" = true ]; then
        echo -n "$secret_value" | gcloud secrets versions add "$secret_name" \
            --project="$PROJECT_ID" \
            --data-file=-
        print_success "Secret '$secret_name' updated"
    else
        echo -n "$secret_value" | gcloud secrets create "$secret_name" \
            --project="$PROJECT_ID" \
            --replication-policy="automatic" \
            --data-file=-
        print_success "Secret '$secret_name' created"
    fi
    
    # Grant access to Cloud Run service account
    PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
    SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
    
    gcloud secrets add-iam-policy-binding "$secret_name" \
        --project="$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor" \
        --quiet
    
    print_success "Access granted to Cloud Run service account"
}

load_from_env() {
    local env_file=".env"
    
    if [ ! -f "$env_file" ]; then
        print_info "No .env file found. Will prompt for values."
        return
    fi
    
    print_info "Found .env file. Attempting to load values..."
    
    # Load MEXC_API_KEY
    if grep -q "^MEXC_API_KEY=" "$env_file"; then
        MEXC_API_KEY=$(grep "^MEXC_API_KEY=" "$env_file" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
        print_success "Loaded MEXC_API_KEY from .env"
    fi
    
    # Load MEXC_SECRET_KEY
    if grep -q "^MEXC_SECRET_KEY=" "$env_file"; then
        MEXC_SECRET_KEY=$(grep "^MEXC_SECRET_KEY=" "$env_file" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
        print_success "Loaded MEXC_SECRET_KEY from .env"
    fi
    
    # Load REDIS_URL
    if grep -q "^REDIS_URL=" "$env_file"; then
        REDIS_URL=$(grep "^REDIS_URL=" "$env_file" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
        print_success "Loaded REDIS_URL from .env"
    fi
}

create_secret_from_value() {
    local secret_name=$1
    local secret_value=$2
    local description=$3
    
    if [ -z "$secret_value" ]; then
        return
    fi
    
    echo ""
    print_header "Creating Secret: $secret_name"
    
    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &> /dev/null; then
        echo -n "$secret_value" | gcloud secrets versions add "$secret_name" \
            --project="$PROJECT_ID" \
            --data-file=-
        print_success "Secret '$secret_name' updated from .env"
    else
        echo -n "$secret_value" | gcloud secrets create "$secret_name" \
            --project="$PROJECT_ID" \
            --replication-policy="automatic" \
            --data-file=-
        print_success "Secret '$secret_name' created from .env"
    fi
    
    # Grant access
    PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
    SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
    
    gcloud secrets add-iam-policy-binding "$secret_name" \
        --project="$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor" \
        --quiet
}

main() {
    clear
    print_header "QRL Trading API - Secret Manager Setup"
    echo ""
    print_info "Project: $PROJECT_ID"
    echo ""
    
    # Check authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        print_error "Not authenticated. Run: gcloud auth login"
        exit 1
    fi
    
    # Enable Secret Manager API
    print_info "Enabling Secret Manager API..."
    gcloud services enable secretmanager.googleapis.com --project="$PROJECT_ID" --quiet
    
    # Try to load from .env
    load_from_env
    
    # Create secrets
    if [ -n "$MEXC_API_KEY" ]; then
        create_secret_from_value "mexc-api-key" "$MEXC_API_KEY" "MEXC API Key"
    else
        create_secret "mexc-api-key" "MEXC API Key" "Enter your MEXC API Key"
    fi
    
    if [ -n "$MEXC_SECRET_KEY" ]; then
        create_secret_from_value "mexc-secret-key" "$MEXC_SECRET_KEY" "MEXC Secret Key"
    else
        create_secret "mexc-secret-key" "MEXC Secret Key" "Enter your MEXC Secret Key"
    fi
    
    if [ -n "$REDIS_URL" ]; then
        create_secret_from_value "redis-url" "$REDIS_URL" "Redis connection URL"
    else
        create_secret "redis-url" "Redis connection URL" "Enter your Redis URL (e.g., redis://user:pass@host:6379/0)"
    fi
    
    echo ""
    print_header "Setup Complete! 🎉"
    print_success "All secrets have been created and configured"
    echo ""
    print_info "You can now run: ./deploy.sh"
}

main "$@"

#!/bin/bash
# DEPLOYMENT_VERIFICATION.sh - Verify all deployment files are in place
# This script checks that all necessary files for the Cloud Build pipeline exist

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

print_header "Cloud Build Pipeline - File Verification"

ERRORS=0

# Check core pipeline files
echo ""
echo "Checking core pipeline files..."

if [ -f "cloudbuild.yaml" ]; then
    print_success "cloudbuild.yaml exists"
    LINES=$(wc -l < cloudbuild.yaml)
    echo "   → $LINES lines"
else
    print_error "cloudbuild.yaml missing"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "Dockerfile" ]; then
    print_success "Dockerfile exists"
else
    print_error "Dockerfile missing"
    ERRORS=$((ERRORS + 1))
fi

if [ -f ".gcloudignore" ]; then
    print_success ".gcloudignore exists"
else
    print_error ".gcloudignore missing"
    ERRORS=$((ERRORS + 1))
fi

# Check automation scripts
echo ""
echo "Checking automation scripts..."

if [ -f "deploy.sh" ] && [ -x "deploy.sh" ]; then
    print_success "deploy.sh exists and is executable"
else
    print_error "deploy.sh missing or not executable"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "setup-secrets.sh" ] && [ -x "setup-secrets.sh" ]; then
    print_success "setup-secrets.sh exists and is executable"
else
    print_error "setup-secrets.sh missing or not executable"
    ERRORS=$((ERRORS + 1))
fi

# Check documentation
echo ""
echo "Checking documentation..."

if [ -f "DEPLOYMENT.md" ]; then
    print_success "DEPLOYMENT.md exists"
    SIZE=$(du -h DEPLOYMENT.md | cut -f1)
    echo "   → $SIZE"
else
    print_error "DEPLOYMENT.md missing"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "QUICK_DEPLOY.md" ]; then
    print_success "QUICK_DEPLOY.md exists"
else
    print_error "QUICK_DEPLOY.md missing"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "docs/CLOUD_BUILD_GUIDE.md" ]; then
    print_success "docs/CLOUD_BUILD_GUIDE.md exists"
else
    print_error "docs/CLOUD_BUILD_GUIDE.md missing"
    ERRORS=$((ERRORS + 1))
fi

# Check scheduler files
echo ""
echo "Checking Cloud Scheduler files..."

if [ -f "cloudbuild-scheduler.yaml" ]; then
    print_success "cloudbuild-scheduler.yaml exists"
else
    print_error "cloudbuild-scheduler.yaml missing"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "scheduler-config.yaml" ]; then
    print_success "scheduler-config.yaml exists"
else
    print_error "scheduler-config.yaml missing"
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo ""
print_header "Verification Summary"

if [ $ERRORS -eq 0 ]; then
    print_success "All deployment files are in place!"
    echo ""
    echo "You can now:"
    echo "  1. Run: ./setup-secrets.sh (one-time setup)"
    echo "  2. Run: ./deploy.sh (deploy to Cloud Run)"
    echo "  3. Or:  gcloud builds submit --config=cloudbuild.yaml ."
    echo ""
    exit 0
else
    print_error "Found $ERRORS missing or incorrect files"
    echo ""
    echo "Please ensure all files are in place before deploying."
    exit 1
fi

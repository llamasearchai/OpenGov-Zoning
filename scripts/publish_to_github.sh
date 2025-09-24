#!/bin/bash

# OpenGov Zoning - GitHub Repository Publishing Script
# This script automates the creation and configuration of the GitHub repository

set -euo pipefail

# Configuration
OWNER="${1:-llamasearchai}"
REPO_NAME="${2:-OpenGov-Zoning}"
VISIBILITY="${3:-public}"
DESCRIPTION="A comprehensive FastAPI-based zoning and land use API for municipal governments"
HOMEPAGE="https://llamasearchai.github.io/OpenGov-Zoning"
TOPICS="api,fastapi,gis,infrastructure,land-use,municipal,permitting,zoning,zoning-api,python,async,sqlalchemy,pydantic,docker,kubernetes,terraform"
BRANCH="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gh CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed. Please install it first:"
        log_error "https://cli.github.com/"
        exit 1
    fi

    if ! gh auth status &> /dev/null; then
        log_error "GitHub CLI is not authenticated. Please run 'gh auth login' first."
        exit 1
    fi
}

# Create GitHub repository
create_repository() {
    log_info "Creating GitHub repository: $OWNER/$REPO_NAME"

    if gh repo view "$OWNER/$REPO_NAME" &> /dev/null; then
        log_warn "Repository $OWNER/$REPO_NAME already exists"
        return 0
    fi

    gh repo create "$OWNER/$REPO_NAME" \
        --$VISIBILITY \
        --description "$DESCRIPTION" \
        --homepage "$HOMEPAGE" \
        --disable-issues=false \
        --disable-wiki=false \
        --enable-projects=true \
        --enable-discussions=true \
        --template=false

    log_info "Repository created successfully"
}

# Set repository topics
set_topics() {
    log_info "Setting repository topics"

    # Convert comma-separated string to array
    IFS=',' read -ra TOPIC_ARRAY <<< "$TOPICS"

    gh repo edit "$OWNER/$REPO_NAME" \
        --add-topic "${TOPIC_ARRAY[@]}"

    log_info "Repository topics set successfully"
}

# Upload social preview image
upload_social_preview() {
    log_info "Uploading social preview image"

    if [ -f "static/branding/og-banner.png" ]; then
        gh api repos/$OWNER/$REPO_NAME/contents/static/branding/og-banner.png \
            -X PUT \
            -H "Accept: application/vnd.github.v3+json" \
            -f message="Add social preview banner" \
            -f content="$(base64 -w 0 static/branding/og-banner.png)"
        log_info "Social preview image uploaded successfully"
    else
        log_warn "Social preview image not found at static/branding/og-banner.png"
    fi
}

# Push code to repository
push_code() {
    log_info "Pushing code to repository"

    # Initialize git if not already done
    if [ ! -d .git ]; then
        git init
        git add .
        git commit -m "Initial commit: Production-ready FastAPI zoning API"
    fi

    # Add remote and push
    git remote add origin "https://github.com/$OWNER/$REPO_NAME.git"
    git branch -M $BRANCH
    git push -u origin $BRANCH

    log_info "Code pushed successfully"
}

# Configure branch protection
configure_branch_protection() {
    log_info "Configuring branch protection rules"

    gh api repos/$OWNER/$REPO_NAME/branches/$BRANCH/protection \
        -X PUT \
        -H "Accept: application/vnd.github.v3+json" \
        -f required_status_checks='{"strict": true, "contexts": ["security", "test", "lint", "performance", "build"]}' \
        -f enforce_admins=true \
        -f required_pull_request_reviews='{"required_approving_review_count": 1}' \
        -f restrictions=null \
        -f required_linear_history=true \
        -f allow_force_pushes=false \
        -f allow_deletions=false \
        -f required_conversation_resolution=true

    log_info "Branch protection configured successfully"
}

# Enable security features
enable_security_features() {
    log_info "Enabling security features"

    # Enable Dependabot alerts and security updates
    gh api repos/$OWNER/$REPO_NAME/vulnerability-alerts \
        -X PUT \
        -H "Accept: application/vnd.github.dorian-preview+json"

    # Enable secret scanning
    gh api repos/$OWNER/$REPO_NAME/private-vulnerability-reporting \
        -X PUT \
        -H "Accept: application/vnd.github.dorian-preview+json"

    log_info "Security features enabled successfully"
}

# Create labels
create_labels() {
    log_info "Creating issue labels"

    # Define labels
    declare -A labels=(
        ["bug"]="d73a49"
        ["enhancement"]="a2eeef"
        ["documentation"]="0075ca"
        ["good first issue"]="7057ff"
        ["help wanted"]="008672"
        ["security"]="d1242f"
        ["performance"]="f85149"
        ["chore"]="6f42c1"
        ["automated"]="0E8A16"
    )

    for label in "${!labels[@]}"; do
        gh label create "$label" \
            --color "${labels[$label]}" \
            --description "Issues related to $label" \
            --force
    done

    log_info "Labels created successfully"
}

# Configure GitHub Pages
configure_pages() {
    log_info "Configuring GitHub Pages"

    gh api repos/$OWNER/$REPO_NAME/pages \
        -X POST \
        -H "Accept: application/vnd.github.v3+json" \
        -f source='{"branch": "main", "path": "/docs"}'

    log_info "GitHub Pages configured successfully"
}

# Create initial release
create_initial_release() {
    log_info "Creating initial release v1.0.0"

    # Generate OpenAPI schema
    python -c "
from src.opengovzoning.web.app import app
import json
with open('static/api/openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)
    "

    # Create release
    gh release create v1.0.0 \
        --title "Release v1.0.0" \
        --notes "Initial production-ready release of OpenGov Zoning API" \
        --generate-notes \
        --latest

    log_info "Initial release created successfully"
}

# Main execution
main() {
    log_info "Starting GitHub repository setup for OpenGov Zoning"

    check_gh_cli
    create_repository
    set_topics
    upload_social_preview
    push_code
    configure_branch_protection
    enable_security_features
    create_labels
    configure_pages
    create_initial_release

    log_info "GitHub repository setup completed successfully!"
    log_info "Repository URL: https://github.com/$OWNER/$REPO_NAME"
    log_info "Documentation URL: https://$OWNER.github.io/$REPO_NAME"
}

# Run main function with all arguments
main "$@"
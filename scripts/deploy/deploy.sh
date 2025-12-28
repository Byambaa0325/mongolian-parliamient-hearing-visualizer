#!/bin/bash
# Deployment script for Transcript Speaker Tagger

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}PROJECT_ID not set. Checking gcloud config...${NC}"
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}Error: PROJECT_ID not set and no default project found.${NC}"
        echo "Please set PROJECT_ID environment variable or run:"
        echo "  gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
fi

echo -e "${GREEN}Using project: $PROJECT_ID${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI not found.${NC}"
    echo "Please install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}Not authenticated. Running gcloud auth login...${NC}"
    gcloud auth login
fi

# Enable required APIs
echo -e "${GREEN}Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID

# Deploy using Cloud Build
echo -e "${GREEN}Starting deployment...${NC}"
echo -e "${YELLOW}This will take approximately 5-10 minutes...${NC}"

gcloud builds submit \
    --config=cloudbuild.yaml \
    --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Deployment successful!${NC}"
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe transcript-tagger \
        --region us-central1 \
        --project $PROJECT_ID \
        --format 'value(status.url)' 2>/dev/null)
    
    if [ ! -z "$SERVICE_URL" ]; then
        echo -e "${GREEN}Your app is available at:${NC}"
        echo -e "${GREEN}$SERVICE_URL${NC}"
    fi
else
    echo -e "${RED}✗ Deployment failed. Check the logs above for details.${NC}"
    exit 1
fi


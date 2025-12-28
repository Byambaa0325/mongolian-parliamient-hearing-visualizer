#!/bin/bash
# Setup script for Cloud SQL PostgreSQL database

set -e

PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
REGION=${REGION:-us-central1}
INSTANCE_NAME=${INSTANCE_NAME:-transcript-db}
DATABASE_NAME=${DATABASE_NAME:-transcripts}
DB_USER=${DB_USER:-transcript_user}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID not set"
    echo "Run: export PROJECT_ID=your-project-id"
    exit 1
fi

echo "Setting up Cloud SQL for project: $PROJECT_ID"

# Create Cloud SQL instance
echo "Creating Cloud SQL instance..."
gcloud sql instances create $INSTANCE_NAME \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=$REGION \
    --project=$PROJECT_ID \
    --root-password=$(openssl rand -base64 32) || {
    echo "Instance may already exist, continuing..."
}

# Create database
echo "Creating database..."
gcloud sql databases create $DATABASE_NAME \
    --instance=$INSTANCE_NAME \
    --project=$PROJECT_ID || {
    echo "Database may already exist, continuing..."
}

# Create user
echo "Creating database user..."
DB_PASSWORD=$(openssl rand -base64 32)
gcloud sql users create $DB_USER \
    --instance=$INSTANCE_NAME \
    --password=$DB_PASSWORD \
    --project=$PROJECT_ID || {
    echo "User may already exist, continuing..."
}

# Get connection name
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --format='value(connectionName)')

echo ""
echo "=========================================="
echo "Cloud SQL Setup Complete!"
echo "=========================================="
echo ""
echo "Connection Name: $CONNECTION_NAME"
echo "Database: $DATABASE_NAME"
echo "User: $DB_USER"
echo "Password: $DB_PASSWORD"
echo ""
echo "Save this password securely!"
echo ""
echo "DATABASE_URL format:"
echo "postgresql://$DB_USER:$DB_PASSWORD@localhost/$DATABASE_NAME?host=/cloudsql/$CONNECTION_NAME"
echo ""
echo "Next steps:"
echo "1. Update Cloud Run service to use Cloud SQL:"
echo "   gcloud run services update transcript-tagger \\"
echo "     --add-cloudsql-instances=$CONNECTION_NAME \\"
echo "     --set-env-vars DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DATABASE_NAME?host=/cloudsql/$CONNECTION_NAME \\"
echo "     --region $REGION \\"
echo "     --project $PROJECT_ID"
echo ""
echo "2. Load transcripts after deployment"
echo ""


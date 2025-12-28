#!/bin/bash
# Script to connect Cloud Run service to existing Cloud SQL database

set -e

PROJECT_ID=${PROJECT_ID:-lazy-jeopardy}
REGION=${REGION:-europe-west1}
SERVICE_NAME=${SERVICE_NAME:-transcript-tagger}
CONNECTION_NAME=${CONNECTION_NAME:-lazy-jeopardy:europe-west1:parliamient-hearing-db}

# Database credentials (you'll need to set these)
DB_USER=${DB_USER:-transcript_user}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_NAME:-transcripts}

if [ -z "$DB_PASSWORD" ]; then
    echo "Error: DB_PASSWORD not set"
    echo "Please set the database password:"
    echo "  export DB_PASSWORD=your-password"
    exit 1
fi

echo "Connecting Cloud Run service to Cloud SQL..."
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Connection: $CONNECTION_NAME"
echo ""

# Build DATABASE_URL for Cloud SQL Unix socket connection
DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}?host=/cloudsql/${CONNECTION_NAME}"

# Update Cloud Run service
echo "Updating Cloud Run service..."
gcloud run services update $SERVICE_NAME \
  --add-cloudsql-instances=$CONNECTION_NAME \
  --set-env-vars DATABASE_URL="$DATABASE_URL" \
  --region $REGION \
  --project $PROJECT_ID

echo ""
echo "✓ Service updated successfully!"
echo ""
echo "Database connection configured:"
echo "  Connection: $CONNECTION_NAME"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""
echo "Next steps:"
echo "1. Verify connection by checking service logs"
echo "2. Load transcripts: python3 -m backend.load_transcripts"
echo ""


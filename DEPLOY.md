# Deployment Guide - Transcript Speaker Tagger

## Quick Deployment to Google Cloud Run

### Prerequisites

1. **Google Cloud SDK installed:**
   ```bash
   # Check if installed
   gcloud --version
   
   # If not installed, download from:
   # https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable required APIs:**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

### Option 1: Deploy with Cloud Build (Recommended)

This is the easiest method - it builds and deploys in one command:

```bash
gcloud builds submit --config=cloudbuild.yaml --project=YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with your Google Cloud project ID.

### Option 2: Manual Docker Build and Deploy

If you prefer more control over the build process:

```bash
# 1. Set your project ID
export PROJECT_ID=YOUR_PROJECT_ID

# 2. Build the Docker image
docker build -t gcr.io/$PROJECT_ID/transcript-tagger:latest .

# 3. Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/transcript-tagger:latest

# 4. Deploy to Cloud Run
gcloud run deploy transcript-tagger \
  --image gcr.io/$PROJECT_ID/transcript-tagger:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --project $PROJECT_ID
```

### Option 3: PowerShell Script (Windows)

For Windows users, here's a PowerShell script:

```powershell
# Set your project ID
$PROJECT_ID = "YOUR_PROJECT_ID"

# Deploy using Cloud Build
gcloud builds submit --config=cloudbuild.yaml --project=$PROJECT_ID
```

## After Deployment

### 1. Set Up Database (Cloud SQL)

**Cloud Run is serverless and stateless** - you need a managed database for persistent storage.

**Quick Setup:**
```bash
# Run setup script
export PROJECT_ID=your-project-id
./setup_cloud_sql.sh

# Or on Windows
$env:PROJECT_ID = "your-project-id"
.\setup_cloud_sql.ps1
```

This creates a Cloud SQL PostgreSQL instance. **Save the password!**

Then connect Cloud Run to Cloud SQL:
```bash
# Get connection name
CONNECTION_NAME=$(gcloud sql instances describe transcript-db --format='value(connectionName)')

# Update Cloud Run service
gcloud run services update transcript-tagger \
  --add-cloudsql-instances=$CONNECTION_NAME \
  --set-env-vars DATABASE_URL="postgresql://user:password@localhost/transcripts?host=/cloudsql/$CONNECTION_NAME" \
  --region us-central1
```

See [DEPLOY_DATABASE.md](DEPLOY_DATABASE.md) for detailed instructions.

### 2. Load Transcripts into Database

After deployment, you need to load the transcript files into the database. You can do this by:

**Option A: One-time Cloud Run Job**
```bash
# Create a job to load transcripts
gcloud run jobs create load-transcripts \
  --image gcr.io/$PROJECT_ID/transcript-tagger \
  --region us-central1 \
  --command python3 \
  --args -m,backend.load_transcripts \
  --set-env-vars DATABASE_URL=$DATABASE_URL

# Execute the job
gcloud run jobs execute load-transcripts --region us-central1
```

**Option B: Manual Load via Cloud SQL**
Connect to your Cloud SQL instance and run the load script.

**Option C: Add Initialization Endpoint**
Modify the API to load transcripts on first request (not recommended for production).

### 3. Get Your Service URL

After deployment completes, you'll see output like:

```
Service URL: https://transcript-tagger-XXXXX-uc.a.run.app
```

Or get it manually:

```bash
gcloud run services describe transcript-tagger \
  --region us-central1 \
  --project YOUR_PROJECT_ID \
  --format 'value(status.url)'
```

### 4. Test the Application

Open the Service URL in your browser. You should see:
- ✅ Transcript selection interface loads
- ✅ Can select from loaded transcripts
- ✅ Tagging interface works
- ✅ Tags save to database
- ✅ Export functionality works

## Configuration

### Change Region

Edit `cloudbuild.yaml` and change:
```yaml
- '--region'
- 'us-central1'  # Change to your preferred region
```

Common regions:
- `us-central1` (Iowa)
- `us-east1` (South Carolina)
- `europe-west1` (Belgium)
- `asia-northeast1` (Tokyo)

### Adjust Resources

Edit `cloudbuild.yaml` to change memory/CPU:

```yaml
- '--memory'
- '512Mi'  # Increase if needed (e.g., '1Gi', '2Gi')
- '--cpu'
- '1'  # Increase if needed (e.g., '2', '4')
```

### Database Configuration

For production, set up Cloud SQL PostgreSQL:

```bash
# Create Cloud SQL instance
gcloud sql instances create transcript-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create transcripts --instance=transcript-db

# Update Cloud Run service with database connection
gcloud run services update transcript-tagger \
  --set-env-vars DATABASE_URL=postgresql://user:password@/transcripts?host=/cloudsql/PROJECT_ID:REGION:transcript-db \
  --add-cloudsql-instances=PROJECT_ID:REGION:transcript-db \
  --region us-central1
```

### Custom Service Name

Edit `cloudbuild.yaml` and change:
```yaml
- 'deploy'
- 'transcript-tagger'  # Change to your preferred name
```

## Monitoring

### View Logs

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=transcript-tagger" \
  --project YOUR_PROJECT_ID \
  --limit 50
```

### View Service Details

```bash
gcloud run services describe transcript-tagger \
  --region us-central1 \
  --project YOUR_PROJECT_ID
```

### View Build History

```bash
gcloud builds list --project YOUR_PROJECT_ID --limit 10
```

## Troubleshooting

### Build Fails

1. **Check build logs:**
   ```bash
   gcloud builds list --project YOUR_PROJECT_ID --limit 5
   gcloud builds log BUILD_ID --project YOUR_PROJECT_ID
   ```

2. **Common issues:**
   - Node.js version mismatch → Check `package.json` Node version
   - Out of memory → Increase Cloud Build machine type in `cloudbuild.yaml`
   - Timeout → Increase timeout in `cloudbuild.yaml`

### Deployment Succeeds but App Doesn't Load

1. **Check Cloud Run logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision" \
     --project YOUR_PROJECT_ID \
     --limit 20
   ```

2. **Verify static files:**
   - Check that `build/` directory exists in Docker image
   - Verify `server.py` is serving from correct directory

3. **Test locally:**
   ```bash
   # Build locally
   docker build -t transcript-tagger .
   
   # Run locally
   docker run -p 8080:8080 transcript-tagger
   
   # Test
   curl http://localhost:8080
   ```

### Need to Roll Back

```bash
# List revisions
gcloud run revisions list \
  --service=transcript-tagger \
  --region us-central1 \
  --project YOUR_PROJECT_ID

# Roll back to previous revision
gcloud run services update-traffic transcript-tagger \
  --region us-central1 \
  --project YOUR_PROJECT_ID \
  --to-revisions=PREVIOUS_REVISION=100
```

## Cost Estimation

For a lightweight React app:
- **Memory:** 512MB (minimal)
- **CPU:** 1 vCPU
- **Traffic:** Pay per request
- **Estimated cost:** ~$0.10-0.50/month for low traffic

## Quick Commands Reference

```bash
# Deploy
gcloud builds submit --config=cloudbuild.yaml --project=YOUR_PROJECT_ID

# Check status
gcloud builds list --project=YOUR_PROJECT_ID --limit=5

# View service
gcloud run services describe transcript-tagger --region us-central1 --project YOUR_PROJECT_ID

# View logs
gcloud logging read "resource.type=cloud_run_revision" --project YOUR_PROJECT_ID --limit=20

# Delete service (if needed)
gcloud run services delete transcript-tagger --region us-central1 --project YOUR_PROJECT_ID
```

---

## Ready to Deploy?

**Run this command:**

```bash
gcloud builds submit --config=cloudbuild.yaml --project=YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with your actual Google Cloud project ID.

The deployment will:
1. Build the React app
2. Create a Docker image
3. Push to Google Container Registry
4. Deploy to Cloud Run
5. Provide you with a public URL

**Expected time:** ~5-10 minutes

---

**Created:** December 2024  
**Status:** Ready to deploy ✅


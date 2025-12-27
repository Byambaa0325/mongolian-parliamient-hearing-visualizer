# PowerShell deployment script for Transcript Speaker Tagger

$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Check if PROJECT_ID is set
if (-not $env:PROJECT_ID) {
    Write-ColorOutput Yellow "PROJECT_ID not set. Checking gcloud config..."
    $env:PROJECT_ID = gcloud config get-value project 2>$null
    
    if (-not $env:PROJECT_ID) {
        Write-ColorOutput Red "Error: PROJECT_ID not set and no default project found."
        Write-Output "Please set PROJECT_ID environment variable or run:"
        Write-Output "  gcloud config set project YOUR_PROJECT_ID"
        exit 1
    }
}

Write-ColorOutput Green "Using project: $env:PROJECT_ID"

# Check if gcloud is installed
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-ColorOutput Red "Error: gcloud CLI not found."
    Write-Output "Please install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Check if user is authenticated
$activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $activeAccount) {
    Write-ColorOutput Yellow "Not authenticated. Running gcloud auth login..."
    gcloud auth login
}

# Enable required APIs
Write-ColorOutput Green "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com --project=$env:PROJECT_ID
gcloud services enable run.googleapis.com --project=$env:PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$env:PROJECT_ID

# Deploy using Cloud Build
Write-ColorOutput Green "Starting deployment..."
Write-ColorOutput Yellow "This will take approximately 5-10 minutes..."

gcloud builds submit `
    --config=cloudbuild.yaml `
    --project=$env:PROJECT_ID

if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput Green "✓ Deployment successful!"
    
    # Get service URL
    $serviceUrl = gcloud run services describe transcript-tagger `
        --region us-central1 `
        --project $env:PROJECT_ID `
        --format 'value(status.url)' 2>$null
    
    if ($serviceUrl) {
        Write-ColorOutput Green "Your app is available at:"
        Write-ColorOutput Green $serviceUrl
    }
} else {
    Write-ColorOutput Red "✗ Deployment failed. Check the logs above for details."
    exit 1
}


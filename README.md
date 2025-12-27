<<<<<<< HEAD
# Transcript Speaker Tagger

A React web application with database backend for tagging speakers in transcripts and creating a tagged dataset.

## Features

- **Database Storage**: Transcripts and tags stored in database (SQLite/PostgreSQL)
- **Transcript Selection**: Select from pre-loaded transcripts (12.7.txt, 12.8.txt, 12.10.txt, 12.12.txt)
- **Interactive Tagging**: Click lines to select and assign speakers
- **Bulk Tagging**: Select multiple lines (Shift+Click, Ctrl/Cmd+Click) and tag at once
- **Speaker Management**: Add, remove, and manage speaker names
- **Search**: Search through transcript content
- **Pagination**: Efficiently handle large transcripts with pagination
- **Tagged View**: View tagged transcript with filtering and grouping options
- **Statistics**: See speaker statistics and line counts with progress tracking
- **Export**: Export tagged transcripts in multiple formats:
  - Plain Text (.txt)
  - JSON (.json)
  - SRT Subtitles (.srt)
  - CSV (.csv)

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Setup

### 1. Configure Environment Variables (Optional)

For local development, you can use a `.env` file:

```bash
# Copy example file
cp .env.example .env

# Edit .env if needed (defaults work for SQLite)
```

See [README_ENV.md](README_ENV.md) for detailed environment variable documentation.

### 2. Load Transcripts into Database

Before using the app, load the transcript files:

```bash
# Linux/Mac
python3 -m backend.load_transcripts

# Windows PowerShell
python -m backend.load_transcripts
```

This will load:
- `12.7.txt` (December 7, 2024)
- `12.8.txt` (December 8, 2024)
- `12.10.txt` (December 10, 2024)
- `12.12.txt` (December 12, 2024)

### 3. Start the Application

```bash
npm start
```

## Usage

### Selecting a Transcript

1. Go to the "Select Transcript" tab
2. Choose one of the loaded transcripts
3. View progress and statistics for each transcript

### Tagging Speakers

1. Navigate to the "Tagging" tab
2. Click on lines to select them
   - Single click: Select one line
   - Shift+Click: Select range of lines
   - Ctrl/Cmd+Click: Select multiple individual lines
3. Click a speaker button to assign that speaker to selected lines
4. Add new speakers using the "Add new speaker" input
5. Use the search box to find specific content

### Viewing Tagged Data

1. Go to the "Tagged View" tab
2. Filter by speaker using the dropdown
3. Toggle "Group by speaker" to see all lines from each speaker together
4. View speaker statistics at the top

### Exporting

1. In the "Tagged View" tab, scroll to the export panel
2. Select export format (TXT, JSON, SRT, or CSV)
3. Click "Export" to download the file

## Keyboard Shortcuts

- **Click**: Select single line
- **Shift + Click**: Select range of lines
- **Ctrl/Cmd + Click**: Multi-select individual lines

## Project Structure

```
src/
  ├── App.js                 # Main application component
  ├── App.css                # Main app styles
  ├── components/
  │   ├── FileUpload.js      # File upload component
  │   ├── TranscriptViewer.js # Main tagging interface
  │   ├── TaggedView.js      # View tagged transcript
  │   └── ExportPanel.js     # Export functionality
  └── index.js               # Entry point
```

## Technologies

- React 18
- CSS3 (no external UI libraries)
- File API for file handling
- Blob API for file downloads

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Deployment to Google Cloud Run

This app can be deployed to Google Cloud Run using the same architecture as the reference app.

### Quick Deploy

1. **Set your project ID:**
   ```bash
   export PROJECT_ID=your-project-id
   # Or on Windows PowerShell:
   $env:PROJECT_ID = "your-project-id"
   ```

2. **Deploy using Cloud Build:**
   ```bash
   # Linux/Mac
   ./deploy.sh
   
   # Windows PowerShell
   .\deploy.ps1
   
   # Or manually
   gcloud builds submit --config=cloudbuild.yaml --project=YOUR_PROJECT_ID
   ```

3. **Get your service URL:**
   ```bash
   gcloud run services describe transcript-tagger \
     --region us-central1 \
     --project YOUR_PROJECT_ID \
     --format 'value(status.url)'
   ```

### Deployment Files

- `Dockerfile` - Multi-stage build (Node.js for build, Python for serving)
- `cloudbuild.yaml` - Cloud Build configuration
- `server.py` - Flask server to serve React static files
- `requirements.txt` - Python dependencies
- `deploy.sh` / `deploy.ps1` - Deployment scripts

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions.

## Database

The app uses a database to store transcripts and tags:

- **Local Development**: SQLite (default) - stored in `transcripts.db` file
- **Production (Cloud Run)**: Cloud SQL PostgreSQL - managed database service

**Important:** Cloud Run is serverless/stateless, so you **must** use Cloud SQL for persistent storage in production.

See:
- [README_DATABASE.md](README_DATABASE.md) - Database schema and local setup
- [DEPLOY_DATABASE.md](DEPLOY_DATABASE.md) - Cloud SQL setup for Cloud Run

## Notes

- Transcripts are stored in the database, not in browser
- Tags are saved immediately to the database
- Large transcripts are handled with pagination
- For production deployment, use PostgreSQL on Cloud SQL

## License

MIT

=======
# mongolian-parliamient-hearing-visualizer
>>>>>>> origin/main

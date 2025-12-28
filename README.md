# Transcript Speaker Tagger

A React web application with database backend for tagging speakers in transcripts and creating a tagged dataset.

## Quick Links

**Getting Started:**
- 📖 [Quick Start Guide](docs/QUICK_START.md) - Get up and running in 5 minutes
- 🚀 [Getting Started](docs/GETTING_STARTED.md) - Comprehensive first-time setup
- 🔌 [Quick Connect](docs/QUICK_CONNECT.md) - Fast database connection

**Documentation:**
- 📚 [Documentation Index](docs/INDEX.md) - Complete documentation index
- 💻 [Local Development](docs/LOCAL_DEVELOPMENT.md) - Development setup and workflow
- ☁️ [Cloud Deployment](docs/DEPLOY.md) - Deploy to Google Cloud Run
- 🔧 [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

**Agent Tools:**
- 🤖 [Agent Tools](agent/README.md) - ML/automation scripts for speaker tagging
- 🎯 [Speaker Tagging ML](docs/SPEAKER_TAGGING_ML.md) - Automated speaker detection
- 📊 [Speaker Patterns](docs/SPEAKER_PATTERNS.md) - Mongolian speaker patterns reference

**Scripts:**
- ⚙️ [Scripts](scripts/README.md) - Development, deployment, and database scripts

## Features

- **Database Storage**: SQLite (local) or PostgreSQL (cloud) for persistent data
- **Interactive Tagging UI**: Click-based line selection with keyboard shortcuts
- **Bulk Operations**: Multi-select with Shift+Click and Ctrl/Cmd+Click
- **ML/NLP Speaker Detection**: Automated speaker identification for Mongolian transcripts
- **Search & Filter**: Find content and filter by speaker
- **Progress Tracking**: Visual statistics and completion metrics
- **Export Formats**: TXT, JSON, SRT, CSV

## Quick Start

### 1. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install
```

### 2. Load Transcripts

```bash
# Load transcript files into database
python -m backend.load_transcripts
```

### 3. Start Application

```bash
# Windows
scripts\dev\start_dev.bat

# Linux/Mac
./scripts/dev/start_dev.sh
```

The app will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080

📖 See [Quick Start Guide](docs/QUICK_START.md) for detailed instructions.

## Usage

### Web Interface

1. **Select Transcript** - Choose from pre-loaded transcripts
2. **Tag Speakers** - Click lines to select, then assign speakers
3. **View Results** - Review tagged data with filters and grouping
4. **Export** - Download in your preferred format

**Keyboard Shortcuts:**
- Click: Select single line
- Shift + Click: Select range
- Ctrl/Cmd + Click: Multi-select

📖 See [Local Development](docs/LOCAL_DEVELOPMENT.md) for detailed usage instructions.

## Automated Speaker Tagging

Use ML tools to automatically tag speakers in Mongolian transcripts:

### Interactive Notebook (Best for exploration)

```bash
jupyter notebook agent/speaker_tagging_ml.ipynb
```

### Command-Line (Best for automation)

```bash
# Tag a single file
python agent/tag_speakers_ml.py 12.7.txt

# With options
python agent/tag_speakers_ml.py 12.7.txt \
    --output tagged.txt \
    --export-json \
    --export-csv
```

**Features:**
- Multi-pattern detection for Mongolian text
- Context-aware speaker assignment
- Confidence scoring (0.5-0.9)
- Quality metrics and recommendations

📖 See [Agent Tools](agent/README.md) for all available tools and [Speaker Tagging ML](docs/SPEAKER_TAGGING_ML.md) for detailed documentation.

## Project Structure

```
ot-transcripts/
├── agent/                 # Automation and ML tools
│   ├── tag_speakers_ml.py        # ML-based speaker tagger
│   ├── speaker_tagging_ml.ipynb  # Interactive notebook
│   ├── tag_speakers.py           # Pattern-based tagger
│   └── check_db.py               # Database tools
├── backend/               # Flask API and database
│   ├── api.py                    # REST API endpoints
│   ├── database.py               # SQLAlchemy models
│   └── load_transcripts.py      # Data loading
├── docs/                  # Documentation
│   ├── INDEX.md                  # Documentation index
│   ├── QUICK_START.md            # Quick start guide
│   ├── SPEAKER_TAGGING_ML.md     # ML tagging docs
│   └── ...                       # More docs
├── scripts/               # Operational scripts
│   ├── dev/                      # Development scripts
│   ├── deploy/                   # Deployment scripts
│   └── database/                 # Database scripts
├── src/                   # React frontend
│   ├── App.js                    # Main component
│   └── components/               # UI components
├── server.py              # Flask server entry point
└── requirements.txt       # Python dependencies
```

## Technologies

**Frontend:**
- React 18
- CSS3 (no external UI libraries)
- Modern browser APIs

**Backend:**
- Flask (Python web framework)
- SQLAlchemy (ORM)
- SQLite/PostgreSQL

**ML/NLP:**
- pandas, numpy, scikit-learn
- Custom pattern detection for Mongolian text

## Cloud Deployment

Deploy to Google Cloud Run with Cloud SQL:

```bash
# Set project ID
export PROJECT_ID=your-project-id

# Deploy
./scripts/deploy/deploy.sh
```

The app includes:
- Multi-stage Docker build
- Cloud Build configuration
- Cloud SQL integration
- Automatic HTTPS

📖 See [Deployment Guide](docs/DEPLOY.md) for complete instructions.

## Database

**Local:** SQLite (default) - `transcripts.db`  
**Cloud:** PostgreSQL on Cloud SQL

📖 See [Database Setup](docs/README_DATABASE.md) and [Cloud SQL Setup](docs/DEPLOY_DATABASE.md).

## License

MIT

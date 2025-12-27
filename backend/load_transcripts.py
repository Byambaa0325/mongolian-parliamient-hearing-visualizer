"""
Script to load transcript files into the database
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from backend.database import db, Transcript, TranscriptLine

# Transcript files to load
TRANSCRIPT_FILES = [
    ('12.7.txt', datetime(2024, 12, 7)),
    ('12.8.txt', datetime(2024, 12, 8)),
    ('12.10.txt', datetime(2024, 12, 10)),
    ('12.12.txt', datetime(2024, 12, 12)),
]


def load_transcripts():
    """Load all transcript files into database"""
    app = Flask(__name__)
    
    # Configure database
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///transcripts.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Get project root directory
        project_root = Path(__file__).parent.parent
        
        for filename, date in TRANSCRIPT_FILES:
            filepath = project_root / filename
            
            if not filepath.exists():
                print(f"Warning: {filename} not found, skipping...")
                continue
            
            # Check if transcript already exists
            existing = Transcript.query.filter_by(filename=filename).first()
            if existing:
                print(f"Transcript {filename} already exists, skipping...")
                continue
            
            print(f"Loading {filename}...")
            
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into lines
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Create transcript record
            transcript = Transcript(
                filename=filename,
                date=date,
                total_lines=len(lines)
            )
            db.session.add(transcript)
            db.session.flush()  # Get transcript.id
            
            # Create line records
            for idx, line_text in enumerate(lines, start=1):
                transcript_line = TranscriptLine(
                    transcript_id=transcript.id,
                    line_number=idx,
                    text=line_text
                )
                db.session.add(transcript_line)
            
            print(f"  Loaded {len(lines)} lines")
        
        # Commit all changes
        db.session.commit()
        print("\nAll transcripts loaded successfully!")
        
        # Print summary
        transcripts = Transcript.query.all()
        print(f"\nTotal transcripts: {len(transcripts)}")
        for t in transcripts:
            print(f"  - {t.filename}: {t.total_lines} lines")


if __name__ == '__main__':
    load_transcripts()


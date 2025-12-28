#!/usr/bin/env python3
"""
Quick script to set up local database and load transcripts
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from backend.database import db, Transcript, TranscriptLine
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    """Initialize database and load transcripts"""
    app = Flask(__name__)
    
    # Configure database
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///transcripts.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("[OK] Database tables created")
        
        # Check if transcripts already exist
        existing_count = Transcript.query.count()
        if existing_count > 0:
            print(f"\n[OK] Database already has {existing_count} transcript(s)")
            print("Skipping transcript loading. Use backend.load_transcripts to reload.")
            return
        
        # Load transcripts
        print("\nLoading transcripts...")
        from backend.load_transcripts import load_transcripts
        load_transcripts()
        print("\n[OK] Setup complete!")

if __name__ == '__main__':
    try:
        setup_database()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


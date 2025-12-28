#!/usr/bin/env python3
"""Quick script to check database status"""
import os
import sys
from flask import Flask
from backend.database import db, Transcript
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///transcripts.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    try:
        # Try to query
        count = Transcript.query.count()
        print(f"[OK] Database connected successfully")
        print(f"[OK] Found {count} transcript(s) in database")
        
        if count > 0:
            transcripts = Transcript.query.all()
            for t in transcripts:
                print(f"  - {t.filename}: {t.total_lines} lines")
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


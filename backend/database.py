"""
Database models and setup for transcript tagging
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Transcript(db.Model):
    """Transcript file model"""
    __tablename__ = 'transcripts'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    date = db.Column(db.Date, nullable=True)
    total_lines = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to lines
    lines = db.relationship('TranscriptLine', backref='transcript', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'date': self.date.isoformat() if self.date else None,
            'total_lines': self.total_lines,
            'tagged_lines': len([l for l in self.lines if l.speaker]),
            'created_at': self.created_at.isoformat()
        }


class TranscriptLine(db.Model):
    """Individual line in a transcript"""
    __tablename__ = 'transcript_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    transcript_id = db.Column(db.Integer, db.ForeignKey('transcripts.id'), nullable=False)
    line_number = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    speaker = db.Column(db.String(255), nullable=True)
    tagged_at = db.Column(db.DateTime, nullable=True)
    tagged_by = db.Column(db.String(100), nullable=True)
    
    # Index for faster queries
    __table_args__ = (
        db.Index('idx_transcript_line_number', 'transcript_id', 'line_number'),
        db.Index('idx_transcript_speaker', 'transcript_id', 'speaker'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'transcript_id': self.transcript_id,
            'line_number': self.line_number,
            'text': self.text,
            'speaker': self.speaker,
            'tagged_at': self.tagged_at.isoformat() if self.tagged_at else None,
            'tagged_by': self.tagged_by
        }


class Speaker(db.Model):
    """Speaker names for reference"""
    __tablename__ = 'speakers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("Database initialized")


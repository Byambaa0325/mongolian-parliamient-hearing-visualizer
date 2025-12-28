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
        """Convert transcript to dictionary"""
        try:
            # Count tagged lines safely - use relationship if available, otherwise query directly
            tagged_count = 0
            try:
                # Try using the relationship first (faster if already loaded)
                tagged_count = len([l for l in self.lines if l.speaker])
            except Exception:
                # If relationship fails, use direct query
                # TranscriptLine is defined later in this file, so we can reference it
                tagged_count = db.session.query(TranscriptLine).filter(
                    TranscriptLine.transcript_id == self.id,
                    TranscriptLine.speaker.isnot(None)
                ).count()
            
            return {
                'id': self.id,
                'filename': self.filename,
                'date': self.date.isoformat() if self.date else None,
                'total_lines': self.total_lines or 0,
                'tagged_lines': tagged_count,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
        except Exception as e:
            # Fallback to basic info if anything fails
            import traceback
            print(f"Error in to_dict for transcript {self.id}: {e}")
            print(traceback.format_exc())
            return {
                'id': self.id,
                'filename': self.filename,
                'date': self.date.isoformat() if self.date else None,
                'total_lines': self.total_lines or 0,
                'tagged_lines': 0,
                'created_at': self.created_at.isoformat() if self.created_at else None
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


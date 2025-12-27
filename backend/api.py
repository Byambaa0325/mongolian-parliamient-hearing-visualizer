"""
Flask API for Transcript Speaker Tagger
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from backend.database import db, Transcript, TranscriptLine, Speaker
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

app = Flask(__name__, static_folder='../build', static_url_path='')

# Configure database
# For Cloud Run: Use Cloud SQL PostgreSQL
# For local dev: Use SQLite
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    # Default to SQLite for local development
    database_url = 'sqlite:///transcripts.db'
elif database_url.startswith('postgres://'):
    # Fix postgres:// to postgresql:// for SQLAlchemy
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app)

# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()


# API Routes

@app.route('/api/transcripts', methods=['GET'])
def get_transcripts():
    """Get list of all transcripts"""
    transcripts = Transcript.query.order_by(Transcript.date.desc()).all()
    return jsonify([t.to_dict() for t in transcripts])


@app.route('/api/transcripts/<int:transcript_id>', methods=['GET'])
def get_transcript(transcript_id):
    """Get transcript details"""
    transcript = Transcript.query.get_or_404(transcript_id)
    return jsonify(transcript.to_dict())


@app.route('/api/transcripts/<int:transcript_id>/lines', methods=['GET'])
def get_transcript_lines(transcript_id):
    """Get lines for a transcript with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    search = request.args.get('search', '').strip()
    
    query = TranscriptLine.query.filter_by(transcript_id=transcript_id)
    
    # Search filter
    if search:
        query = query.filter(TranscriptLine.text.ilike(f'%{search}%'))
    
    # Pagination
    pagination = query.order_by(TranscriptLine.line_number).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'lines': [line.to_dict() for line in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@app.route('/api/transcripts/<int:transcript_id>/lines/<int:line_id>', methods=['PATCH'])
def update_line(transcript_id, line_id):
    """Update speaker tag for a line"""
    line = TranscriptLine.query.get_or_404(line_id)
    
    if line.transcript_id != transcript_id:
        return jsonify({'error': 'Line does not belong to transcript'}), 400
    
    data = request.get_json()
    speaker = data.get('speaker', '').strip()
    
    if speaker:
        line.speaker = speaker
        line.tagged_at = datetime.utcnow()
        line.tagged_by = data.get('tagged_by', 'web_user')
    else:
        line.speaker = None
        line.tagged_at = None
        line.tagged_by = None
    
    db.session.commit()
    return jsonify(line.to_dict())


@app.route('/api/transcripts/<int:transcript_id>/lines/bulk', methods=['PATCH'])
def bulk_update_lines(transcript_id):
    """Bulk update speaker tags for multiple lines"""
    data = request.get_json()
    line_ids = data.get('line_ids', [])
    speaker = data.get('speaker', '').strip()
    tagged_by = data.get('tagged_by', 'web_user')
    
    if not line_ids:
        return jsonify({'error': 'No line IDs provided'}), 400
    
    # Verify all lines belong to the transcript
    lines = TranscriptLine.query.filter(
        TranscriptLine.id.in_(line_ids),
        TranscriptLine.transcript_id == transcript_id
    ).all()
    
    if len(lines) != len(line_ids):
        return jsonify({'error': 'Some lines not found or belong to different transcript'}), 400
    
    # Update lines
    now = datetime.utcnow()
    for line in lines:
        if speaker:
            line.speaker = speaker
            line.tagged_at = now
            line.tagged_by = tagged_by
        else:
            line.speaker = None
            line.tagged_at = None
            line.tagged_by = None
    
    db.session.commit()
    return jsonify({
        'updated': len(lines),
        'lines': [line.to_dict() for line in lines]
    })


@app.route('/api/transcripts/<int:transcript_id>/speakers', methods=['GET'])
def get_speakers(transcript_id):
    """Get list of speakers used in a transcript"""
    speakers = db.session.query(
        TranscriptLine.speaker,
        db.func.count(TranscriptLine.id).label('count')
    ).filter(
        TranscriptLine.transcript_id == transcript_id,
        TranscriptLine.speaker.isnot(None)
    ).group_by(TranscriptLine.speaker).all()
    
    return jsonify({
        'speakers': [{'name': s[0], 'count': s[1]} for s in speakers]
    })


@app.route('/api/speakers', methods=['GET'])
def get_all_speakers():
    """Get all unique speakers across all transcripts"""
    speakers = db.session.query(
        TranscriptLine.speaker,
        db.func.count(TranscriptLine.id).label('count')
    ).filter(
        TranscriptLine.speaker.isnot(None)
    ).group_by(TranscriptLine.speaker).all()
    
    return jsonify({
        'speakers': [{'name': s[0], 'count': s[1]} for s in speakers]
    })


@app.route('/api/transcripts/<int:transcript_id>/stats', methods=['GET'])
def get_transcript_stats(transcript_id):
    """Get statistics for a transcript"""
    transcript = Transcript.query.get_or_404(transcript_id)
    
    total_lines = TranscriptLine.query.filter_by(transcript_id=transcript_id).count()
    tagged_lines = TranscriptLine.query.filter_by(
        transcript_id=transcript_id,
        speaker=db.not_(None)
    ).count()
    
    # Speaker statistics
    speaker_stats = db.session.query(
        TranscriptLine.speaker,
        db.func.count(TranscriptLine.id).label('count')
    ).filter(
        TranscriptLine.transcript_id == transcript_id,
        TranscriptLine.speaker.isnot(None)
    ).group_by(TranscriptLine.speaker).all()
    
    return jsonify({
        'total_lines': total_lines,
        'tagged_lines': tagged_lines,
        'untagged_lines': total_lines - tagged_lines,
        'progress': round((tagged_lines / total_lines * 100) if total_lines > 0 else 0, 2),
        'speakers': [{'name': s[0], 'count': s[1]} for s in speaker_stats]
    })


@app.route('/api/transcripts/<int:transcript_id>/export', methods=['GET'])
def export_transcript(transcript_id):
    """Export tagged transcript in various formats"""
    format_type = request.args.get('format', 'txt')
    transcript = Transcript.query.get_or_404(transcript_id)
    
    lines = TranscriptLine.query.filter_by(
        transcript_id=transcript_id
    ).order_by(TranscriptLine.line_number).all()
    
    if format_type == 'txt':
        content = '\n'.join([
            f"[{line.speaker or 'UNKNOWN'}]: {line.text}"
            for line in lines
        ])
        return content, 200, {'Content-Type': 'text/plain'}
    
    elif format_type == 'json':
        return jsonify({
            'transcript': transcript.to_dict(),
            'lines': [line.to_dict() for line in lines]
        })
    
    elif format_type == 'srt':
        content = []
        subtitle_num = 1
        time_offset = 0
        for line in lines:
            start_time = format_time(time_offset)
            time_offset += 5
            end_time = format_time(time_offset)
            content.append(f"{subtitle_num}")
            content.append(f"{start_time} --> {end_time}")
            content.append(f"{line.speaker or 'UNKNOWN'}: {line.text}")
            content.append("")
            subtitle_num += 1
        return '\n'.join(content), 200, {'Content-Type': 'text/plain'}
    
    elif format_type == 'csv':
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Line Number', 'Speaker', 'Text'])
        for line in lines:
            writer.writerow([line.line_number, line.speaker or 'UNKNOWN', line.text])
        return output.getvalue(), 200, {'Content-Type': 'text/csv'}
    
    return jsonify({'error': 'Invalid format'}), 400


def format_time(seconds):
    """Format seconds to SRT time format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},000"


# Serve React app for all routes (SPA routing)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)


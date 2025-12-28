"""
Flask API for Transcript Speaker Tagger
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from backend.database import db, Transcript, TranscriptLine, Speaker
from datetime import datetime
import os
import re
from dotenv import load_dotenv
from collections import defaultdict
from typing import List, Dict

# Load environment variables from .env file (if present)
load_dotenv()

app = Flask(__name__, static_folder='../build', static_url_path='')

# Enable logging
import logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

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
    try:
        db.create_all()
        app.logger.info('Database initialized successfully')
    except Exception as e:
        app.logger.error(f'Error initializing database: {str(e)}', exc_info=True)


# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Backend is running'})

@app.route('/api/transcripts', methods=['GET'])
def get_transcripts():
    """Get list of all transcripts"""
    try:
        app.logger.info('Fetching transcripts...')
        # Use joinedload to eagerly load lines relationship to avoid lazy loading issues
        from sqlalchemy.orm import joinedload
        transcripts = Transcript.query.options(joinedload(Transcript.lines)).order_by(Transcript.date.desc()).all()
        app.logger.info(f'Found {len(transcripts)} transcripts')
        
        result = []
        for t in transcripts:
            try:
                result.append(t.to_dict())
            except Exception as e:
                app.logger.error(f'Error serializing transcript {t.id}: {str(e)}', exc_info=True)
                import traceback
                app.logger.error(traceback.format_exc())
                # Return basic info if to_dict fails
                result.append({
                    'id': t.id,
                    'filename': t.filename,
                    'date': t.date.isoformat() if t.date else None,
                    'total_lines': t.total_lines or 0,
                    'tagged_lines': 0,
                    'created_at': t.created_at.isoformat() if t.created_at else None
                })
        app.logger.info(f'Returning {len(result)} transcripts')
        return jsonify(result)
    except Exception as e:
        app.logger.error(f'Error fetching transcripts: {str(e)}', exc_info=True)
        import traceback
        error_trace = traceback.format_exc()
        app.logger.error(f'Traceback: {error_trace}')
        # Print to console as well for immediate visibility
        print(f"ERROR in get_transcripts: {e}")
        print(error_trace)
        return jsonify({'error': str(e), 'traceback': error_trace}), 500


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


# ML Speaker Detection Helper Class
class SpeakerDetector:
    """Detect speakers using ML patterns for Mongolian text"""
    
    def __init__(self):
        self.titles = [
            'Ерөнхий сайд', 'ерөнхий сайд',
            'УИХ-ын дарга', 'УИХ-ын гишүүн',
            'сайд', 'Сайд',
            'шинжээч', 'Шинжээч',
            'хянан шалгагч', 'Хянан шалгагч',
            'Тэргүүн шадар сайд', 'тэргүүн шадар сайд',
            'дарга', 'Дарга',
            'захирал', 'Захирал',
            'гүйцэтгэх захирал',
            'нарийн бичгийн дарга',
            'гишүүн',
        ]
        
        self.patterns = {
            'intro_za': re.compile(
                r'За\.?\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})\s+(гуай|' + '|'.join(self.titles) + ')',
                re.IGNORECASE
            ),
            'microphone_assignment': re.compile(
                r'\d+\s+номерын\s+микрофон(?:\s+.*?)?\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})',
                re.IGNORECASE
            ),
            'number_name': re.compile(
                r'(?:за|За)?\s*(\d+)\s+номер(?:ын)?\s+(?:микрофон\s+)?([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)',
                re.IGNORECASE
            ),
            'title_asan': re.compile(
                r'([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})\s+(' + '|'.join(self.titles) + r')\s+асан',
                re.IGNORECASE
            ),
        }
        
        self.microphone_speakers = {}
    
    def detect_in_text(self, text: str) -> List[Dict]:
        """Detect speakers in text"""
        detected = []
        
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                if pattern_name == 'microphone_assignment':
                    name = match.group(1).strip()
                    title = ''
                    mic_match = re.search(r'(\d+)\s+номерын\s+микрофон', text[:match.start() + 30])
                    if mic_match:
                        mic_num = mic_match.group(1)
                        self.microphone_speakers[mic_num] = name
                
                elif pattern_name == 'number_name':
                    mic_num = match.group(1).strip()
                    name = match.group(2).strip()
                    title = ''
                    self.microphone_speakers[mic_num] = name
                
                else:
                    name = match.group(1).strip()
                    title = match.group(2).strip() if match.lastindex >= 2 else ''
                
                full_name = f"{name} {title}".strip()
                confidence = self._calculate_confidence(pattern_name, match.start(), len(text))
                
                detected.append({
                    'name': full_name,
                    'position': match.start(),
                    'confidence': confidence,
                    'pattern': pattern_name
                })
        
        # Return highest confidence detection
        if detected:
            return sorted(detected, key=lambda x: x['confidence'], reverse=True)
        return []
    
    def _calculate_confidence(self, pattern_name: str, position: int, text_length: int) -> float:
        base_scores = {
            'intro_za': 0.95,
            'microphone_assignment': 0.92,
            'number_name': 0.88,
            'title_asan': 0.90,
        }
        
        score = base_scores.get(pattern_name, 0.5)
        
        # Boost if at start of text
        if position < 50:
            score = min(0.98, score + 0.05)
        
        return score


@app.route('/api/transcripts/<int:transcript_id>/detect-speakers', methods=['POST'])
def detect_speakers_ml(transcript_id):
    """Use ML to detect speakers in transcript lines"""
    try:
        data = request.get_json()
        line_ids = data.get('line_ids', [])
        auto_tag = data.get('auto_tag', False)  # Whether to automatically tag
        
        if not line_ids:
            # If no line IDs provided, process all lines
            lines = TranscriptLine.query.filter_by(transcript_id=transcript_id).order_by(TranscriptLine.line_number).all()
        else:
            lines = TranscriptLine.query.filter(
                TranscriptLine.id.in_(line_ids),
                TranscriptLine.transcript_id == transcript_id
            ).order_by(TranscriptLine.line_number).all()
        
        detector = SpeakerDetector()
        results = []
        updates_made = 0
        
        for line in lines:
            detections = detector.detect_in_text(line.text)
            
            if detections:
                best = detections[0]
                result = {
                    'line_id': line.id,
                    'line_number': line.line_number,
                    'text_preview': line.text[:100],
                    'detected_speaker': best['name'],
                    'confidence': best['confidence'],
                    'pattern': best['pattern'],
                    'all_detections': detections
                }
                
                # Auto-tag if requested and confidence is high
                if auto_tag and best['confidence'] >= 0.7:
                    line.speaker = best['name']
                    line.tagged_at = datetime.utcnow()
                    line.tagged_by = 'ml_auto'
                    updates_made += 1
                    result['tagged'] = True
                else:
                    result['tagged'] = False
                
                results.append(result)
        
        if auto_tag and updates_made > 0:
            db.session.commit()
        
        return jsonify({
            'success': True,
            'results': results,
            'total_detections': len(results),
            'updates_made': updates_made
        })
    
    except Exception as e:
        app.logger.error(f'Error in ML speaker detection: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/transcripts/<int:transcript_id>/lines/<int:line_id>/split', methods=['POST'])
def split_line(transcript_id, line_id):
    """Split a compound line into multiple lines"""
    try:
        line = TranscriptLine.query.get_or_404(line_id)
        
        if line.transcript_id != transcript_id:
            return jsonify({'error': 'Line does not belong to transcript'}), 400
        
        data = request.get_json()
        split_positions = data.get('split_positions', [])  # Array of character positions
        
        if not split_positions:
            return jsonify({'error': 'No split positions provided'}), 400
        
        # Sort positions
        split_positions = sorted([0] + split_positions + [len(line.text)])
        
        # Create segments
        segments = []
        for i in range(len(split_positions) - 1):
            start = split_positions[i]
            end = split_positions[i + 1]
            text = line.text[start:end].strip()
            if text:
                segments.append(text)
        
        if len(segments) <= 1:
            return jsonify({'error': 'Split would not create multiple lines'}), 400
        
        # Get lines after this one
        lines_after = TranscriptLine.query.filter(
            TranscriptLine.transcript_id == transcript_id,
            TranscriptLine.line_number > line.line_number
        ).order_by(TranscriptLine.line_number).all()
        
        # Increment line numbers for lines after
        for later_line in reversed(lines_after):
            later_line.line_number += len(segments) - 1
        
        # Update original line with first segment
        line.text = segments[0]
        
        # Create new lines for remaining segments
        new_lines = []
        for i, segment in enumerate(segments[1:], 1):
            new_line = TranscriptLine(
                transcript_id=transcript_id,
                line_number=line.line_number + i,
                text=segment,
                speaker=line.speaker,  # Inherit speaker from original
                tagged_at=line.tagged_at,
                tagged_by=line.tagged_by
            )
            db.session.add(new_line)
            new_lines.append(new_line)
        
        db.session.commit()
        
        # Return all created lines
        all_lines = [line] + new_lines
        
        return jsonify({
            'success': True,
            'original_line_id': line_id,
            'segments_created': len(segments),
            'lines': [l.to_dict() for l in all_lines]
        })
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error splitting line: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/transcripts/<int:transcript_id>/lines/<int:line_id>/merge', methods=['POST'])
def merge_lines(transcript_id, line_id):
    """Merge a line with the next line"""
    try:
        line = TranscriptLine.query.get_or_404(line_id)
        
        if line.transcript_id != transcript_id:
            return jsonify({'error': 'Line does not belong to transcript'}), 400
        
        # Get next line
        next_line = TranscriptLine.query.filter(
            TranscriptLine.transcript_id == transcript_id,
            TranscriptLine.line_number == line.line_number + 1
        ).first()
        
        if not next_line:
            return jsonify({'error': 'No next line to merge with'}), 400
        
        # Merge text
        line.text = f"{line.text} {next_line.text}"
        
        # Delete next line
        db.session.delete(next_line)
        
        # Decrement line numbers for lines after
        lines_after = TranscriptLine.query.filter(
            TranscriptLine.transcript_id == transcript_id,
            TranscriptLine.line_number > next_line.line_number
        ).all()
        
        for later_line in lines_after:
            later_line.line_number -= 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'merged_line': line.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error merging lines: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500


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


#!/usr/bin/env python3
"""
Database Sync Utility

Syncs data between local SQLite and Cloud SQL PostgreSQL databases.

Usage:
  # Export local SQLite to JSON
  python sync_database.py export --output backup.json

  # Import JSON to Cloud SQL
  python sync_database.py import --input backup.json --target cloud

  # Direct sync: local -> cloud (push your local changes)
  python sync_database.py push

  # Direct sync: cloud -> local (pull cloud changes)
  python sync_database.py pull

  # Compare databases
  python sync_database.py compare
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_db_connection(db_type='local'):
    """Get database connection based on type"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    if db_type == 'local':
        # Local SQLite - check multiple locations
        possible_paths = [
            'instance/transcripts.db',
            'backend/instance/transcripts.db',
            'transcripts.db'
        ]
        db_path = None
        for path in possible_paths:
            if os.path.exists(path) and os.path.getsize(path) > 0:
                db_path = path
                break
        
        if not db_path:
            # Default to instance path
            db_path = 'instance/transcripts.db'
            print(f"[!] No existing local database found, will use: {db_path}")
        
        db_url = f'sqlite:///{db_path}'
    else:
        # Cloud SQL - from environment
        db_url = os.environ.get('CLOUD_DATABASE_URL') or os.environ.get('DATABASE_URL')
        if not db_url:
            raise ValueError(
                "Cloud database URL not found. Set CLOUD_DATABASE_URL or DATABASE_URL.\n"
                "Example: postgresql://user:password@35.205.155.54:5432/transcripts"
            )
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return engine, Session()


def export_to_json(output_file, db_type='local'):
    """Export database to JSON file"""
    from backend.database import Transcript, TranscriptLine, Speaker
    
    print(f"Exporting from {db_type} database...")
    engine, session = get_db_connection(db_type)
    
    # Create tables in memory model
    from backend.database import db
    
    data = {
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'source': db_type,
        'transcripts': [],
        'speakers': []
    }
    
    # Export transcripts with lines
    transcripts = session.query(Transcript).all()
    for t in transcripts:
        transcript_data = {
            'id': t.id,
            'filename': t.filename,
            'date': t.date.isoformat() if t.date else None,
            'total_lines': t.total_lines,
            'created_at': t.created_at.isoformat() if t.created_at else None,
            'lines': []
        }
        
        lines = session.query(TranscriptLine).filter_by(transcript_id=t.id).order_by(TranscriptLine.line_number).all()
        for line in lines:
            transcript_data['lines'].append({
                'id': line.id,
                'line_number': line.line_number,
                'text': line.text,
                'speaker': line.speaker,
                'tagged_at': line.tagged_at.isoformat() if line.tagged_at else None,
                'tagged_by': line.tagged_by
            })
        
        data['transcripts'].append(transcript_data)
    
    # Export speakers
    speakers = session.query(Speaker).all()
    for s in speakers:
        data['speakers'].append({
            'id': s.id,
            'name': s.name,
            'created_at': s.created_at.isoformat() if s.created_at else None
        })
    
    session.close()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Exported {len(data['transcripts'])} transcripts and {len(data['speakers'])} speakers to {output_file}")
    return data


def import_from_json(input_file, db_type='cloud', mode='merge'):
    """
    Import data from JSON to database
    
    Modes:
    - merge: Update existing, add new (default)
    - replace: Clear target database and import fresh
    - tags_only: Only sync speaker tags, don't modify transcripts/lines
    """
    from backend.database import Transcript, TranscriptLine, Speaker
    from sqlalchemy import text
    
    print(f"Importing to {db_type} database (mode: {mode})...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    engine, session = get_db_connection(db_type)
    
    # Create tables if they don't exist
    from backend.database import db
    db.metadata.create_all(engine)
    
    try:
        if mode == 'replace':
            print("[!] Clearing target database...")
            session.query(TranscriptLine).delete()
            session.query(Transcript).delete()
            session.query(Speaker).delete()
            session.commit()
        
        # Import speakers first
        for speaker_data in data.get('speakers', []):
            existing = session.query(Speaker).filter_by(name=speaker_data['name']).first()
            if not existing:
                speaker = Speaker(
                    name=speaker_data['name'],
                    created_at=datetime.fromisoformat(speaker_data['created_at']) if speaker_data.get('created_at') else datetime.utcnow()
                )
                session.add(speaker)
        session.commit()
        
        # Import transcripts
        stats = {'transcripts': 0, 'lines': 0, 'tags_updated': 0}
        
        for t_data in data['transcripts']:
            if mode == 'tags_only':
                # Only update tags for existing transcripts
                transcript = session.query(Transcript).filter_by(filename=t_data['filename']).first()
                if transcript:
                    for line_data in t_data.get('lines', []):
                        line = session.query(TranscriptLine).filter_by(
                            transcript_id=transcript.id,
                            line_number=line_data['line_number']
                        ).first()
                        if line and line_data.get('speaker'):
                            if line.speaker != line_data['speaker']:
                                line.speaker = line_data['speaker']
                                line.tagged_at = datetime.fromisoformat(line_data['tagged_at']) if line_data.get('tagged_at') else datetime.utcnow()
                                line.tagged_by = line_data.get('tagged_by', 'sync')
                                stats['tags_updated'] += 1
            else:
                # Full import
                existing = session.query(Transcript).filter_by(filename=t_data['filename']).first()
                
                if existing:
                    # Update existing transcript
                    transcript = existing
                    if mode == 'merge':
                        # Update lines with tags
                        for line_data in t_data.get('lines', []):
                            line = session.query(TranscriptLine).filter_by(
                                transcript_id=transcript.id,
                                line_number=line_data['line_number']
                            ).first()
                            if line:
                                # Only update if source has tag and target doesn't, or source is newer
                                if line_data.get('speaker') and not line.speaker:
                                    line.speaker = line_data['speaker']
                                    line.tagged_at = datetime.fromisoformat(line_data['tagged_at']) if line_data.get('tagged_at') else None
                                    line.tagged_by = line_data.get('tagged_by')
                                    stats['tags_updated'] += 1
                else:
                    # Create new transcript
                    transcript = Transcript(
                        filename=t_data['filename'],
                        date=datetime.fromisoformat(t_data['date']).date() if t_data.get('date') else None,
                        total_lines=t_data.get('total_lines', 0),
                        created_at=datetime.fromisoformat(t_data['created_at']) if t_data.get('created_at') else datetime.utcnow()
                    )
                    session.add(transcript)
                    session.flush()  # Get the ID
                    
                    # Add lines
                    for line_data in t_data.get('lines', []):
                        line = TranscriptLine(
                            transcript_id=transcript.id,
                            line_number=line_data['line_number'],
                            text=line_data['text'],
                            speaker=line_data.get('speaker'),
                            tagged_at=datetime.fromisoformat(line_data['tagged_at']) if line_data.get('tagged_at') else None,
                            tagged_by=line_data.get('tagged_by')
                        )
                        session.add(line)
                        stats['lines'] += 1
                    
                    stats['transcripts'] += 1
        
        session.commit()
        print(f"[OK] Imported: {stats['transcripts']} new transcripts, {stats['lines']} new lines, {stats['tags_updated']} tags updated")
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR] {e}")
        raise
    finally:
        session.close()


def sync_tags(source='local', target='cloud'):
    """Sync only speaker tags from source to target"""
    print(f"Syncing tags from {source} to {target}...")
    
    # Export from source
    temp_file = f'_sync_temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    export_to_json(temp_file, source)
    
    # Import to target (tags only)
    import_from_json(temp_file, target, mode='tags_only')
    
    # Clean up
    os.remove(temp_file)
    print("[OK] Tag sync complete!")


def compare_databases():
    """Compare local and cloud databases"""
    from backend.database import Transcript, TranscriptLine
    
    print("Comparing databases...")
    
    try:
        _, local_session = get_db_connection('local')
        _, cloud_session = get_db_connection('cloud')
        
        local_transcripts = {t.filename: t for t in local_session.query(Transcript).all()}
        cloud_transcripts = {t.filename: t for t in cloud_session.query(Transcript).all()}
        
        print("\n=== Database Comparison ===")
        print("=" * 50)
        
        # Transcripts
        local_only = set(local_transcripts.keys()) - set(cloud_transcripts.keys())
        cloud_only = set(cloud_transcripts.keys()) - set(local_transcripts.keys())
        common = set(local_transcripts.keys()) & set(cloud_transcripts.keys())
        
        print(f"\nTranscripts:")
        print(f"  Local only: {len(local_only)}")
        print(f"  Cloud only: {len(cloud_only)}")
        print(f"  Both: {len(common)}")
        
        if local_only:
            print(f"\n  [Local only]: {', '.join(sorted(local_only))}")
        if cloud_only:
            print(f"\n  [Cloud only]: {', '.join(sorted(cloud_only))}")
        
        # Compare tags for common transcripts
        print(f"\nTag comparison for common transcripts:")
        for filename in sorted(common):
            local_t = local_transcripts[filename]
            cloud_t = cloud_transcripts[filename]
            
            local_tagged = local_session.query(TranscriptLine).filter(
                TranscriptLine.transcript_id == local_t.id,
                TranscriptLine.speaker.isnot(None)
            ).count()
            
            cloud_tagged = cloud_session.query(TranscriptLine).filter(
                TranscriptLine.transcript_id == cloud_t.id,
                TranscriptLine.speaker.isnot(None)
            ).count()
            
            if local_tagged != cloud_tagged:
                print(f"  {filename}: Local={local_tagged} tagged, Cloud={cloud_tagged} tagged")
        
        local_session.close()
        cloud_session.close()
        
    except Exception as e:
        print(f"[ERROR] Error comparing: {e}")
        print("Make sure CLOUD_DATABASE_URL is set for cloud comparison.")


def main():
    parser = argparse.ArgumentParser(description='Sync database between local and cloud')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export database to JSON')
    export_parser.add_argument('--output', '-o', default='db_backup.json', help='Output file')
    export_parser.add_argument('--source', '-s', choices=['local', 'cloud'], default='local', help='Source database')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import JSON to database')
    import_parser.add_argument('--input', '-i', required=True, help='Input JSON file')
    import_parser.add_argument('--target', '-t', choices=['local', 'cloud'], default='cloud', help='Target database')
    import_parser.add_argument('--mode', '-m', choices=['merge', 'replace', 'tags_only'], default='merge', help='Import mode')
    
    # Push command (local -> cloud)
    push_parser = subparsers.add_parser('push', help='Push local changes to cloud')
    push_parser.add_argument('--mode', '-m', choices=['merge', 'replace', 'tags_only'], default='tags_only', help='Sync mode')
    
    # Pull command (cloud -> local)  
    pull_parser = subparsers.add_parser('pull', help='Pull cloud changes to local')
    pull_parser.add_argument('--mode', '-m', choices=['merge', 'replace', 'tags_only'], default='tags_only', help='Sync mode')
    
    # Compare command
    subparsers.add_parser('compare', help='Compare local and cloud databases')
    
    args = parser.parse_args()
    
    if args.command == 'export':
        export_to_json(args.output, args.source)
    
    elif args.command == 'import':
        import_from_json(args.input, args.target, args.mode)
    
    elif args.command == 'push':
        temp_file = f'_push_temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        export_to_json(temp_file, 'local')
        import_from_json(temp_file, 'cloud', args.mode)
        os.remove(temp_file)
        print("[OK] Push complete!")
    
    elif args.command == 'pull':
        temp_file = f'_pull_temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        export_to_json(temp_file, 'cloud')
        import_from_json(temp_file, 'local', args.mode)
        os.remove(temp_file)
        print("[OK] Pull complete!")
    
    elif args.command == 'compare':
        compare_databases()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()


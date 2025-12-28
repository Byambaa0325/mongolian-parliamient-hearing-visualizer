# Agent Tools

This directory contains automation scripts and ML tools for speaker tagging and database management.

## Speaker Tagging Tools

### ML-Based Speaker Tagging

**[speaker_tagging_ml.ipynb](speaker_tagging_ml.ipynb)** - Interactive Jupyter notebook
- Visual exploration of speaker patterns
- Interactive correction and review
- Real-time metrics and charts
- Best for: Analysis and exploration

**[tag_speakers_ml.py](tag_speakers_ml.py)** - Command-line ML tagger
```bash
# Basic usage
python agent/tag_speakers_ml.py 12.7.txt

# With options
python agent/tag_speakers_ml.py 12.7.txt \
    --output tagged.txt \
    --context-window 25 \
    --export-json \
    --export-csv
```
- Multi-pattern detection for Mongolian text
- Context-aware speaker assignment
- Confidence scoring
- Best for: Automated batch processing

### Pattern-Based Tools

**[tag_speakers.py](tag_speakers.py)** - Simple pattern-based tagger
```bash
python agent/tag_speakers.py 12.7.txt
```
- Basic regex pattern matching
- Quick tagging for standard formats
- Best for: Simple, well-structured transcripts

**[tag_speakers_enhanced.py](tag_speakers_enhanced.py)** - Enhanced pattern tagger
```bash
python agent/tag_speakers_enhanced.py 12.7.txt
```
- Improved pattern detection
- Better error handling
- Best for: Transcripts with more complex patterns

### Example Scripts

**[quick_tag_example.py](quick_tag_example.py)** - Example usage
- Demonstrates basic API usage
- Good starting point for custom scripts

## Database Tools

**[check_db.py](check_db.py)** - Database inspection tool
```bash
python agent/check_db.py
```
- View database contents
- Check schema and data
- Useful for debugging

**[setup_local_db.py](setup_local_db.py)** - Local database setup
```bash
python agent/setup_local_db.py
```
- Initialize local SQLite database
- Create tables and schema

**[sync_database.py](sync_database.py)** - Database synchronization
```bash
python agent/sync_database.py
```
- Sync data between local and cloud databases
- Backup and restore utilities

## Tool Selection Guide

| Task | Recommended Tool | Alternative |
|------|-----------------|-------------|
| First-time exploration | `speaker_tagging_ml.ipynb` | - |
| Batch processing | `tag_speakers_ml.py` | - |
| Quick single file | `tag_speakers.py` | `tag_speakers_enhanced.py` |
| Database inspection | `check_db.py` | - |
| Local setup | `setup_local_db.py` | - |
| Data sync | `sync_database.py` | - |

## Requirements

```bash
# Install dependencies
pip install -r ../requirements.txt

# For Jupyter notebook
pip install jupyter
```

## Documentation

For detailed documentation on speaker tagging approaches, see:
- [Speaker Tagging ML Documentation](../docs/SPEAKER_TAGGING_ML.md)
- [Speaker Tagging Summary](../docs/SPEAKER_TAGGING_SUMMARY.md)
- [Speaker Patterns Reference](../docs/SPEAKER_PATTERNS.md)

## Integration

These tools can be used:
1. **Standalone** - Run scripts directly on transcript files
2. **Programmatically** - Import as Python modules
3. **Via Backend** - Called from the Flask API

Example integration:
```python
# Import ML tagger
from agent.tag_speakers_ml import SpeakerDetector, SpeakerAssigner

# Process transcript
detector = SpeakerDetector()
detections = detector.detect_all_speakers(lines)
assigner = SpeakerAssigner(lines, detections)
assignments = assigner.assign_speakers()
```

## Navigation

- [Back to Main README](../README.md)
- [Documentation Index](../docs/INDEX.md)


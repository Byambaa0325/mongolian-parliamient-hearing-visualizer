# ML/NLP Speaker Tagging for Parliament Transcripts

## Overview

This notebook (`agent/speaker_tagging_ml.ipynb`) provides automated speaker identification and tagging for raw Mongolian parliament hearing transcripts using machine learning and natural language processing techniques.

## Features

### 1. **Pattern-Based Detection**
- Detects Mongolian speaker introduction patterns
- Recognizes titles and honorifics (сайд, дарга, гишүүн, etc.)
- Multiple pattern strategies for robust detection
- Confidence scoring for each detection

### 2. **Context-Aware Assignment**
- Propagates speakers across consecutive lines
- Configurable context window
- Confidence decay over distance
- Handles speaker transitions intelligently

### 3. **Interactive Review**
- Identifies uncertain assignments
- Manual correction interface
- Real-time updates to assignments
- Quality metrics and feedback

### 4. **Visualization**
- Speaker frequency charts
- Timeline visualization
- Detection pattern analysis
- Confidence distributions

### 5. **Multiple Export Formats**
- Plain text (human-readable)
- JSON (structured data)
- CSV (spreadsheet)
- Database-ready format

### 6. **Batch Processing**
- Process multiple files at once
- Consistent tagging across sessions
- Automated quality reporting

## Quick Start

```python
# 1. Open the notebook
jupyter notebook agent/speaker_tagging_ml.ipynb

# 2. Set your transcript file (in cell 4)
TRANSCRIPT_FILE = '12.7.txt'

# 3. Run all cells (Cell > Run All)

# 4. Review the output
```

## Output Files

For input `12.7.txt`, the notebook generates:

- `12.7_tagged_ml.txt` - Tagged transcript with speaker labels
- `12.7_tagged_ml.json` - Structured JSON format
- `12.7_tagged_ml.csv` - Spreadsheet format
- `12.7_tagged_ml.report.txt` - Quality metrics and statistics

## Detection Patterns

The notebook recognizes these Mongolian patterns:

| Pattern | Example | Confidence |
|---------|---------|------------|
| `За. [Name] [Title]` | За. Баяр ерөнхий сайд | 0.95 (Very High) |
| `[Number] номерын микрофон [Name]` | 3 номерын микрофон Баяр | 0.92 (Very High) |
| `[Name] [Title] асан` | Дэмбэрэл дарга асан | 0.90 (High) |
| `За [Number] номер [Name]` | За 3 номер Дэмбэрэл | 0.88 (High) |
| `[Name] [Title] та` | Баярцогт сайд та | 0.85 (Good) |
| `[Name] гуайгаас асууя` | Ганзориг гуайгаас асууя | 0.80 (Good) |
| `[Number] номер нэмэлт минут` | 3 номер нэмэлт нэг минут | 0.75 (Continuation) |
| `[Name]-гийн` | Баяр-гийн | 0.50 (Medium) |

**Special Feature**: Microphone tracking - the tool remembers which speaker has which microphone number throughout the session.

📚 **See [SPEAKER_PATTERNS.md](SPEAKER_PATTERNS.md) for complete pattern documentation** and [PATTERN_QUICK_REFERENCE.md](PATTERN_QUICK_REFERENCE.md) for quick reference.

### Recognized Titles

- Ерөнхий сайд (Prime Minister)
- УИХ-ын дарга (Parliament Speaker)
- Тэргүүн шадар сайд (First Deputy PM)
- сайд (Minister)
- дарга (Chairman)
- захирал (Director)
- шинжээч (Expert)
- хянан шалгагч (Auditor)
- гишүүн (Member)

## Key Parameters

### context_window (default: 20)
How many lines a speaker's identification continues without re-detection.
- **Lower values** (10-15): More frequent speaker changes expected
- **Higher values** (25-30): Longer speaking segments expected

### confidence_threshold (default: 0.6)
Minimum confidence for automatic assignment.
- **Lower values** (0.4-0.5): More permissive, fewer unknowns
- **Higher values** (0.7-0.8): More conservative, more manual review needed

## Workflow

```
1. Load Transcript
   ↓
2. Detect Speaker Patterns
   ↓
3. Assign Speakers (with context)
   ↓
4. Generate Visualizations
   ↓
5. Export Tagged Files
   ↓
6. Review Uncertain Lines
   ↓
7. Manual Corrections (if needed)
   ↓
8. Final Export
```

## Usage Examples

### Basic Usage

```python
# Load and process a single file
lines = load_transcript('12.7.txt')
detector = SpeakerDetector()
detections_df = detector.detect_all_speakers(lines)
assigner = SpeakerAssigner(lines, detections_df)
assignments = assigner.assign_speakers()
export_tagged_transcript(assignments, '12.7_tagged_ml.txt', format='txt')
```

### Batch Processing

```python
# Process all transcript files
transcript_files = ['12.7.txt', '12.8.txt', '12.10.txt', '12.12.txt']
batch_results = batch_process_transcripts(transcript_files)
```

### Interactive Review

```python
# Find uncertain lines
uncertain_df = find_uncertain_lines(assignments, confidence_threshold=0.6)

# Review and correct
corrections = interactive_review(assignments, start_idx=100, num_lines=10)
```

### Custom Patterns

```python
# Add custom detection pattern
detector = SpeakerDetector()
detector.patterns['custom'] = re.compile(r'Your pattern here')
```

## Quality Metrics

The notebook provides comprehensive quality metrics:

- **Coverage**: % of lines with assigned speakers
- **Confidence**: Average confidence score
- **Unique Speakers**: Number of distinct speakers detected
- **Distribution**: Lines per speaker
- **Quality Bands**: High/Medium/Low confidence breakdown

### Interpreting Results

**Good Quality**:
- Coverage > 80%
- Average confidence > 0.7
- Few UNKNOWN assignments

**Needs Review**:
- Coverage < 60%
- Average confidence < 0.5
- Many low-confidence assignments

## Integration with Application

### Option 1: Direct File Import

```python
# Load tagged transcript into the app
# Use the existing load_transcripts.py script
python backend/load_transcripts.py --file 12.7_tagged_ml.txt
```

### Option 2: Database Integration

```python
# Use the notebook's database export
# Uncomment the database save section in the notebook
df = export_tagged_transcript(assignments, OUTPUT_FILE, format='database')
# Follow up with backend API to insert into database
```

## Troubleshooting

### Few Speakers Detected

**Cause**: Patterns don't match transcript style
**Solution**: 
- Review sample lines manually
- Add custom patterns for your specific format
- Adjust regex patterns in `SpeakerDetector`

### Many UNKNOWN Lines

**Cause**: Context window too short or patterns not matching
**Solution**:
- Increase `context_window` parameter
- Lower `confidence_threshold`
- Add more detection patterns

### Wrong Speaker Assignments

**Cause**: Pattern matches wrong text
**Solution**:
- Use interactive review to correct
- Refine patterns to be more specific
- Adjust confidence scoring

## Advanced Features

### Custom Speaker Mapping

```python
# Map detected names to canonical names
speaker_mapping = {
    'Баяр ерөнхий сайд': 'С.Баяр',
    'Дэмбэрэл дарга': 'Д.Дэмбэрэл',
    # ...
}

for item in assignments:
    if item['speaker'] in speaker_mapping:
        item['speaker'] = speaker_mapping[item['speaker']]
```

### Export to SRT Subtitles

```python
# For video subtitle sync
export_tagged_transcript(assignments, 'output.srt', format='srt')
```

### TF-IDF Analysis (Optional)

The notebook includes optional text clustering to identify speaking styles and verify speaker consistency.

## Comparison with Existing Tool

| Feature | agent/tag_speakers.py | agent/speaker_tagging_ml.ipynb |
|---------|-----------------|--------------------------|
| Detection Method | Simple regex | Multi-pattern + context |
| Confidence Scoring | No | Yes |
| Context Awareness | No | Yes |
| Visualizations | No | Yes |
| Quality Metrics | No | Yes |
| Interactive Mode | Basic | Advanced |
| Batch Processing | No | Yes |
| Export Formats | 3 | 4+ |

## Tips for Best Results

1. **Start Small**: Process one file first to test patterns
2. **Iterate**: Review results and adjust parameters
3. **Manual Review**: Always review uncertain sections
4. **Document Patterns**: Note which patterns work best for your transcripts
5. **Consistent Names**: Use canonical speaker names across files
6. **Batch Process**: Process similar files with same settings

## Requirements

```txt
python >= 3.8
pandas >= 1.3.0
numpy >= 1.21.0
scikit-learn >= 0.24.0
matplotlib >= 3.4.0
seaborn >= 0.11.0
```

Install with:
```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter
```

## Next Steps

1. ✅ Test on one transcript file (12.7.txt)
2. ⬜ Review and refine detection patterns
3. ⬜ Batch process all transcript files
4. ⬜ Manual review and corrections
5. ⬜ Load into application database
6. ⬜ Integrate with transcript viewer UI

## Support

For issues or questions:
- Review the existing documentation in `README_speaker_tagging.md`
- Check pattern definitions in the notebook
- Use the interactive review function for uncertain lines
- Refer to the summary report for quality metrics


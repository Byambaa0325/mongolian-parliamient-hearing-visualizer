# Quick Pattern Reference Card

## 🎤 Microphone Patterns (Your Key Insights!)

### Pattern 1: Microphone Assignment
```
Format: [Number] номерын микрофон [Name]
Example: "За дараагийн хариулт 3 номерын 3 номерын микрофон Баяр"
Means: Microphone #3 is assigned to Баяр
Confidence: 92% ⭐⭐⭐⭐⭐
```

### Pattern 2: Short Microphone Form
```
Format: За [Number] номер [Name]
Example: "За 3 номер Дэмбэрэл"
Means: Speaker #3 is Дэмбэрэл
Confidence: 88% ⭐⭐⭐⭐
```

### Pattern 3: Extension Request (CONTINUATION, not change!)
```
Format: [Number] номер нэмэлт [time] минут
Example: "За 3 номер нэмэлт нэг минут"
Means: Speaker at mic #3 wants 1 more minute (SAME SPEAKER continues)
Confidence: 75% ⭐⭐⭐
Action: Tool looks up who has mic #3 and continues their speech
```

## 📋 Standard Patterns

### Introduction Pattern
```
Format: За. [Name] [Title]
Example: "За. Баяр ерөнхий сайд"
Confidence: 95% ⭐⭐⭐⭐⭐
```

### Past Reference
```
Format: [Name] [Title] асан
Example: "Монгол улсын ерөнхий сайд асан Баяр"
Confidence: 90% ⭐⭐⭐⭐
```

### Question/Discussion
```
Format: [Name] гуайгаас асууя
Example: "Ганзориг гуайгаас асууя"
Confidence: 80% ⭐⭐⭐
```

## 🔍 How the Tool Works

### Step 1: Build Microphone Map
```python
# As it reads the transcript:
"3 номерын микрофон Баяр" → stores: mic[3] = "Баяр"
"5 номерын микрофон Дэмбэрэл" → stores: mic[5] = "Дэмбэрэл"
"9 номер Ганзориг" → stores: mic[9] = "Ганзориг"
```

### Step 2: Use Map for Extensions
```python
# When it sees:
"3 номер нэмэлт нэг минут"
# It looks up: mic[3] = "Баяр"
# Assigns: "Баяр" (continuation, not new speaker)
```

### Step 3: Context Propagation
```
Segment 1: [DETECTED] Баяр ерөнхий сайд (95%)
Segment 2: [INHERITED] Баяр ерөнхий сайд (85%)
Segment 3: [INHERITED] Баяр ерөнхий сайд (77%)
...
Segment 10: [DETECTED] Дэмбэрэл дарга (95%) → NEW SPEAKER
```

## 🎯 Key Examples from Your Transcripts

### Example 1: Microphone Assignment
```
Text: "За дараагийн хариулт 3 номерын 3 номерын микрофон Баяр"

Detection:
  Pattern: microphone_assignment
  Microphone: 3
  Speaker: Баяр
  Confidence: 92%
  Action: Store mic[3] = Баяр, assign speaker
```

### Example 2: Extension Request
```
Text: "За 3 номер 3 номер нэмэлт нэг минут"

Detection:
  Pattern: extension_request
  Microphone: 3
  Lookup: mic[3] = Баяр
  Speaker: Баяр (SAME SPEAKER)
  Confidence: 75%
  Action: Continue Баяр's speech
```

### Example 3: Speaker Change
```
Text: "...гэж би хэлж байна. За Дэмбэрэл дарга та хариулна уу"

Detection:
  Pattern: intro_za
  Previous: Баяр
  New Speaker: Дэмбэрэл дарга
  Confidence: 95%
  Action: Switch to Дэмбэрэл дарга
```

## 📊 Quality Metrics

After running the tool, you'll see:

```
Quality Statistics:
  - Original lines: 42
  - Total segments: ~250-300 (avg 6 per line)
  - Assigned segments: 210 (75%)
  - Unknown segments: 40 (25%)
  - Unique speakers: 15-20
  - Average confidence: 0.78
```

**Good Quality**: Coverage > 75%, Confidence > 0.70  
**Needs Review**: Coverage < 60%, Confidence < 0.60

## 🚀 Quick Commands

```bash
# Basic usage
python tag_speakers_enhanced.py 12.7.txt

# With verbose output (recommended first time)
python tag_speakers_enhanced.py 12.7.txt --verbose

# Adjust for frequent speaker changes
python tag_speakers_enhanced.py 12.7.txt --context-window 8

# Full export
python tag_speakers_enhanced.py 12.7.txt --export-json --export-csv --verbose
```

## 🔧 Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Many UNKNOWN | Too short context window | Increase `--context-window 15` |
| Wrong continuations | Too long context window | Decrease `--context-window 5` |
| Missed speaker changes | Patterns not matching | Check SPEAKER_PATTERNS.md for pattern details |
| Extension not working | Mic not mapped yet | Normal - tool learns as it reads |

## 💡 Pro Tips

1. **First microphone assignment is key** - Once the tool sees "3 номерын микрофон Баяр", it remembers this for the whole session

2. **Extensions indicate continuation** - "3 номер нэмэлт минут" means the SAME person keeps speaking, not a new speaker

3. **Compound lines are normal** - Your 42 lines will become 200-300 segments, this is expected

4. **Review uncertain segments** - Segments with confidence < 60% may need manual correction

5. **Microphone numbers are session-specific** - Mic #3 might be different people in different sessions

## 📚 See Also

- **SPEAKER_PATTERNS.md** - Complete pattern documentation
- **SPEAKER_TAGGING_ML.md** - Full user guide
- **tag_speakers_enhanced.py** - The tool with microphone tracking


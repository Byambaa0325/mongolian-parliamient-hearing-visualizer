# Mongolian Parliament Transcript - Speaker Pattern Reference

## Overview

This document describes the speaker identification patterns found in Mongolian parliament hearing transcripts. These patterns are used by the ML speaker tagging tools to automatically detect and assign speakers.

## Pattern Categories

### 1. Direct Speaker Introduction Patterns

#### Pattern: "За. [Name] [Title]"
**Mongolian**: За. Баяр ерөнхий сайд  
**English**: Well. Bayar Prime Minister  
**Confidence**: 95% (Very High)  
**Regex**: `За\.?\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})\s+(гуай|сайд|дарга|...)`

**Examples**:
- За. Баяр ерөнхий сайд
- За Дэмбэрэл дарга
- За. Ганзориг гишүүн

**Usage**: Most reliable pattern. Indicates the person is being directly introduced to speak.

---

### 2. Microphone Assignment Patterns

#### Pattern A: "[Number] номерын микрофон [Name]"
**Mongolian**: 3 номерын микрофон Баяр  
**English**: Microphone number 3, Bayar  
**Confidence**: 92% (Very High)  
**Regex**: `\d+\s+номерын\s+микрофон(?:\s+.*?)?\s+([А-ЯЁ][а-яё]+)`

**Examples**:
- 3 номерын микрофон Баяр
- За дараагийн хариулт 3 номерын микрофон Дэмбэрэл
- 7 номерын микрофон Баярцогт сайд

**Usage**: Moderator assigns a microphone to a specific person. Very reliable for identifying who will speak next.

#### Pattern B: "За [Number] номер [Name]"
**Mongolian**: За 3 номер Баяр  
**English**: Well, number 3, Bayar  
**Confidence**: 88% (High)  
**Regex**: `(?:за|За)?\s*(\d+)\s+номер(?:ын)?\s+(?:микрофон\s+)?([А-ЯЁ][а-яё]+)`

**Examples**:
- За 3 номер Баяр
- 5 номерын Дэмбэрэл
- За 9 номер микрофон Ганзориг

**Usage**: Shorter form of microphone assignment. Also very reliable.

**Feature**: The tool tracks microphone number → speaker mappings throughout the transcript.

---

### 3. Extension Request Patterns

#### Pattern: "[Number] номер нэмэлт [time] минут"
**Mongolian**: 3 номер нэмэлт нэг минут  
**English**: Number 3, extension one minute  
**Confidence**: 75% (Good - continuation signal)  
**Regex**: `(\d+)\s+номер(?:ын)?\s+нэмэлт.*?минут`

**Examples**:
- За 3 номер нэмэлт нэг минут
- 9 номерын нэмэлт хоёр минут
- За 6 номер 6 номер нэмэлт нэг минут

**Usage**: 
- Indicates the current speaker is requesting more time
- **Important**: This is NOT a speaker change - it's a continuation
- The tool looks up which speaker has this microphone number
- If known, assigns that speaker with medium-high confidence

**Special Handling**:
```python
# Tool maintains a dictionary:
microphone_speakers = {
    '3': 'Баяр ерөнхий сайд',
    '5': 'Дэмбэрэл дарга',
    '9': 'Ганзориг гишүүн'
}
```

---

### 4. Past Reference Patterns

#### Pattern: "[Name] [Title] асан"
**Mongolian**: Баяр ерөнхий сайд асан  
**English**: Bayar, former Prime Minister  
**Confidence**: 90% (High)  
**Regex**: `([А-ЯЁ][а-яё]+)\s+(сайд|дарга|...)\s+асан`

**Examples**:
- Баяр ерөнхий сайд асан
- Монгол улсын ерөнхий сайд асан Баяр
- УИХ-ын дарга асан Дэмбэрэл

**Usage**: References to former office holders. High confidence because it's specific.

---

### 5. Question/Discussion Patterns

#### Pattern: "[Name] гуайгаас асууя"
**Mongolian**: Ганзориг гуайгаас асууя  
**English**: Let's ask from Mr. Ganzurig  
**Confidence**: 80% (Good)  
**Regex**: `([А-ЯЁ][а-яё]+)\s+гуай(?:гаас)?\s+асуу`

**Examples**:
- Ганзориг гуайгаас асууя
- Баяр гуай асууя
- Дэмбэрэл гуайгаас асуулт асууя

**Usage**: Indicates someone is being called upon to ask questions or speak.

---

### 6. Direct Address Patterns

#### Pattern: "[Name] [Title] та"
**Mongolian**: Баяр ерөнхий сайд та  
**English**: Prime Minister Bayar, you  
**Confidence**: 85% (High)  
**Regex**: `([А-ЯЁ][а-яё]+)\s+(сайд|дарга|...)\s+та`

**Examples**:
- Баяр ерөнхий сайд та
- Дэмбэрэл дарга та гэрчийн суудалд сууна уу
- Баярцогт сайд та хариулна уу

**Usage**: Direct address - someone is speaking TO or ABOUT this person.

---

### 7. Possessive/Context Patterns

#### Pattern: "[Name]-гийн" or "[Name]-ын"
**Mongolian**: Баяр-гийн, Монголын  
**English**: Bayar's, Mongolia's  
**Confidence**: 50% (Medium-Low)  
**Regex**: `([А-ЯЁ][а-яё]+)-[г|ы]ийн`

**Examples**:
- Баяр-гийн хариулт
- Дэмбэрэл-гийн асуулт
- Монголын талаас

**Usage**: 
- Possessive form - less reliable for speaker identification
- Often refers to someone rather than indicating they are speaking
- Used with low confidence, mainly for context

---

## Common Titles (Mongolian)

| Mongolian | English | Context |
|-----------|---------|---------|
| Ерөнхий сайд | Prime Minister | Government head |
| УИХ-ын дарга | Parliament Speaker | Session chair |
| Тэргүүн шадар сайд | First Deputy PM | Government official |
| сайд | Minister | Cabinet member |
| дарга | Chairman/Speaker | Committee/meeting leader |
| захирал | Director | Organization head |
| гүйцэтгэх захирал | Executive Director | Company leadership |
| шинжээч | Expert/Analyst | Technical expert |
| хянан шалгагч | Auditor/Inspector | Investigation role |
| нарийн бичгийн дарга | Secretary General | Administrative head |
| гишүүн | Member | Parliament member |
| гуай | Mr./Sir (honorific) | Respectful address |

---

## Pattern Priority & Confidence Levels

When multiple patterns match the same text, the tool uses confidence scores:

| Priority | Pattern Type | Confidence | Use Case |
|----------|-------------|------------|----------|
| 1 | Introduction "За. Name Title" | 95% | Direct introduction |
| 2 | Microphone assignment | 88-92% | Moderator assigns speaker |
| 3 | Past reference "асан" | 90% | Former officials |
| 4 | Direct address "та" | 85% | Direct conversation |
| 5 | Question pattern "асууя" | 80% | Call to speak |
| 6 | Extension request | 75% | Continuation (same speaker) |
| 7 | Possessive form | 50% | Context only |

---

## Special Features

### 1. Microphone Tracking
The tool maintains a mapping of microphone numbers to speakers:
- When "3 номерын микрофон Баяр" is detected → stores mic #3 = Баяр
- Later, "3 номер нэмэлт минут" → looks up mic #3 → assigns Баяр
- Persists throughout the transcript session

### 2. Position Weighting
Patterns found at the **start of a segment** (first 50 characters) get a +5% confidence boost:
- "За. Баяр сайд [long text]..." → 95% + 5% = **98% confidence**
- "[long text]... За. Баяр сайд" → 95% confidence

### 3. Context Propagation
After detecting a speaker, subsequent segments inherit that speaker:
- Detection at segment 10: Баяр (confidence: 95%)
- Segment 11: Баяр (confidence: 85%) - inherited
- Segment 12: Баяр (confidence: 77%) - inherited with decay
- Segment 13: New detection or UNKNOWN

Default context window: **10 segments** (adjustable via `--context-window` flag)

---

## Example Transcript Flow

```
Original Line 25 (compound line with ~800 words):

Segment 1: "За дараагийн хариулт 3 номерын микрофон Баяр ерөнхий сайд..."
→ DETECTED: Баяр ерөнхий сайд (microphone_assignment: 92%)
→ STORED: mic #3 = Баяр ерөнхий сайд

Segment 2: "...энэ асуудлыг хэлэлцэхдээ бид нар..."
→ INHERITED: Баяр ерөнхий сайд (85%)

Segment 3: "За 3 номер нэмэлт нэг минут..."
→ DETECTED: Extension request for mic #3
→ LOOKUP: mic #3 = Баяр ерөнхий сайд
→ ASSIGNED: Баяр ерөнхий сайд (75%)

Segment 4: "...гэж би хэлж байна. За Дэмбэрэл дарга..."
→ DETECTED: Дэмбэрэл дарга (intro_za: 95%)
→ SPEAKER CHANGE

Segment 5: "...танилцуулъя та бүхэнд..."
→ INHERITED: Дэмбэрэл дарга (85%)
```

---

## Edge Cases & Challenges

### 1. Multiple Names in One Segment
```
"За Баяр ерөнхий сайд асан Дэмбэрэл дарга..."
```
- Two speakers mentioned
- Tool takes **highest confidence** match
- Consider manual review if confidence < 70%

### 2. No Clear Speaker Indicator
```
"Энэ асуудлыг хэлэлцэхдээ бид нар анхаарах ёстой..."
```
- No speaker pattern
- Relies on context propagation
- Will inherit previous speaker or mark UNKNOWN

### 3. Microphone Number Without Name
```
"За 3 номер..." (no name following)
```
- Looks up mic #3 in tracking dictionary
- If found: assigns that speaker
- If not found: marks as UNKNOWN

### 4. Ambiguous Extensions
```
"За нэмэлт нэг минут..." (no microphone number)
```
- Cannot determine which speaker
- Relies on context propagation
- Inherits previous speaker

---

## Configuration & Tuning

### Adjust Context Window
For transcripts with frequent speaker changes:
```bash
python tag_speakers_enhanced.py transcript.txt --context-window 5
```

For transcripts with long speaking turns:
```bash
python tag_speakers_enhanced.py transcript.txt --context-window 15
```

### Adjust Segment Length
For finer-grained segmentation:
```bash
python tag_speakers_enhanced.py transcript.txt --max-segment-length 200
```

For larger segments:
```bash
python tag_speakers_enhanced.py transcript.txt --max-segment-length 500
```

---

## Quality Indicators

**Good Quality Detection**:
- ✅ Many direct introductions ("За. Name Title")
- ✅ Consistent microphone assignments
- ✅ Clear speaker changes with patterns
- ✅ Coverage > 75%

**Needs Manual Review**:
- ⚠️ Few direct speaker mentions
- ⚠️ Heavy reliance on context propagation
- ⚠️ Coverage < 60%
- ⚠️ Many UNKNOWN segments

**Requires Adjustment**:
- ❌ Wrong speaker continuations
- ❌ Missed speaker changes
- ❌ Microphone tracking inconsistent

---

## Adding Custom Patterns

To add your own patterns, edit `tag_speakers_enhanced.py`:

```python
self.patterns = {
    # Add your custom pattern here
    'your_pattern_name': re.compile(
        r'your_regex_pattern',
        re.IGNORECASE
    ),
    # ... existing patterns
}

# Update confidence scores
def _calculate_confidence(self, pattern_name: str, text: str, position: int):
    base_scores = {
        'your_pattern_name': 0.85,  # Set appropriate confidence
        # ... existing scores
    }
```

---

## Testing Patterns

To test if patterns work on your transcript:

```bash
# Run with verbose mode
python tag_speakers_enhanced.py 12.7.txt --verbose

# Check the output for:
# - Detection counts by pattern type
# - Sample detections
# - Confidence distribution
```

---

## Further Improvements

Potential enhancements for future versions:

1. **Named Entity Recognition (NER)**: Train a custom Mongolian NER model
2. **Speaker Diarization**: Use audio timestamps if available
3. **Co-reference Resolution**: Track when "тэр" (he/she) refers to a specific speaker
4. **Question-Answer Pairing**: Link questions to responses
5. **Topic Segmentation**: Identify topic changes that may signal new speakers

---

## References

- **Mongolian Grammar**: Possessive case, honorifics
- **Parliament Procedures**: Microphone protocols, speaking order
- **Regex Documentation**: Python `re` module

---

**Last Updated**: December 2024  
**Version**: 2.0 (Enhanced for compound lines with microphone tracking)


# Speaker Tagging Guide for Raw Transcripts

## Overview

This guide explains how to tag speakers in raw text transcripts, specifically for Mongolian parliamentary hearing transcripts.

## Challenge

Raw transcripts don't have speaker labels. You need to identify:
- Who is speaking
- When speakers change
- Context clues (titles, names, question patterns)

## Methods

### Method 1: Interactive Tagging (Recommended)

Use the provided Python script for guided tagging:

```bash
python tag_speakers.py 12.7.txt 12.7_tagged.txt
```

**Steps:**
1. Script loads the transcript
2. Detects potential speaker patterns
3. Shows text chunks (5 lines at a time)
4. You assign speakers for each chunk
4. Exports tagged transcript

**Commands:**
- Enter speaker name to assign
- `s` - Skip segment
- `u` - Undo last assignment
- `q` - Quit and save
- `?` - Show current speakers

### Method 2: Pattern-Based Detection

The script automatically detects:
- Speaker introductions: "За. [Name] [Title]"
- Questions: Lines containing "?"
- Titles: Ерөнхий сайд, УИХ-ын дарга, сайд, etc.

**Limitations:**
- May miss some speaker changes
- Requires manual review
- Best used as starting point

### Method 3: Manual Tagging

For maximum accuracy, manually tag:

1. **Identify speaker indicators:**
   - Look for "За. [Name] [Title]" patterns
   - Find question markers
   - Note context changes

2. **Common patterns in Mongolian transcripts:**
   - "За. [Name] гуай" - Speaker introduction
   - "[Name] сайд" - Minister speaking
   - "УИХ-ын дарга" - Parliament speaker
   - Questions often indicate speaker change

3. **Tagging format:**
   ```
   [Speaker Name]: [Text content]
   ```

## Output Formats

The script exports in multiple formats:

1. **Plain text** (`.txt`):
   ```
   [Баяр ерөнхий сайд]: За. Та бүхэнд энэ өдрийн мэндийг хүргэе...
   [Дэмбэрэл дарга]: За. Энэ өдрийн та бүхний амар амгаланг айлтгая...
   ```

2. **JSON** (`.json`):
   ```json
   [
     {
       "line_num": 1,
       "speaker": "Баяр ерөнхий сайд",
       "text": "За. Та бүхэнд..."
     }
   ]
   ```

3. **SRT subtitles** (`.srt`):
   ```
   1
   00:00:00,000 --> 00:00:05,000
   [Баяр ерөнхий сайд]: За. Та бүхэнд...
   ```

## Tips for Accurate Tagging

1. **Read context**: Understand the conversation flow
2. **Note titles**: Mongolian transcripts often use titles (сайд, дарга, гуай)
3. **Watch for questions**: Questions usually indicate speaker change
4. **Check patterns**: Look for "За." (Well) which often introduces speakers
5. **Review**: Always review auto-tagged results

## Common Speaker Patterns in Your Transcripts

Based on the transcript structure, common speakers include:

- **УИХ-ын дарга** (Parliament Speaker)
- **Ерөнхий сайд** (Prime Minister)
- **Сайд** (Minister)
- **Шинжээч** (Expert/Analyst)
- **Хянан шалгагч** (Auditor)
- **УИХ-ын гишүүн** (Parliament Member)

## Workflow Recommendation

1. **First pass**: Run auto-detection to get initial tags
2. **Review**: Read through and identify obvious errors
3. **Refine**: Use interactive mode to correct mistakes
4. **Final check**: Read entire tagged transcript for consistency

## Example Workflow

```bash
# Step 1: Auto-detect patterns
python tag_speakers.py 12.7.txt 12.7_tagged.txt
# Choose option 2 (auto-tag)

# Step 2: Review and manually correct
# Open 12.7_tagged.txt and fix errors

# Step 3: Re-run interactive mode for difficult sections
python tag_speakers.py 12.7.txt 12.7_tagged.txt
# Choose option 1 (interactive)
```

## Troubleshooting

**Problem**: Script can't detect speakers
- **Solution**: Use interactive mode and tag manually

**Problem**: Too many "UNKNOWN" speakers
- **Solution**: Review transcript for missed patterns, adjust detection rules

**Problem**: Speaker changes not detected
- **Solution**: Look for context clues (questions, topic changes, pauses)

## Next Steps

After tagging:
1. Validate speaker names are consistent
2. Check for missing speaker changes
3. Export in desired format
4. Use tagged transcript for analysis


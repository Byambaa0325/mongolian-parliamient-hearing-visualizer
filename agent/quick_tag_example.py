#!/usr/bin/env python3
"""
Quick Example: ML Speaker Tagging

This script demonstrates how to use the ML speaker tagging tools
to automatically tag a parliament transcript.
"""

from tag_speakers_ml import SpeakerDetector, SpeakerAssigner, load_transcript, export_tagged

# Configuration
TRANSCRIPT_FILE = '12.7.txt'
OUTPUT_FILE = '12.7_tagged_example.txt'
CONTEXT_WINDOW = 20  # How many lines a speaker continues without re-detection

print("=" * 80)
print("ML Speaker Tagging - Quick Example")
print("=" * 80)

# Step 1: Load transcript
print(f"\n1. Loading transcript: {TRANSCRIPT_FILE}")
lines = load_transcript(TRANSCRIPT_FILE)
print(f"   ✓ Loaded {len(lines)} lines")

# Step 2: Detect speakers
print("\n2. Detecting speaker patterns...")
detector = SpeakerDetector()
detections_df = detector.detect_all_speakers(lines)
print(f"   ✓ Found {len(detections_df)} speaker mentions")

if len(detections_df) > 0:
    print("\n   Top 5 detected speakers:")
    for speaker, count in detections_df['full_name'].value_counts().head(5).items():
        print(f"   - {speaker}: {count} mentions")

# Step 3: Assign speakers to all lines
print(f"\n3. Assigning speakers (context window: {CONTEXT_WINDOW} lines)...")
assigner = SpeakerAssigner(lines, detections_df)
assignments = assigner.assign_speakers(context_window=CONTEXT_WINDOW)
print(f"   ✓ Assigned speakers to {len(assignments)} lines")

# Step 4: Get statistics
print("\n4. Quality Statistics:")
stats = assigner.get_statistics()
print(f"   - Total lines: {stats['total_lines']}")
print(f"   - Assigned lines: {stats['assigned_lines']} ({stats['assigned_lines']/stats['total_lines']*100:.1f}%)")
print(f"   - Unknown lines: {stats['unknown_lines']} ({stats['unknown_lines']/stats['total_lines']*100:.1f}%)")
print(f"   - Unique speakers: {stats['unique_speakers']}")
print(f"   - Average confidence: {stats['avg_confidence']:.2f}")

# Step 5: Show sample of assignments
print("\n5. Sample of tagged lines:")
for i, item in enumerate(assignments[:5]):
    print(f"   Line {item['line_num']}: [{item['speaker']}] (conf: {item['confidence']:.2f})")
    print(f"            {item['text'][:80]}...")

# Step 6: Export
print(f"\n6. Exporting to {OUTPUT_FILE}...")
export_tagged(assignments, OUTPUT_FILE, format='txt')
export_tagged(assignments, OUTPUT_FILE, format='json')
export_tagged(assignments, OUTPUT_FILE, format='csv')

print(f"   ✓ Text: {OUTPUT_FILE}")
print(f"   ✓ JSON: {OUTPUT_FILE.replace('.txt', '.json')}")
print(f"   ✓ CSV:  {OUTPUT_FILE.replace('.txt', '.csv')}")

# Step 7: Quality assessment
print("\n7. Quality Assessment:")
coverage = stats['assigned_lines'] / stats['total_lines'] * 100
if coverage > 80 and stats['avg_confidence'] > 0.7:
    print("   ✓ Excellent quality! Ready to use.")
    print("   → Recommended: Quick manual review of uncertain lines")
elif coverage > 60 and stats['avg_confidence'] > 0.5:
    print("   ⚠ Good quality but needs review")
    print("   → Recommended: Review uncertain lines using interactive mode")
else:
    print("   ⚠ Low quality - needs manual intervention")
    print("   → Recommended: Use interactive review mode or adjust parameters")

print("\n" + "=" * 80)
print("Tagging Complete!")
print("=" * 80)

print("\nNext Steps:")
print("1. Review the tagged output files")
print("2. Use interactive_review() for uncertain sections (see notebook)")
print("3. Load into database: python backend/load_transcripts.py --file", OUTPUT_FILE)
print("4. Process more files: python tag_speakers_ml.py <file> --export-json")
print("\nFor more options: python tag_speakers_ml.py --help")

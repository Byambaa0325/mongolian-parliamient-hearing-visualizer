#!/usr/bin/env python3
"""
Enhanced ML Speaker Tagging for Compound Transcript Lines

This version handles transcripts where each line contains hundreds of words
and multiple speaker changes, rather than individual speaking turns.
"""

import re
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Tuple


class TranscriptSegmenter:
    """Split compound transcript lines into smaller segments"""
    
    def __init__(self):
        # Sentence-ending patterns
        self.sentence_enders = [
            r'\.(?:\s+|$)',  # Period followed by space or end
            r'\?(?:\s+|$)',  # Question mark
            r'!(?:\s+|$)',   # Exclamation
            r'\.\.\.(?:\s+|$)',  # Ellipsis
        ]
        
        # Strong speaker change indicators
        self.speaker_indicators = [
            r'За\.?\s+[А-ЯЁ][а-яё]+',  # "За. Name"
            r'[А-ЯЁ][а-яё]+\s+(гуай|сайд|дарга|гишүүн)',  # Name + title
        ]
    
    def segment_line(self, line: str, original_line_num: int) -> List[Dict]:
        """
        Split a compound line into smaller segments.
        
        Strategy:
        1. Look for strong speaker indicators
        2. Split on sentence boundaries
        3. Keep segments reasonably sized (not too small)
        """
        segments = []
        
        # First, find all speaker change points
        change_points = []
        for pattern in self.speaker_indicators:
            for match in re.finditer(pattern, line, re.IGNORECASE):
                change_points.append(match.start())
        
        change_points = sorted(set(change_points))
        change_points.append(len(line))  # Add end of line
        
        # Split line at change points
        if not change_points or change_points[0] != 0:
            change_points.insert(0, 0)
        
        segment_num = 0
        for i in range(len(change_points) - 1):
            start = change_points[i]
            end = change_points[i + 1]
            text = line[start:end].strip()
            
            if text:  # Only add non-empty segments
                # Further split long segments by sentences
                if len(text) > 500:  # If segment is still very long
                    sub_segments = self._split_by_sentences(text)
                    for sub_seg in sub_segments:
                        if sub_seg.strip():
                            segments.append({
                                'original_line': original_line_num,
                                'segment_num': segment_num,
                                'text': sub_seg.strip(),
                                'char_start': start,
                                'char_end': start + len(sub_seg)
                            })
                            segment_num += 1
                else:
                    segments.append({
                        'original_line': original_line_num,
                        'segment_num': segment_num,
                        'text': text,
                        'char_start': start,
                        'char_end': end
                    })
                    segment_num += 1
        
        return segments
    
    def _split_by_sentences(self, text: str, max_length: int = 300) -> List[str]:
        """Split text by sentences, keeping segments under max_length"""
        sentences = []
        current = ""
        
        # Split on sentence enders
        parts = re.split(r'([.?!]+\s+)', text)
        
        for i in range(0, len(parts), 2):
            sentence = parts[i]
            if i + 1 < len(parts):
                sentence += parts[i + 1]
            
            if len(current) + len(sentence) > max_length and current:
                sentences.append(current.strip())
                current = sentence
            else:
                current += sentence
        
        if current:
            sentences.append(current.strip())
        
        return sentences
    
    def segment_transcript(self, lines: List[str]) -> pd.DataFrame:
        """Segment all lines in transcript"""
        all_segments = []
        
        for line_num, line in enumerate(lines, 1):
            segments = self.segment_line(line, line_num)
            all_segments.extend(segments)
        
        df = pd.DataFrame(all_segments)
        if len(df) > 0:
            df['segment_id'] = range(1, len(df) + 1)
        return df


class EnhancedSpeakerDetector:
    """Enhanced speaker detection for segmented transcripts"""
    
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
        
        # Enhanced patterns for speaker detection
        self.patterns = {
            # Very high confidence - direct introduction
            'intro_za': re.compile(
                r'За\.?\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})\s+(гуай|' + '|'.join(self.titles) + ')',
                re.IGNORECASE
            ),
            # High confidence - past reference
            'title_asan': re.compile(
                r'([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})\s+(' + '|'.join(self.titles) + r')\s+асан',
                re.IGNORECASE
            ),
            # Good confidence - direct address
            'title_ta': re.compile(
                r'([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})\s+(' + '|'.join(self.titles) + r')\s+та',
                re.IGNORECASE
            ),
            # High confidence - microphone assignment "3 номерын микрофон [Name]"
            'microphone_assignment': re.compile(
                r'\d+\s+номерын\s+микрофон(?:\s+.*?)?\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})',
                re.IGNORECASE
            ),
            # High confidence - "за [Number] номер [Name]" or just "[Number] номер [Name]"
            'number_name': re.compile(
                r'(?:за|За)?\s*(\d+)\s+номер(?:ын)?\s+(?:микрофон\s+)?([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)',
                re.IGNORECASE
            ),
            # Medium confidence - extension request "3 номер нэмэлт нэг минут"
            # This indicates the current speaker, not a new one
            'extension_request': re.compile(
                r'(\d+)\s+номер(?:ын)?\s+нэмэлт.*?минут',
                re.IGNORECASE
            ),
            # Good confidence - "Name гуайгаас асууя"
            'name_guai_asuuya': re.compile(
                r'([А-ЯЁ][а-яё]+)\s+гуай(?:гаас)?\s+асуу',
                re.IGNORECASE
            ),
            # Medium confidence - possessive
            'name_giin': re.compile(
                r'([А-ЯЁ][а-яё]+)-[г|ы]ийн',
                re.IGNORECASE
            ),
        }
        
        # Track microphone number to speaker mappings
        self.microphone_speakers = {}
        
        self.question_words = ['асууя', 'асуулт', 'хэлнэ үү', 'гэж асууж байна']
    
    def detect_speakers_in_segment(self, text: str) -> List[Dict]:
        """Detect potential speakers in a segment"""
        detected = []
        
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                # Handle different pattern types
                if pattern_name == 'microphone_assignment':
                    # Pattern: "3 номерын микрофон [Name]"
                    name = match.group(1).strip()
                    title = ''
                    # Store microphone number if available
                    mic_match = re.search(r'(\d+)\s+номерын\s+микрофон', text[:match.start() + 30])
                    if mic_match:
                        mic_num = mic_match.group(1)
                        self.microphone_speakers[mic_num] = name
                
                elif pattern_name == 'number_name':
                    # Pattern: "за 3 номер [Name]" or "3 номерын микрофон [Name]"
                    mic_num = match.group(1).strip()
                    name = match.group(2).strip()
                    title = ''
                    # Store microphone mapping
                    self.microphone_speakers[mic_num] = name
                
                elif pattern_name == 'extension_request':
                    # Extension request - check if we know who has this microphone
                    mic_num = match.group(1).strip()
                    if mic_num in self.microphone_speakers:
                        name = self.microphone_speakers[mic_num]
                        title = ''
                    else:
                        continue  # Skip if we don't know who has this mic
                
                else:
                    # Standard patterns
                    name = match.group(1).strip()
                    title = match.group(2).strip() if match.lastindex >= 2 else ''
                
                detected.append({
                    'pattern': pattern_name,
                    'name': name,
                    'title': title,
                    'full_name': f"{name} {title}".strip(),
                    'position': match.start(),
                    'confidence': self._calculate_confidence(pattern_name, text, match.start())
                })
        
        return detected
    
    def _calculate_confidence(self, pattern_name: str, text: str, position: int) -> float:
        """Calculate confidence score with position weighting"""
        base_scores = {
            'intro_za': 0.95,                    # "За. Name Title"
            'title_asan': 0.90,                  # "Name Title асан"
            'microphone_assignment': 0.92,       # "3 номерын микрофон Name"
            'number_name': 0.88,                 # "за 3 номер Name"
            'title_ta': 0.85,                    # "Name Title та"
            'extension_request': 0.75,           # "3 номер нэмэлт минут" (continuation)
            'name_guai_asuuya': 0.80,           # "Name гуайгаас асууя"
            'name_giin': 0.50,                   # "Name-гийн" (possessive)
        }
        
        base_score = base_scores.get(pattern_name, 0.5)
        
        # Boost confidence if speaker mention is at start of segment
        if position < 50:
            base_score = min(0.98, base_score + 0.05)
        
        return base_score
    
    def detect_all_speakers(self, segments_df: pd.DataFrame) -> pd.DataFrame:
        """Detect speakers across all segments"""
        detections = []
        
        for idx, row in segments_df.iterrows():
            speakers = self.detect_speakers_in_segment(row['text'])
            for speaker in speakers:
                detections.append({
                    'segment_id': row['segment_id'],
                    'original_line': row['original_line'],
                    'segment_num': row['segment_num'],
                    'speaker_name': speaker['name'],
                    'speaker_title': speaker['title'],
                    'full_name': speaker['full_name'],
                    'pattern': speaker['pattern'],
                    'confidence': speaker['confidence'],
                })
        
        return pd.DataFrame(detections)


class SegmentSpeakerAssigner:
    """Assign speakers to segments with context awareness"""
    
    def __init__(self, segments_df: pd.DataFrame, detections_df: pd.DataFrame):
        self.segments = segments_df
        self.detections = detections_df
        self.assignments = []
    
    def assign_speakers(self, context_window: int = 10) -> List[Dict]:
        """
        Assign speakers to all segments.
        
        For compound lines, use shorter context window since speaker
        changes happen more frequently.
        """
        speaker_by_segment = {}
        if len(self.detections) > 0:
            for segment_id in self.detections['segment_id'].unique():
                seg_detections = self.detections[self.detections['segment_id'] == segment_id]
                best = seg_detections.loc[seg_detections['confidence'].idxmax()]
                speaker_by_segment[segment_id] = {
                    'name': best['full_name'],
                    'confidence': best['confidence']
                }
        
        current_speaker = None
        segments_since_detection = 0
        
        for idx, row in self.segments.iterrows():
            segment_id = row['segment_id']
            
            if segment_id in speaker_by_segment:
                current_speaker = speaker_by_segment[segment_id]['name']
                assigned_speaker = current_speaker
                confidence = speaker_by_segment[segment_id]['confidence']
                segments_since_detection = 0
            elif current_speaker and segments_since_detection < context_window:
                assigned_speaker = current_speaker
                confidence = max(0.3, 0.85 - (segments_since_detection * 0.08))
                segments_since_detection += 1
            else:
                assigned_speaker = 'UNKNOWN'
                confidence = 0.0
                segments_since_detection += 1
            
            self.assignments.append({
                'segment_id': segment_id,
                'original_line': row['original_line'],
                'segment_num': row['segment_num'],
                'speaker': assigned_speaker,
                'confidence': confidence,
                'text': row['text'],
                'char_start': row['char_start'],
                'char_end': row['char_end']
            })
        
        return self.assignments
    
    def get_statistics(self) -> Dict:
        """Get assignment statistics"""
        df = pd.DataFrame(self.assignments)
        
        stats = {
            'total_segments': len(df),
            'total_original_lines': df['original_line'].nunique(),
            'assigned_segments': len(df[df['speaker'] != 'UNKNOWN']),
            'unknown_segments': len(df[df['speaker'] == 'UNKNOWN']),
            'unique_speakers': df[df['speaker'] != 'UNKNOWN']['speaker'].nunique(),
            'avg_confidence': df['confidence'].mean(),
            'speaker_distribution': df['speaker'].value_counts().to_dict(),
            'avg_segments_per_line': len(df) / df['original_line'].nunique() if len(df) > 0 else 0
        }
        
        return stats


def load_transcript(file_path: str) -> List[str]:
    """Load transcript from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return [line.strip() for line in content.split('\n') if line.strip()]


def export_tagged_segments(assignments: List[Dict], output_file: str, format: str = 'txt'):
    """Export tagged segments"""
    output_path = Path(output_file)
    
    if format == 'txt':
        with open(output_path, 'w', encoding='utf-8') as f:
            current_speaker = None
            current_line = None
            
            for item in assignments:
                # Add line separator when moving to new original line
                if current_line != item['original_line']:
                    f.write(f"\n--- Original Line {item['original_line']} ---\n")
                    current_line = item['original_line']
                    current_speaker = None
                
                # Add speaker tag when speaker changes
                if item['speaker'] != current_speaker:
                    f.write(f"\n[{item['speaker']}]\n")
                    current_speaker = item['speaker']
                
                f.write(f"{item['text']}\n")
    
    elif format == 'json':
        with open(output_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
            json.dump(assignments, f, ensure_ascii=False, indent=2)
    
    elif format == 'csv':
        df = pd.DataFrame(assignments)
        df.to_csv(output_path.with_suffix('.csv'), index=False, encoding='utf-8')


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Enhanced ML Speaker Tagging for Compound Transcript Lines'
    )
    parser.add_argument('input_file', help='Input transcript file')
    parser.add_argument('--output', '-o', help='Output file (default: input_tagged_enhanced.txt)')
    parser.add_argument('--context-window', '-c', type=int, default=10,
                        help='Context window for speaker continuation in segments (default: 10)')
    parser.add_argument('--max-segment-length', '-m', type=int, default=300,
                        help='Maximum segment length in characters (default: 300)')
    parser.add_argument('--export-json', action='store_true', help='Also export JSON')
    parser.add_argument('--export-csv', action='store_true', help='Also export CSV')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if not args.output:
        input_path = Path(args.input_file)
        args.output = f"{input_path.stem}_tagged_enhanced.txt"
    
    print("=" * 80)
    print("ENHANCED ML SPEAKER TAGGING")
    print("For compound transcript lines with multiple speakers per line")
    print("=" * 80)
    
    # Step 1: Load transcript
    print(f"\n1. Loading transcript: {args.input_file}")
    lines = load_transcript(args.input_file)
    print(f"   ✓ Loaded {len(lines)} original lines")
    
    # Step 2: Segment compound lines
    print("\n2. Segmenting compound lines...")
    segmenter = TranscriptSegmenter()
    segments_df = segmenter.segment_transcript(lines)
    print(f"   ✓ Created {len(segments_df)} segments from {len(lines)} lines")
    print(f"   ✓ Average {len(segments_df)/len(lines):.1f} segments per line")
    
    if args.verbose and len(segments_df) > 0:
        print("\n   Sample segments from first line:")
        first_line_segs = segments_df[segments_df['original_line'] == 1].head(3)
        for _, seg in first_line_segs.iterrows():
            print(f"   - Segment {seg['segment_num']}: {seg['text'][:80]}...")
    
    # Step 3: Detect speakers
    print("\n3. Detecting speakers in segments...")
    detector = EnhancedSpeakerDetector()
    detections_df = detector.detect_all_speakers(segments_df)
    print(f"   ✓ Found {len(detections_df)} speaker mentions")
    
    if args.verbose and len(detections_df) > 0:
        print("\n   Top speakers detected:")
        for speaker, count in detections_df['full_name'].value_counts().head(5).items():
            print(f"   - {speaker}: {count} mentions")
    
    # Step 4: Assign speakers
    print(f"\n4. Assigning speakers (context window: {args.context_window} segments)...")
    assigner = SegmentSpeakerAssigner(segments_df, detections_df)
    assignments = assigner.assign_speakers(context_window=args.context_window)
    print(f"   ✓ Assigned speakers to {len(assignments)} segments")
    
    # Step 5: Statistics
    print("\n5. Quality Statistics:")
    stats = assigner.get_statistics()
    print(f"   - Original lines: {stats['total_original_lines']}")
    print(f"   - Total segments: {stats['total_segments']}")
    print(f"   - Segments per line: {stats['avg_segments_per_line']:.1f}")
    print(f"   - Assigned segments: {stats['assigned_segments']} ({stats['assigned_segments']/stats['total_segments']*100:.1f}%)")
    print(f"   - Unknown segments: {stats['unknown_segments']} ({stats['unknown_segments']/stats['total_segments']*100:.1f}%)")
    print(f"   - Unique speakers: {stats['unique_speakers']}")
    print(f"   - Average confidence: {stats['avg_confidence']:.2f}")
    
    # Step 6: Export
    print(f"\n6. Exporting to {args.output}...")
    export_tagged_segments(assignments, args.output, format='txt')
    print(f"   ✓ Text: {args.output}")
    
    if args.export_json:
        export_tagged_segments(assignments, args.output, format='json')
        print(f"   ✓ JSON: {Path(args.output).with_suffix('.json')}")
    
    if args.export_csv:
        export_tagged_segments(assignments, args.output, format='csv')
        print(f"   ✓ CSV: {Path(args.output).with_suffix('.csv')}")
    
    # Step 7: Quality assessment
    print("\n7. Quality Assessment:")
    coverage = stats['assigned_segments'] / stats['total_segments'] * 100
    if coverage > 75 and stats['avg_confidence'] > 0.7:
        print("   ✓ Excellent quality for compound lines!")
    elif coverage > 60:
        print("   ⚠ Good quality but may need review")
    else:
        print("   ⚠ Lower quality - consider adjusting parameters")
    
    print("\n" + "=" * 80)
    print("Tagging Complete!")
    print("=" * 80)
    print(f"\nProcessed {stats['total_original_lines']} compound lines into")
    print(f"{stats['total_segments']} segments (~{stats['avg_segments_per_line']:.1f} per line)")
    print(f"\nReview the output to see speaker changes within each original line.")


if __name__ == '__main__':
    main()


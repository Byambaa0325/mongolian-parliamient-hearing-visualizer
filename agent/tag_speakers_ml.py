#!/usr/bin/env python3
"""
ML-Enhanced Speaker Tagging Tool
Automated speaker detection and tagging for Mongolian parliament transcripts

Usage:
    python tag_speakers_ml.py <input_file> [--output output_file] [--context-window 20]
    
Example:
    python tag_speakers_ml.py 12.7.txt --output 12.7_tagged.txt --context-window 20
"""

import argparse
import re
import json
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict


class SpeakerDetector:
    """Advanced speaker detection using multiple strategies"""
    
    def __init__(self):
        # Common Mongolian titles and patterns
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
        
        # Compile patterns
        self.patterns = {
            'intro_za': re.compile(
                r'За\.?\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})\s+(гуай|' + '|'.join(self.titles) + ')',
                re.IGNORECASE
            ),
            'title_asan': re.compile(
                r'([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})\s+(' + '|'.join(self.titles) + r')\s+асан',
                re.IGNORECASE
            ),
            'title_ta': re.compile(
                r'([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){0,2})\s+(' + '|'.join(self.titles) + r')\s+та',
                re.IGNORECASE
            ),
            'name_giin': re.compile(
                r'([А-ЯЁ][а-яё]+)-[г|ы]ийн',
                re.IGNORECASE
            ),
        }
        
        self.question_words = ['асууя', 'асуулт', 'хэлнэ үү', 'гэж асууж байна']
    
    def detect_speakers_in_line(self, line: str) -> List[Dict]:
        """Detect potential speakers in a single line"""
        detected = []
        
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.finditer(line)
            for match in matches:
                detected.append({
                    'pattern': pattern_name,
                    'name': match.group(1).strip(),
                    'title': match.group(2).strip() if match.lastindex >= 2 else '',
                    'confidence': self._calculate_confidence(pattern_name)
                })
        
        return detected
    
    def _calculate_confidence(self, pattern_name: str) -> float:
        """Calculate confidence score for detected speaker"""
        base_scores = {
            'intro_za': 0.9,
            'title_asan': 0.85,
            'title_ta': 0.8,
            'name_giin': 0.5,
        }
        return base_scores.get(pattern_name, 0.5)
    
    def detect_all_speakers(self, lines: List[str]) -> pd.DataFrame:
        """Detect speakers across all lines"""
        detections = []
        
        for line_num, line in enumerate(lines, 1):
            speakers = self.detect_speakers_in_line(line)
            for speaker in speakers:
                detections.append({
                    'line_num': line_num,
                    'speaker_name': speaker['name'],
                    'speaker_title': speaker['title'],
                    'full_name': f"{speaker['name']} {speaker['title']}".strip(),
                    'pattern': speaker['pattern'],
                    'confidence': speaker['confidence'],
                })
        
        return pd.DataFrame(detections)


class SpeakerAssigner:
    """Assign speakers to transcript lines using context"""
    
    def __init__(self, lines: List[str], detections_df: pd.DataFrame):
        self.lines = lines
        self.detections = detections_df
        self.assignments = []
    
    def assign_speakers(self, context_window: int = 20) -> List[Dict]:
        """Assign speakers to all lines"""
        speaker_by_line = {}
        if len(self.detections) > 0:
            for line_num in self.detections['line_num'].unique():
                line_detections = self.detections[self.detections['line_num'] == line_num]
                best = line_detections.loc[line_detections['confidence'].idxmax()]
                speaker_by_line[line_num] = {
                    'name': best['full_name'],
                    'confidence': best['confidence']
                }
        
        current_speaker = None
        lines_since_detection = 0
        
        for line_num, line in enumerate(self.lines, 1):
            if line_num in speaker_by_line:
                current_speaker = speaker_by_line[line_num]['name']
                assigned_speaker = current_speaker
                confidence = speaker_by_line[line_num]['confidence']
                lines_since_detection = 0
            elif current_speaker and lines_since_detection < context_window:
                assigned_speaker = current_speaker
                confidence = max(0.3, 0.8 - (lines_since_detection * 0.05))
                lines_since_detection += 1
            else:
                assigned_speaker = 'UNKNOWN'
                confidence = 0.0
                lines_since_detection += 1
            
            self.assignments.append({
                'line_num': line_num,
                'speaker': assigned_speaker,
                'confidence': confidence,
                'text': line
            })
        
        return self.assignments
    
    def get_statistics(self) -> Dict:
        """Get assignment statistics"""
        df = pd.DataFrame(self.assignments)
        return {
            'total_lines': len(df),
            'assigned_lines': len(df[df['speaker'] != 'UNKNOWN']),
            'unknown_lines': len(df[df['speaker'] == 'UNKNOWN']),
            'unique_speakers': df[df['speaker'] != 'UNKNOWN']['speaker'].nunique(),
            'avg_confidence': df['confidence'].mean(),
            'speaker_distribution': df['speaker'].value_counts().to_dict()
        }


def load_transcript(file_path: str) -> List[str]:
    """Load transcript from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return [line.strip() for line in content.split('\n') if line.strip()]


def export_tagged(assignments: List[Dict], output_file: str, format: str = 'txt'):
    """Export tagged transcript"""
    output_path = Path(output_file)
    
    if format == 'txt':
        with open(output_path, 'w', encoding='utf-8') as f:
            current_speaker = None
            for item in assignments:
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


def generate_report(stats: Dict, output_file: str) -> str:
    """Generate summary report"""
    report = f"""
{'=' * 80}
SPEAKER TAGGING REPORT
{'=' * 80}

STATISTICS
{'-' * 80}
Total Lines:         {stats['total_lines']}
Assigned Lines:      {stats['assigned_lines']} ({stats['assigned_lines']/stats['total_lines']*100:.1f}%)
Unknown Lines:       {stats['unknown_lines']} ({stats['unknown_lines']/stats['total_lines']*100:.1f}%)
Unique Speakers:     {stats['unique_speakers']}
Average Confidence:  {stats['avg_confidence']:.2f}

TOP SPEAKERS
{'-' * 80}
"""
    
    for speaker, count in sorted(stats['speaker_distribution'].items(), key=lambda x: -x[1])[:10]:
        report += f"  {speaker:40s} {count:5d} lines\n"
    
    report += f"\n{'=' * 80}\n"
    return report


def main():
    parser = argparse.ArgumentParser(
        description='ML-Enhanced Speaker Tagging for Parliament Transcripts'
    )
    parser.add_argument('input_file', help='Input transcript file')
    parser.add_argument('--output', '-o', help='Output file (default: input_tagged_ml.txt)')
    parser.add_argument('--context-window', '-c', type=int, default=20,
                        help='Context window for speaker continuation (default: 20)')
    parser.add_argument('--export-json', action='store_true',
                        help='Also export JSON format')
    parser.add_argument('--export-csv', action='store_true',
                        help='Also export CSV format')
    parser.add_argument('--report', '-r', help='Save report to file')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # Set output file
    if not args.output:
        input_path = Path(args.input_file)
        args.output = f"{input_path.stem}_tagged_ml.txt"
    
    # Load transcript
    print(f"Loading transcript: {args.input_file}")
    lines = load_transcript(args.input_file)
    print(f"✓ Loaded {len(lines)} lines")
    
    # Detect speakers
    print("\nDetecting speakers...")
    detector = SpeakerDetector()
    detections_df = detector.detect_all_speakers(lines)
    print(f"✓ Found {len(detections_df)} speaker mentions")
    
    if args.verbose and len(detections_df) > 0:
        print("\nTop speakers detected:")
        for speaker, count in detections_df['full_name'].value_counts().head(5).items():
            print(f"  {speaker}: {count} mentions")
    
    # Assign speakers
    print("\nAssigning speakers...")
    assigner = SpeakerAssigner(lines, detections_df)
    assignments = assigner.assign_speakers(context_window=args.context_window)
    print(f"✓ Assigned speakers to {len(assignments)} lines")
    
    # Get statistics
    stats = assigner.get_statistics()
    
    # Export
    print("\nExporting...")
    export_tagged(assignments, args.output, format='txt')
    print(f"✓ Exported text: {args.output}")
    
    if args.export_json:
        export_tagged(assignments, args.output, format='json')
        print(f"✓ Exported JSON: {Path(args.output).with_suffix('.json')}")
    
    if args.export_csv:
        export_tagged(assignments, args.output, format='csv')
        print(f"✓ Exported CSV: {Path(args.output).with_suffix('.csv')}")
    
    # Generate report
    report = generate_report(stats, args.output)
    print(report)
    
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ Report saved to {args.report}")
    
    # Summary
    coverage = stats['assigned_lines'] / stats['total_lines'] * 100
    if coverage > 80 and stats['avg_confidence'] > 0.7:
        print("✓ Good quality tagging!")
    elif coverage > 60:
        print("⚠ Moderate quality. Consider manual review of uncertain lines.")
    else:
        print("⚠ Low coverage. May need pattern adjustments or manual tagging.")


if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
Speaker Tagging Tool for Raw Transcripts

This script helps identify and tag speakers in raw text transcripts.
It provides multiple approaches:
1. Pattern-based detection (looking for common speaker indicators)
2. Interactive tagging interface
3. Export to tagged format
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter


class SpeakerTagger:
    def __init__(self, transcript_path: str):
        self.transcript_path = Path(transcript_path)
        self.lines = []
        self.speakers = {}
        self.tagged_lines = []
        
    def load_transcript(self):
        """Load the transcript file"""
        with open(self.transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Split by double newlines or periods followed by newlines
            # This helps identify potential speaker changes
            self.lines = [line.strip() for line in content.split('\n') if line.strip()]
        return self.lines
    
    def detect_speaker_patterns(self) -> Dict[str, List[str]]:
        """
        Detect potential speaker indicators in the text.
        Looks for patterns like:
        - "За. [Name] [title]" (Mongolian: "Well. [Name] [title]")
        - "[Name] гуай" (Mongolian honorific)
        - "[Title] [Name]"
        - Question patterns
        """
        patterns = {
            'speaker_introductions': [],
            'questions': [],
            'responses': [],
            'titles': []
        }
        
        # Common Mongolian titles and patterns
        title_patterns = [
            r'(Ерөнхий сайд|ерөнхий сайд)',
            r'(УИХ-ын дарга|УИХ-ын гишүүн)',
            r'(сайд|Сайд)',
            r'(шинжээч|Шинжээч)',
            r'(хянан шалгагч|Хянан шалгагч)',
            r'(гуай|Гуай)',
            r'(дарга|Дарга)',
        ]
        
        # Look for speaker introductions
        intro_pattern = r'(За\.|За,|За\s+)([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)*)\s+(гуай|Гуай|сайд|Сайд|дарга|Дарга)'
        
        for i, line in enumerate(self.lines):
            # Check for speaker introductions
            match = re.search(intro_pattern, line)
            if match:
                name = match.group(2)
                title = match.group(3)
                patterns['speaker_introductions'].append({
                    'line_num': i,
                    'name': name,
                    'title': title,
                    'context': line[:100]
                })
            
            # Check for questions (often indicate speaker change)
            if '?' in line or any(word in line for word in ['асууя', 'асуулт', 'хэлнэ үү']):
                patterns['questions'].append({
                    'line_num': i,
                    'text': line[:100]
                })
        
        return patterns
    
    def interactive_tagging(self):
        """
        Interactive mode for manually tagging speakers.
        Shows chunks of text and allows user to assign speakers.
        """
        print("=" * 80)
        print("Interactive Speaker Tagging")
        print("=" * 80)
        print("\nCommands:")
        print("  [name] - Assign speaker name")
        print("  s - Skip this segment")
        print("  u - Undo last assignment")
        print("  q - Quit and save")
        print("  ? - Show current speakers")
        print("=" * 80)
        
        chunk_size = 5  # Number of lines per chunk
        current_speaker = None
        speaker_counter = Counter()
        
        i = 0
        while i < len(self.lines):
            # Show chunk
            print(f"\n--- Lines {i+1}-{min(i+chunk_size, len(self.lines))} ---")
            for j in range(i, min(i + chunk_size, len(self.lines))):
                print(f"{j+1:4d}: {self.lines[j][:100]}")
            
            # Get user input
            user_input = input(f"\nSpeaker (current: {current_speaker or 'None'})? ").strip()
            
            if user_input.lower() == 'q':
                break
            elif user_input.lower() == 's':
                i += chunk_size
                continue
            elif user_input.lower() == 'u':
                if self.tagged_lines:
                    removed = self.tagged_lines.pop()
                    print(f"Removed: {removed}")
                continue
            elif user_input.lower() == '?':
                print("\nCurrent speakers:")
                for speaker, count in speaker_counter.most_common():
                    print(f"  {speaker}: {count} segments")
                continue
            elif user_input:
                current_speaker = user_input
                speaker_counter[current_speaker] += 1
            
            # Tag the chunk
            for j in range(i, min(i + chunk_size, len(self.lines))):
                self.tagged_lines.append({
                    'line_num': j + 1,
                    'speaker': current_speaker,
                    'text': self.lines[j]
                })
            
            i += chunk_size
        
        return self.tagged_lines
    
    def auto_tag_by_patterns(self, patterns: Dict) -> List[Dict]:
        """
        Attempt to automatically tag speakers based on detected patterns.
        This is a heuristic approach and may need manual correction.
        """
        tagged = []
        current_speaker = None
        
        for i, line in enumerate(self.lines):
            # Check if this line contains a speaker introduction
            intro_match = None
            for intro in patterns['speaker_introductions']:
                if intro['line_num'] == i:
                    intro_match = intro
                    break
            
            if intro_match:
                current_speaker = f"{intro_match['name']} {intro_match['title']}"
            
            tagged.append({
                'line_num': i + 1,
                'speaker': current_speaker or 'UNKNOWN',
                'text': line,
                'confidence': 'high' if current_speaker else 'low'
            })
        
        return tagged
    
    def export_tagged(self, output_path: str, format: str = 'txt'):
        """Export tagged transcript to file"""
        output_path = Path(output_path)
        
        if format == 'txt':
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in self.tagged_lines:
                    speaker = item.get('speaker', 'UNKNOWN')
                    text = item.get('text', '')
                    f.write(f"[{speaker}]: {text}\n")
        
        elif format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.tagged_lines, f, ensure_ascii=False, indent=2)
        
        elif format == 'srt':
            # Export as SRT subtitle format
            with open(output_path, 'w', encoding='utf-8') as f:
                subtitle_num = 1
                for item in self.tagged_lines:
                    speaker = item.get('speaker', 'UNKNOWN')
                    text = item.get('text', '')
                    f.write(f"{subtitle_num}\n")
                    f.write(f"00:00:00,000 --> 00:00:05,000\n")
                    f.write(f"{speaker}: {text}\n\n")
                    subtitle_num += 1
        
        print(f"Exported {len(self.tagged_lines)} tagged lines to {output_path}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tag_speakers.py <transcript_file> [output_file]")
        print("\nExample:")
        print("  python tag_speakers.py 12.7.txt 12.7_tagged.txt")
        sys.exit(1)
    
    transcript_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else transcript_file.replace('.txt', '_tagged.txt')
    
    tagger = SpeakerTagger(transcript_file)
    
    print(f"Loading transcript: {transcript_file}")
    tagger.load_transcript()
    print(f"Loaded {len(tagger.lines)} lines")
    
    # Detect patterns
    print("\nDetecting speaker patterns...")
    patterns = tagger.detect_speaker_patterns()
    print(f"Found {len(patterns['speaker_introductions'])} potential speaker introductions")
    print(f"Found {len(patterns['questions'])} potential questions")
    
    # Show some detected patterns
    if patterns['speaker_introductions']:
        print("\nSample speaker introductions found:")
        for intro in patterns['speaker_introductions'][:5]:
            print(f"  Line {intro['line_num']}: {intro['name']} {intro['title']}")
    
    # Ask user what to do
    print("\n" + "=" * 80)
    print("Choose tagging method:")
    print("  1. Interactive tagging (recommended for accuracy)")
    print("  2. Auto-tag based on patterns (faster, less accurate)")
    print("  3. Show patterns only (no tagging)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        tagger.interactive_tagging()
        tagger.export_tagged(output_file, format='txt')
        tagger.export_tagged(output_file.replace('.txt', '.json'), format='json')
    
    elif choice == '2':
        tagged = tagger.auto_tag_by_patterns(patterns)
        tagger.tagged_lines = tagged
        tagger.export_tagged(output_file, format='txt')
        print("\nNote: Auto-tagging may have errors. Please review and correct manually.")
    
    elif choice == '3':
        print("\nDetected patterns:")
        print(json.dumps(patterns, ensure_ascii=False, indent=2))
    
    else:
        print("Invalid choice")


if __name__ == '__main__':
    main()


#!/usr/bin/env python3

import os
import re
import argparse
from pathlib import Path

def process_markdown_file(file_path):
    """Process a single markdown file to ensure proper spacing before lists."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        processed_lines = []
        for i, line in enumerate(lines):
            current_line = line.strip()
            
            # Check if line is a numbered list item with bold text
            is_numbered_bold = bool(re.match(r'^\d+\.\s+\*\*.*\*\*', current_line))
            if is_numbered_bold:
                line = '#### ' + line
            
            # Check if current line starts a list
            is_list_start = bool(re.match(r'^(\d+\.|[-*])\s', current_line))
            
            # Check if previous line was part of a list
            prev_was_list = False
            if i > 0:
                prev_was_list = bool(re.match(r'^(\d+\.|[-*])\s', lines[i-1].strip()))
            
            # Add newline if this is list start and previous line wasn't empty or a list
            if is_list_start and i > 0 and not prev_was_list and lines[i-1].strip():
                processed_lines.append('\n')
            
            processed_lines.append(line)
        
        # Join lines and clean up multiple consecutive newlines
        content = ''.join(processed_lines)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Preprocess Markdown files to ensure proper spacing before lists.')
    parser.add_argument('--content-dir', type=str, default='Site/content/',
                       help='Path to content directory (default: content/)')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode with only specific test file')
    args = parser.parse_args()

    # Ensure content directory exists
    content_dir = Path(args.content_dir)
    if not content_dir.exists():
        print(f"Error: Content directory '{content_dir}' does not exist")
        return

    # Whitelist for testing
    whitelist = ['Site/content/blog/dangers-of-physicalism.md']
    
    # Track statistics
    processed_files = 0
    successful_files = 0

    # Walk through all files in content directory
    for file_path in content_dir.rglob('*.md'):
        if args.test and str(file_path) not in whitelist:
            continue
            
        print(f"Processing: {file_path}")
        if process_markdown_file(file_path):
            successful_files += 1
        processed_files += 1

    # Print summary
    print("\nProcessing complete!")
    print(f"Files processed: {processed_files}")
    print(f"Successfully processed: {successful_files}")
    if processed_files != successful_files:
        print(f"Failed: {processed_files - successful_files}")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Entry point script for PDF Exercise Extractor.
This script allows command-line usage of the PDF exercise extraction tool.
"""
import argparse
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_extractor.main import PDFExerciseExtractor
from pdf_extractor.config.settings import ExtractionConfig


def main():
    parser = argparse.ArgumentParser(
        description="Extract 'Sample Exercise' sections from PDF textbooks"
    )
    parser.add_argument(
        "input_pdf", 
        help="Path to the input PDF file"
    )
    parser.add_argument(
        "-o", "--output", 
        default="sample_exercises_extracted.pdf",
        help="Path for the output PDF file (default: sample_exercises_extracted.pdf)"
    )
    parser.add_argument(
        "--preview", 
        action="store_true",
        help="Enable preview mode with visual indicators"
    )
    parser.add_argument(
        "--no-progress", 
        action="store_true",
        help="Disable progress indicators"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_pdf):
        print(f"Error: Input file '{args.input_pdf}' does not exist.")
        sys.exit(1)
    
    try:
        # Create configuration
        config = ExtractionConfig(
            preview_mode=args.preview,
            show_progress=not args.no_progress
        )
        
        # Create extractor and run extraction
        extractor = PDFExerciseExtractor(config)
        
        print(f"Extracting 'Sample Exercise' sections from '{args.input_pdf}'...")
        sections_extracted = extractor.extract_exercises(args.input_pdf, args.output)
        
        print(f"Successfully extracted {sections_extracted} exercise sections to '{args.output}'")
        
        # Additional logging
        if sections_extracted == 0:
            print("Warning: No exercise sections were found in the PDF.")
        else:
            print(f"Extraction completed successfully with {sections_extracted} sections.")
            
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
# PDF Exercise Extractor

A Python tool for extracting "Sample Exercise" sections from educational PDFs while preserving vector graphics, text, and layout.

## Overview

This project automatically identifies and extracts "Sample Exercise" sections from educational textbooks. It maintains the original layout, including vector graphics, text formatting, and background elements, making it ideal for creating focused study materials from large textbooks.

Based on the analysis of textbook patterns, the tool recognizes the consistent structure of exercise sections:
- Green gradient header box with "Sample Exercise X.Y" title
- Consistent layout: Problem statement → SOLUTION → Analyze/Plan/Solve → Comment → Practice Exercise
- Fixed boundaries with distinctive visual elements

## Features

- Extract "Sample Exercise" sections using pattern recognition
- Preserve original vector graphics, text formatting, and backgrounds
- Maintain text selection capabilities in output PDFs
- Configurable settings for extraction parameters
- Progress tracking and validation

## Requirements

- Python 3.7+
- PyMuPDF library

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```python
from src.pdf_extractor.main import PDFExerciseExtractor
from src.pdf_extractor.config.settings import ExtractionConfig

# Initialize extractor with default or custom configuration
config = ExtractionConfig()
extractor = PDFExerciseExtractor(config)

# Extract exercises from your PDF
input_pdf = "path/to/your/textbook.pdf"
output_pdf = "sample_exercises_extracted.pdf"
sections_extracted = extractor.extract_exercises(input_pdf, output_pdf)

print(f"Extracted {sections_extracted} exercise sections")
```

## Configuration

The `ExtractionConfig` class allows customization of:

- Pattern regex for detecting exercise sections
- Page margins and header spacing
- Output compression settings
- Preview and progress modes

## Project Structure

```
pdf_exerise_croppy/
├── src/
│   └── pdf_extractor/
│       ├── __init__.py
│       ├── main.py              # Core extraction logic
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py       # Configuration classes
│       └── utils/
│           ├── __init__.py
│           └── bbox_operations.py # Utility functions
├── requirements.txt             # Project dependencies
├── README.md                   # This file
└── main.py                     # Entry point script
```

## How It Works

1. The tool scans each page for the pattern "Sample Exercise [number].[number]"
2. It identifies the header bounding box and calculates the full section boundaries
3. Using PyMuPDF's `show_pdf_page()` with a clip parameter, it preserves the exact layout
4. Each exercise section is placed on a new page in the output PDF

The extraction maintains all original elements: vector graphics, text formatting, background colors, and mathematical formulas.

## Performance

The tool is designed to process 600+ page textbooks efficiently, with extraction times typically under 5 minutes depending on the source PDF complexity.
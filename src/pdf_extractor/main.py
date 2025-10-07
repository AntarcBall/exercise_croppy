"""
Main module for extracting 'Sample Exercise' sections from PDFs.
This module contains the core logic for finding, extracting, and saving
specific sections from educational PDFs.
"""
import fitz  # PyMuPDF
import re
from typing import List, Tuple, Optional
from tqdm import tqdm
from .utils.bbox_operations import calculate_section_bounds, calculate_multiline_section_bounds
from .config.settings import ExtractionConfig


class PDFExerciseExtractor:
    """
    A class to extract 'Sample Exercise' sections from PDF files.
    """
    
    def __init__(self, config: Optional[ExtractionConfig] = None):
        """
        Initialize the extractor with optional configuration.
        
        Args:
            config: Configuration object with extraction parameters
        """
        self.config = config or ExtractionConfig()
        # Store the pattern string for use with PyMuPDF's search_for
        # However, PyMuPDF search_for doesn't support complex regex patterns
        # So we'll use a simpler search approach
        self.base_search_str = "Sample Exercise"
        # Also keep the compiled version for proper regex matching and other uses
        self.pattern_compiled = re.compile(
            self.config.pattern_regex, 
            re.IGNORECASE
        )
        # And keep the original pattern string for bbox operations
        self.pattern_str = self.config.pattern_regex
    
    def extract_exercises(self, input_pdf_path: str, output_pdf_path: str) -> int:
        """
        Extract all 'Sample Exercise' sections from the input PDF and save to output PDF.
        
        Args:
            input_pdf_path: Path to the input PDF file
            output_pdf_path: Path to save the extracted exercises PDF
            
        Returns:
            Number of sections extracted
        """
        # Open the input PDF
        input_doc = fitz.open(input_pdf_path)
        output_doc = fitz.open()
        
        # Track extracted sections
        extracted_count = 0
        
        # Create progress bar if enabled in config
        pbar = tqdm(
            range(len(input_doc)), 
            desc="Processing PDF pages", 
            disable=not self.config.show_progress
        ) if self.config.show_progress else range(len(input_doc))
        
        # For each page in the input PDF
        for page_num in pbar:
            page = input_doc[page_num]
            
            # Search for "Sample Exercise" patterns on the page
            exercise_bboxes = self._find_exercise_headers(page)
            
            # For each found exercise header, extract the section
            for header_bbox in exercise_bboxes:
                # First, try to determine if this is a multi-page section
                multi_result = calculate_multiline_section_bounds(
                    page, 
                    header_bbox, 
                    input_doc, 
                    page_num,
                    self.pattern_str,
                    self.config.max_pages_to_search
                )
                
                if multi_result:
                    # This is a multi-page section
                    overall_bbox, page_bounds = multi_result
                    
                    # For multi-page sections, we'll add each page of the section separately
                    # This way, we preserve the content across pages properly
                    for current_page_num, current_page_bbox in page_bounds:
                        current_page = input_doc[current_page_num]
                        
                        # Create a new page in the output document
                        new_page = output_doc.new_page(-1)
                        
                        # Copy the specific area of the current page to the new page
                        new_page.show_pdf_page(
                            new_page.rect,  # Full page in output
                            input_doc,      # Source document
                            current_page_num,  # Source page
                            clip=current_page_bbox  # Only the relevant area
                        )
                        
                        # If in preview mode, add visual indicators
                        if self.config.preview_mode:
                            from .utils.bbox_operations import add_preview_overlay
                            add_preview_overlay(new_page, current_page_bbox, f"Ex {extracted_count + 1}-P{current_page_num+1}")
                    
                    # Since this multi-page section counts as a single exercise,
                    # we increment the count after processing all pages of this exercise
                    extracted_count += 1
                else:
                    # Handle single-page sections
                    section_bbox = calculate_section_bounds(
                        page, 
                        header_bbox, 
                        input_doc, 
                        page_num,
                        self.pattern_str
                    )
                    
                    # If a valid section was found, add it to output
                    if section_bbox:
                        # Create a new page in the output document
                        new_page = output_doc.new_page(-1)
                        
                        # Copy the section to the new page using clip
                        new_page.show_pdf_page(
                            new_page.rect,  # Full page
                            input_doc,      # Source document
                            page_num,       # Source page
                            clip=section_bbox  # Only this area
                        )
                        
                        # If in preview mode, add visual indicators
                        if self.config.preview_mode:
                            from .utils.bbox_operations import add_preview_overlay
                            add_preview_overlay(new_page, section_bbox, f"Ex {extracted_count + 1}")
                        
                        extracted_count += 1
        
        # Update progress bar description with results
        if hasattr(pbar, 'set_description'):
            pbar.set_description(f"Completed - Extracted {extracted_count} exercises")
        
        # Close progress bar if it exists
        if hasattr(pbar, 'close') and self.config.show_progress:
            pbar.close()
        
        # Save and close documents
        output_doc.save(
            output_pdf_path, 
            garbage=self.config.garbage_collect, 
            deflate=self.config.deflate_output
        )
        output_doc.close()
        input_doc.close()
        
        return extracted_count
    
    def _find_exercise_headers(self, page) -> List[fitz.Rect]:
        """
        Find all 'Sample Exercise' headers on a given page.
        
        Args:
            page: The PDF page object to search
            
        Returns:
            List of bounding boxes for found headers
        """
        headers = []
        
        # Search for the base string "Sample Exercise" using PyMuPDF's search
        text_instances = page.search_for(self.base_search_str)
        
        # Extract the full text from the page with position information
        # to properly match our regex pattern
        page_text_dict = page.get_text("dict")
        
        # For each found instance, we'll check if it matches our expected pattern
        for inst in text_instances:
            # Get the text near this instance to check if it matches our full regex
            # Extract text from the page with position information
            inst_text = None
            
            for block in page_text_dict.get("blocks", []):
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            span_bbox = fitz.Rect(span["bbox"])
                            
                            # If the span bbox intersects with our target instance
                            if span_bbox.intersects(inst):
                                # Get more context around the instance
                                full_page_text = page.get_text()
                                
                                # Search for our full pattern in the text
                                matches = self.pattern_compiled.findall(full_page_text)
                                if matches:
                                    # Now we need to map back to the actual positions
                                    # A better approach: search in the page text and match positions
                                    for match in self.pattern_compiled.finditer(full_page_text):
                                        matched_text = match.group(0)
                                        
                                        # Search for this matched text in the page to get its position
                                        possible_instances = page.search_for(matched_text)
                                        for possible_inst in possible_instances:
                                            # Check if this possible instance is in the right area
                                            # and check if it's a proper header
                                            if self._is_header_format(page, possible_inst):
                                                # Avoid duplicates by checking if this is close to our original instance
                                                if (abs(possible_inst.x0 - inst.x0) < 50 and 
                                                    abs(possible_inst.y0 - inst.y0) < 20):
                                                    if possible_inst not in headers:
                                                        headers.append(possible_inst)
        
        # Alternative approach: Get all text and search for full pattern, then map to positions
        if not headers:
            # Get all text from the page
            full_text = page.get_text()
            
            # Find all matches using our regex
            matches = list(self.pattern_compiled.finditer(full_text))
            
            for match in matches:
                matched_text = match.group(0)
                
                # Find the position of this text in the page
                # Search for this specific text to get its bounding box
                text_positions = page.search_for(matched_text)
                
                for pos in text_positions:
                    if self._is_header_format(page, pos):
                        if pos not in headers:
                            headers.append(pos)
        
        return headers

    def _is_header_format(self, page, bbox: fitz.Rect) -> bool:
        """
        Determine if a text instance is formatted as a header based on font properties.
        
        Args:
            page: The PDF page object
            bbox: Bounding box of the text instance
            
        Returns:
            True if the text instance appears to be a header, False otherwise
        """
        # Get all text spans from the page
        page_dict = page.get_text("dict")
        
        for block in page_dict.get("blocks", []):
            if "lines" in block:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        span_bbox = fitz.Rect(span["bbox"])
                        
                        # If the span bbox intersects with our target
                        if span_bbox.intersects(bbox):
                            # Check if font size is large enough to be a header
                            if span["size"] >= self.config.min_font_size:
                                # Check if it's bold (flags bit 3 is for bold)
                                if span["flags"] & 2**3:  # Bold text
                                    return True
                                
                                # Check if font name contains "Bold" or similar indicators
                                if any(bold_indicator in span["font"].lower() for bold_indicator in ["bold", "black"]):
                                    return True
                                
                                # If it's larger than minimum threshold, consider it a header
                                if span["size"] > self.config.min_font_size:
                                    return True

        # Additional heuristic: check if the text is at the top of the page
        page_height = page.rect.height
        if bbox.y0 < page_height * self.config.header_detection_threshold:
            # If the text is in the top portion of the page and matches our pattern,
            # it's likely a header rather than inline text
            return True

        return False
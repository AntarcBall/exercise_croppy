"""
Utility functions module for PDF Exercise Extractor.
Contains helper functions for bounding box operations and other utilities.
"""
import fitz  # PyMuPDF
from typing import Optional, List, Tuple


def calculate_section_bounds(
    page, 
    header_bbox: fitz.Rect, 
    doc, 
    page_num: int,
    pattern
) -> Optional[fitz.Rect]:
    """
    Calculate the bounding box for an entire exercise section.
    Handles sections that span multiple pages.
    
    Args:
        page: The PDF page object containing the header
        header_bbox: Bounding box of the exercise header
        doc: The PDF document object
        page_num: The page number of the current page
        pattern: Regex pattern for finding exercise headers
        
    Returns:
        Bounding box for the entire exercise section, or None if not found
    """
    # Start with the header's bounding box
    section_top = header_bbox.y0
    
    # Look for the next exercise header to determine the end of this section
    next_exercise_bbox = None
    next_exercise_page = None
    
    # First, check if there are more exercise headers on the same page
    remaining_text_instances = []
    all_instances = page.search_for(pattern)
    
    for inst in all_instances:
        # Only consider instances that appear after our header
        if inst.y0 > header_bbox.y1:
            remaining_text_instances.append(inst)
    
    if remaining_text_instances:
        # If there are more exercise headers on this page, 
        # use the first one as the end of our section
        next_exercise_bbox = min(remaining_text_instances, key=lambda x: x.y0)
        section_bottom = next_exercise_bbox.y0
        section_right = next_exercise_bbox.x1
    else:
        # If no more exercises on this page, check subsequent pages
        found_on_next_page = False
        for next_page_num in range(page_num + 1, len(doc)):
            next_page = doc[next_page_num]
            next_page_instances = next_page.search_for(pattern)
            
            if next_page_instances:
                # Found the next exercise on a subsequent page
                next_exercise_bbox = min(next_page_instances, key=lambda x: x.y0)
                next_exercise_page = next_page_num
                section_bottom = next_exercise_bbox.y0
                section_right = next_exercise_bbox.x1
                found_on_next_page = True
                break
        
        if not found_on_next_page:
            # No more exercises found, go to the bottom of the current page
            # Or if the current page has content continuing beyond the header
            section_bottom = page.rect.height
            # Check if there's any content after the header that might be part of the exercise
            page_words = page.get_text("words")
            max_bottom = header_bbox.y1
            for word_info in page_words:
                word_bbox = fitz.Rect(word_info[0], word_info[1], word_info[2], word_info[3])
                # Consider words that appear after the header
                if word_bbox.y0 > header_bbox.y1:
                    max_bottom = max(max_bottom, word_bbox.y1)
            
            if max_bottom > header_bbox.y1:
                section_bottom = max_bottom + 20  # Add a little margin
        
    # Create the final section bounding box
    # Use the full page width to ensure we capture all content
    section_bbox = fitz.Rect(
        page.rect.x0,  # Use left edge of page
        section_top,
        page.rect.x1,  # Use right edge of page
        section_bottom
    )
    
    # If the section spans multiple pages, we need special handling
    # For now, we return the bounds on the initial page, 
    # but in a full implementation we would handle multi-page sections differently
    return section_bbox


def calculate_multiline_section_bounds(
    start_page, 
    header_bbox: fitz.Rect, 
    doc, 
    start_page_num: int,
    pattern,
    max_pages_to_search: int = 10  # Limit pages to search to prevent infinite loops
) -> Optional[Tuple[fitz.Rect, List[Tuple[int, fitz.Rect]]]]:
    """
    Calculate bounds for sections that span multiple pages.
    
    Args:
        start_page: The PDF page object containing the header
        header_bbox: Bounding box of the exercise header
        doc: The PDF document object
        start_page_num: The page number of the starting page
        pattern: Regex pattern for finding exercise headers
        max_pages_to_search: Maximum number of pages to search for section end
        
    Returns:
        Tuple of (overall bounding box, list of (page_num, page_bbox) tuples) or None if not found
    """
    from typing import List, Tuple
    
    page_bounds = []
    
    # Look through pages to find where this section ends
    for current_page_num in range(start_page_num, min(len(doc), start_page_num + max_pages_to_search)):
        current_page = doc[current_page_num]
        
        # If this is the starting page, start from the header position
        if current_page_num == start_page_num:
            current_top = header_bbox.y0
        else:
            # On subsequent pages, start from the top
            current_top = 0  # Start from the top of the page
        
        # Check for the next exercise header on this page
        current_page_instances = current_page.search_for(pattern)
        
        # Filter for instances that come after the header if it's the start page
        relevant_instances = []
        for inst in current_page_instances:
            if current_page_num == start_page_num:
                # On start page, only consider instances after our header
                if inst.y0 > header_bbox.y1:
                    relevant_instances.append(inst)
            else:
                # On other pages, all instances are relevant
                relevant_instances.append(inst)
        
        if relevant_instances:
            # Found the next exercise header, so this section ends here
            first_next_header = min(relevant_instances, key=lambda x: x.y0)
            
            # Define bounds for this page of the section
            current_page_bbox = fitz.Rect(
                current_page.rect.x0,  # Left edge
                current_top,           # Top (header position on first page, 0 on subsequent pages)
                current_page.rect.x1,  # Right edge
                first_next_header.y0   # Bottom (where next exercise starts)
            )
            
            page_bounds.append((current_page_num, current_page_bbox))
            
            # We found where this section ends
            break
        else:
            # No next exercise on this page, include the page content
            # Only include content that's relevant to the exercise (starting from the header position on first page)
            current_page_bbox = fitz.Rect(
                current_page.rect.x0,          # Left edge
                current_top,                   # Top (header position on first page, 0 on subsequent pages)
                current_page.rect.x1,          # Right edge
                current_page.rect.height       # Bottom of the page
            )
            
            page_bounds.append((current_page_num, current_page_bbox))
    
    if page_bounds:
        # Calculate the overall bounding box across all pages
        # For display purposes, since we're processing multi-page content separately,
        # we'll return the first page's effective bbox as the overall one
        first_page_num, first_bbox = page_bounds[0]
        last_page_num, last_bbox = page_bounds[-1]
        
        # Calculate overall bottom based on how many pages and positions
        # This is simplified since we're handling multi-page sections by adding separate pages
        overall_bbox = fitz.Rect(
            start_page.rect.x0,
            header_bbox.y0,  # Start from the header position
            start_page.rect.x1,
            last_bbox.y1     # End where the last page in the section ends
        )
        
        return overall_bbox, page_bounds
    
    return None


def add_preview_overlay(page, bbox: fitz.Rect, label: str = ""):
    """
    Add a preview overlay to a bounding box for visualization.
    
    Args:
        page: The PDF page to add overlay to
        bbox: The bounding box to highlight
        label: Optional label to add to the overlay
    """
    # Create a red rectangle to highlight the extracted area
    page.draw_rect(bbox, color=(1, 0, 0), width=2)
    
    # Optionally add a label
    if label:
        page.insert_text(
            fitz.Point(bbox.x0, bbox.y0 - 5),
            label,
            fontsize=12,
            color=(1, 0, 0)
        )
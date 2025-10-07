"""
Configuration module for PDF Exercise Extractor.
Contains settings and configuration classes for the extraction process.
"""


class ExtractionConfig:
    """
    Configuration class for PDF exercise extraction parameters.
    """
    
    def __init__(
        self,
        pattern_regex: str = r"Sample\s*Exercise\s+\d+\.\d+",  # Updated to handle line breaks
        header_margin: int = 10,
        page_margin: int = 30,
        garbage_collect: int = 3,
        deflate_output: bool = True,
        preview_mode: bool = False,
        show_progress: bool = True,
        min_font_size: float = 10.0,  # Minimum font size considered for headers
        max_pages_to_search: int = 10,  # Max pages to search for section end
        header_detection_threshold: float = 0.3  # Threshold for header detection (0.0-1.0)
    ):
        """
        Initialize extraction configuration.
        
        Args:
            pattern_regex: Regex pattern to identify exercise sections
            header_margin: Additional margin around header bounding boxes
            page_margin: Page margin for section extraction
            garbage_collect: Garbage collection level for output PDF
            deflate_output: Whether to compress output PDF
            preview_mode: Whether to include preview features
            show_progress: Whether to show progress indicators
            min_font_size: Minimum font size to consider as potential header
            max_pages_to_search: Max pages to search when finding section end
            header_detection_threshold: Position threshold for header detection (0.0-1.0)
        """
        self.pattern_regex = pattern_regex
        self.header_margin = header_margin
        self.page_margin = page_margin
        self.garbage_collect = garbage_collect
        self.deflate_output = deflate_output
        self.preview_mode = preview_mode
        self.show_progress = show_progress
        self.min_font_size = min_font_size
        self.max_pages_to_search = max_pages_to_search
        self.header_detection_threshold = header_detection_threshold
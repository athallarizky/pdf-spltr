"""Core PDF splitting logic."""

import os
from pathlib import Path
from typing import Optional

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError, PyPdfError


class PDFSplitterError(Exception):
    """Base exception for PDF splitting errors."""

    pass


class PDFValidationError(PDFSplitterError):
    """Raised when PDF input validation fails."""

    pass


class PDFSplitter:
    """Handles PDF file splitting into smaller chunks.

    This class provides methods to validate input PDF files and split them
    into multiple smaller PDF files based on a specified chunk size.
    """

    def __init__(self, input_path: str | Path, chunk_size: int, output_dir: Optional[str | Path] = None):
        """Initialize the PDF splitter.

        Args:
            input_path: Path to the input PDF file.
            chunk_size: Number of pages per output file.
            output_dir: Optional directory for output files. Defaults to input file's directory.

        Raises:
            PDFValidationError: If initial validation fails.
        """
        self.input_path = Path(input_path).resolve()
        self.chunk_size = chunk_size
        self.output_dir = Path(output_dir).resolve() if output_dir else self.input_path.parent
        self._reader: Optional[PdfReader] = None

        self._validate_inputs()

    @property
    def reader(self) -> PdfReader:
        """Lazy-load and return the PDF reader.

        Returns:
            PdfReader instance for the input file.

        Raises:
            PDFValidationError: If the file cannot be read as a valid PDF.
        """
        if self._reader is None:
            try:
                self._reader = PdfReader(str(self.input_path))
            except (PdfReadError, PyPdfError) as e:
                raise PDFValidationError(f"Invalid PDF file: {e}") from e
        return self._reader

    @property
    def total_pages(self) -> int:
        """Get the total number of pages in the PDF.

        Returns:
            Total page count.
        """
        return len(self.reader.pages)

    def _validate_inputs(self) -> None:
        """Validate all input parameters.

        Raises:
            PDFValidationError: If any validation fails.
        """
        # Check if input file exists
        if not self.input_path.exists():
            raise PDFValidationError(f"Input file does not exist: {self.input_path}")

        # Check if input is a file (not a directory)
        if not self.input_path.is_file():
            raise PDFValidationError(f"Input path is not a file: {self.input_path}")

        # Validate chunk size
        if self.chunk_size <= 0:
            raise PDFValidationError(f"Chunk size must be a positive integer, got: {self.chunk_size}")

        # Create output directory if it doesn't exist
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise PDFValidationError(f"Cannot create output directory: {e}") from e

        # Verify output directory is writable
        if not os.access(self.output_dir, os.W_OK):
            raise PDFValidationError(f"Output directory is not writable: {self.output_dir}")

    def _generate_output_filename(self, part_number: int) -> Path:
        """Generate output filename for a specific part.

        Args:
            part_number: The part number (1-indexed).

        Returns:
            Full path for the output file.
        """
        stem = self.input_path.stem
        return self.output_dir / f"{stem}_part_{part_number}.pdf"

    def split(self, progress_callback=None) -> list[Path]:
        """Split the PDF into multiple smaller PDFs.

        Args:
            progress_callback: Optional callback function(current_page, total_pages).

        Returns:
            List of paths to the generated output files.

        Raises:
            PDFSplitterError: If splitting fails.
        """
        output_files = []
        total_pages = self.total_pages
        part_number = 1
        start_page = 0

        try:
            while start_page < total_pages:
                end_page = min(start_page + self.chunk_size, total_pages)
                output_path = self._generate_output_filename(part_number)

                writer = PdfWriter()

                for page_num in range(start_page, end_page):
                    page = self.reader.pages[page_num]
                    writer.add_page(page)

                    if progress_callback:
                        progress_callback(page_num + 1, total_pages)

                with open(output_path, "wb") as f:
                    writer.write(f)

                output_files.append(output_path)
                start_page = end_page
                part_number += 1

            return output_files

        except (OSError, PyPdfError) as e:
            raise PDFSplitterError(f"Failed to split PDF: {e}") from e

    def get_split_info(self) -> dict:
        """Get information about the pending split operation.

        Returns:
            Dictionary containing split information including number of parts,
            total pages, and output directory.
        """
        total_pages = self.total_pages
        num_parts = (total_pages + self.chunk_size - 1) // self.chunk_size

        return {
            "total_pages": total_pages,
            "chunk_size": self.chunk_size,
            "num_parts": num_parts,
            "output_directory": str(self.output_dir),
            "input_file": str(self.input_path),
        }

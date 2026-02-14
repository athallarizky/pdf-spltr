"""Command-line interface for PDF Splitter."""

import argparse
import sys
from pathlib import Path

from .splitter import PDFSplitter, PDFSplitterError, PDFValidationError


class ProgressIndicator:
    """Displays progress information in the terminal."""

    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, total: int, width: int = 50, show_spinner: bool = True):
        """Initialize the progress indicator.

        Args:
            total: Total number of items to process.
            width: Width of the progress bar in characters.
            show_spinner: Whether to show animated spinner.
        """
        self.total = total
        self.width = width
        self.show_spinner = show_spinner
        self.current = 0
        self.spinner_index = 0
        self.last_update_len = 0

    def update(self, current: int) -> None:
        """Update the progress display.

        Args:
            current: Current progress value.
        """
        self.current = current
        self._display()

    def _display(self) -> None:
        """Render the progress bar to stdout."""
        if self.total == 0:
            return

        filled = int(self.width * self.current / self.total)
        bar = "█" * filled + "░" * (self.width - filled)
        percent = (self.current / self.total) * 100

        spinner = ""
        if self.show_spinner:
            spinner = f" {self.SPINNER_FRAMES[self.spinner_index % len(self.SPINNER_FRAMES)]}"
            self.spinner_index += 1

        line = f"\r[{bar}] {percent:5.1f}% ({self.current}/{self.total}){spinner}"
        self.last_update_len = len(line)

        # Clear any previous output that might be longer
        sys.stdout.write(" " * (self.last_update_len + 5) + "\r")
        sys.stdout.write(line)
        sys.stdout.flush()

    def finish(self) -> None:
        """Complete the progress display with a final update."""
        self._display()
        sys.stdout.write("\n")
        sys.stdout.flush()


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="pdf-splitter",
        description="Split a PDF file into multiple smaller PDFs based on page count.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf 50
      Split document.pdf into 50-page chunks in the same directory.

  %(prog)s document.pdf 100 -o ./output
      Split document.pdf into 100-page chunks in the ./output directory.

  %(prog)s "large file.pdf" 25 --output-dir /tmp/splits
      Split with spaces in filename and custom output directory.
        """,
    )

    parser.add_argument(
        "input",
        type=str,
        help="Path to the input PDF file",
    )

    parser.add_argument(
        "chunk_size",
        type=int,
        help="Number of pages per output file (must be positive)",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        dest="output_dir",
        help="Directory for output files (default: same as input file)",
    )

    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar display",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    return parser.parse_args()


def print_split_info(info: dict) -> None:
    """Display information about the split operation.

    Args:
        info: Dictionary containing split operation details.
    """
    print("\n" + "=" * 60)
    print("PDF Splitter - Split Information")
    print("=" * 60)
    print(f"  Input file:    {info['input_file']}")
    print(f"  Total pages:   {info['total_pages']}")
    print(f"  Chunk size:    {info['chunk_size']}")
    print(f"  Output parts:  {info['num_parts']}")
    print(f"  Output dir:    {info['output_directory']}")
    print("=" * 60 + "\n")


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    args = parse_arguments()

    try:
        # Initialize the splitter
        splitter = PDFSplitter(
            input_path=args.input,
            chunk_size=args.chunk_size,
            output_dir=args.output_dir,
        )

        # Display split information
        info = splitter.get_split_info()
        print_split_info(info)

        # Set up progress tracking
        progress = ProgressIndicator(info["total_pages"], show_spinner=not args.no_progress)

        def progress_callback(current: int, total: int) -> None:
            progress.update(current)

        # Perform the split
        print("Splitting PDF...")
        output_files = splitter.split(progress_callback=progress_callback)
        progress.finish()

        # Display results
        print(f"\nSuccessfully created {len(output_files)} file(s):")
        for i, path in enumerate(output_files, 1):
            size_kb = path.stat().st_size / 1024
            print(f"  {i}. {path.name} ({size_kb:.1f} KB)")

        return 0

    except PDFValidationError as e:
        print(f"\n❌ Validation Error: {e}", file=sys.stderr)
        return 1

    except PDFSplitterError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

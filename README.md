# PDF Splitter 📄✂️

A handy CLI tool that chops up big PDFs into smaller pieces. Great for when you've got a massive document and need to break it down into manageable chunks.

## What it does

- Handles large PDFs (1000+ pages) without eating up all your RAM
- Validates everything before it starts (file exists, valid PDF, etc.)
- Shows a nice progress bar so you know what's happening
- Names files automatically: `filename_part_1.pdf`, `filename_part_2.pdf`, etc.
- Gives you clear error messages when something goes wrong

## What you need

- Python 3.10+
- pypdf library

## Setup

### Quick setup with venv (recommended)

```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux

# Install the dependencies
pip install -r requirements.txt
```

That's it! You're ready to go.

## How to use

### Basic syntax

```bash
source venv/bin/activate  # Don't forget to activate venv first!
python -m pdf_splitter <input.pdf> <chunk_size> [options]
```

### What the arguments mean

| Argument | What it does |
|----------|---------------|
| `input` | Your PDF file path |
| `chunk_size` | How many pages per split file |

### Options

| Flag | Short | What it does |
|------|-------|---------------|
| `--output-dir` | `-o` | Where to save the splits (default: same folder) |
| `--no-progress` | | Turn off the progress bar |
| `--help` | `-h` | Show help |
| `--version` | `-V` | Show version |

### Examples

```bash
# Split into 50-page chunks
python -m pdf_splitter document.pdf 50

# Split into 100-page chunks, save to specific folder
python -m pdf_splitter document.pdf 100 -o ./output

# File has spaces? Use quotes
python -m pdf_splitter "my ebook.pdf" 25

# No progress bar (for scripts)
python -m pdf_splitter report.pdf 75 --no-progress
```

## What you get

<img width="1104" height="581" alt="image" src="https://github.com/user-attachments/assets/d736b4e8-fe7d-4c95-8145-4237ac25efca" />

Your files get named automatically:

```
input.pdf
├── input_part_1.pdf  (pages 1-50)
├── input_part_2.pdf  (pages 51-100)
└── input_part_3.pdf  (pages 101-120)
```

## Sample output

```
============================================================
PDF Splitter - Split Information
============================================================
  Input file:    /path/to/document.pdf
  Total pages:   250
  Chunk size:    50
  Output parts:  5
  Output dir:    /path/to/output
============================================================

Splitting PDF...
[██████████████████████████████████████████████████] 100.0% (250/250)

Successfully created 5 file(s):
  1. document_part_1.pdf (245.3 KB)
  2. document_part_2.pdf (238.7 KB)
  3. document_part_3.pdf (251.1 KB)
  4. document_part_4.pdf (244.9 KB)
  5. document_part_5.pdf (98.2 KB)
```

## Common errors

If something goes wrong, you'll get a clear message:

```
❌ Validation Error: Input file does not exist: missing.pdf
❌ Validation Error: Invalid PDF file: not_a_pdf.txt
❌ Validation Error: Chunk size must be a positive integer, got: -5
```

## Using as a Python module

Want to use it inside your Python code? Sure thing:

```python
from pdf_splitter.splitter import PDFSplitter

splitter = PDFSplitter("document.pdf", chunk_size=50, output_dir="./output")
output_files = splitter.split()
print(f"Created {len(output_files)} files")
```

## Project structure

```
pdf-splitter/
├── pdf_splitter/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── main.py
│   └── splitter.py
├── requirements.txt
└── README.md
```

## License

MIT

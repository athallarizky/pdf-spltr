.PHONY: help install test clean run

help:
	@echo "Available targets:"
	@echo "  make install   - Install the package and dependencies"
	@echo "  make test      - Run tests"
	@echo "  make clean     - Remove build artifacts"
	@echo "  make run       - Run with example: ARGS='input.pdf 50'"

install:
	pip install -e .

test:
	python -m pdf_splitter --help

clean:
	rm -rf build/ dist/ *.egg-info __pycache__ pdf_splitter/__pycache__

run:
	python -m pdf_splitter $(ARGS)

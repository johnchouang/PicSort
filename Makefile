# Makefile for PicSort project
# Provides convenient commands for development and building

.PHONY: help install install-dev test test-unit test-integration test-performance clean build build-debug build-clean lint format

# Default target
help:
	@echo "PicSort Development Commands"
	@echo "=========================="
	@echo ""
	@echo "Development:"
	@echo "  install        Install runtime dependencies"
	@echo "  install-dev    Install development dependencies"
	@echo "  install-build  Install build dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-performance Run performance tests only"
	@echo ""
	@echo "Building:"
	@echo "  build         Build standalone executable"
	@echo "  build-debug   Build debug executable"
	@echo "  build-clean   Clean build and rebuild executable"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean         Clean build artifacts and cache"
	@echo "  lint          Run code linting"
	@echo "  format        Format code"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-build.txt

install-build:
	pip install -r requirements-build.txt

# Testing targets
test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/unit/ -v

test-integration:
	python -m pytest tests/integration/ -v

test-performance:
	python -m pytest tests/performance/ -v -m performance

# Building targets
build:
	python build_executable.py

build-debug:
	python build_executable.py --debug

build-clean:
	python build_executable.py --clean

# Maintenance targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

lint:
	@echo "Running flake8..."
	@flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics || echo "flake8 not installed"
	@echo "Running mypy..."
	@mypy src/ || echo "mypy not installed"

format:
	@echo "Formatting with black..."
	@black src/ tests/ || echo "black not installed"

# Platform-specific targets
ifeq ($(OS),Windows_NT)
    # Windows-specific commands
    PYTHON = python
    RM = del /Q
    RMDIR = rmdir /S /Q
else
    # Unix-like systems (Linux, macOS)
    PYTHON = python3
    RM = rm -f
    RMDIR = rm -rf
endif

# Development server (if we add one later)
serve:
	@echo "PicSort is a CLI application, no server to start"
	@echo "Try: python -m src.cli.main --help"

# Quick test command
quick-test:
	python -m src.cli.main --help

# Package for distribution
package: build
	@echo "Creating distribution package..."
	@mkdir -p package
	@cp -r dist/* package/
	@cp README.md package/
	@cp CHANGELOG.md package/ || true
	@echo "Distribution package created in package/"

# Install from source (development installation)
install-source:
	pip install -e .

# Uninstall
uninstall:
	pip uninstall picsort -y
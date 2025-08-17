# MyConfig Makefile

.PHONY: help install install-user install-system install-dev uninstall clean build test lint format check

# Default target
help:
	@echo "MyConfig - macOS Configuration Backup and Restore Tool"
	@echo ""
	@echo "Available commands:"
	@echo "  help          Show this help message"
	@echo "  install       Interactive installation"
	@echo "  install-user  User installation (recommended)"
	@echo "  install-system System installation (requires sudo)"
	@echo "  install-dev   Development mode installation"
	@echo "  uninstall     Uninstall"
	@echo "  clean         Clean build files"
	@echo "  build         Build package"
	@echo "  test          Run tests"
	@echo "  lint          Code linting"
	@echo "  format        Code formatting"
	@echo "  check         Full check (lint + test)"

# Installation related
install:
	@./scripts/install.sh

install-user:
	@./scripts/install.sh --user

install-system:
	@./scripts/install.sh --system

install-dev:
	@./scripts/install.sh --dev

uninstall:
	@echo "Uninstalling MyConfig..."
	pip3 uninstall myconfig -y || echo "No installed version found"

# Development related
clean:
	@echo "Cleaning build files..."
	@rm -rf build/ dist/ *.egg-info/
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "*.pyd" -delete
	@find . -name ".coverage" -delete
	@find . -name "*.cover" -delete
	@find . -name "*.log" -delete

build: clean
	@echo "Building package..."
	@python3 -m build

test:
	@echo "Running tests..."
	@if [ -d "tests" ]; then \
		python3 -m pytest tests/ -v; \
	else \
		echo "No test files yet"; \
	fi

lint:
	@echo "Code linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 src/ --max-line-length=88 --extend-ignore=E203,W503; \
	else \
		echo "flake8 not installed, skipping check"; \
	fi
	@if command -v mypy >/dev/null 2>&1; then \
		mypy src/ --ignore-missing-imports; \
	else \
		echo "mypy not installed, skipping type check"; \
	fi

format:
	@echo "Code formatting..."
	@if command -v black >/dev/null 2>&1; then \
		black src/; \
	else \
		echo "black not installed, skipping formatting"; \
	fi

check: lint test
	@echo "Full check completed"

# Release related
package: clean build
	@echo "Creating release package..."
	@ls -la dist/

# Development environment setup
dev-setup:
	@echo "Setting up development environment..."
	@pip3 install --user -e ".[dev]"
	@echo "Development environment setup completed"

# Verify installation
verify:
	@echo "Verifying installation..."
	@if command -v myconfig >/dev/null 2>&1; then \
		echo "✓ myconfig command available"; \
		echo "Version: $$(myconfig --version)"; \
		myconfig doctor; \
	else \
		echo "✗ myconfig command not available"; \
		exit 1; \
	fi

# Show project information
info:
	@echo "Project information:"
	@echo "  Name: MyConfig"
	@echo "  Version: $$(python3 -c 'import sys; sys.path.insert(0, "src"); from _version import VERSION; print(VERSION)')"
	@echo "  Python: $$(python3 --version)"
	@echo "  Directory: $$(pwd)"
	@echo "  Package count: $$(find src -name '*.py' | wc -l | tr -d ' ') Python files"

# MyConfig Makefile

.PHONY: help install install-user install-system install-dev uninstall clean build test lint format check publish test-publish check-package clean-build clean-pyc clean-test release test-release version

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
	@echo ""
	@echo "PyPI Publishing:"
	@echo "  publish       Publish to PyPI"
	@echo "  test-publish  Publish to Test PyPI"
	@echo "  check-package Check built package"
	@echo "  release       Full release process (build + check + publish)"
	@echo "  test-release  Full test release process"
	@echo ""
	@echo "Utilities:"
	@echo "  version       Show version information"
	@echo "  clean-build   Clean build directories only"
	@echo "  clean-pyc     Clean Python cache only"
	@echo "  clean-test    Clean test cache only"

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
		flake8 myconfig/ --max-line-length=88 --extend-ignore=E203,W503; \
	else \
		echo "flake8 not installed, skipping check"; \
	fi
	@if command -v mypy >/dev/null 2>&1; then \
		mypy myconfig/ --ignore-missing-imports; \
	else \
		echo "mypy not installed, skipping type check"; \
	fi

format:
	@echo "Code formatting..."
	@if command -v black >/dev/null 2>&1; then \
		black myconfig/; \
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
	@echo "  Version: $$(python3 -c 'import sys; sys.path.insert(0, "myconfig"); from _version import VERSION; print(VERSION)')"
	@echo "  Python: $$(python3 --version)"
	@echo "  Directory: $$(pwd)"
	@echo "  Package count: $$(find myconfig -name '*.py' | wc -l | tr -d ' ') Python files"

# PyPI Publishing related
publish: check-package
	@echo "Publishing to PyPI..."
	@if [ -z "$$PYPI_TOKEN" ]; then \
		echo "Error: Please set PYPI_TOKEN environment variable"; \
		echo "Example: export PYPI_TOKEN=your_token_here"; \
		exit 1; \
	fi
	TWINE_PASSWORD=$$PYPI_TOKEN twine upload dist/*
	@echo "Successfully published to PyPI!"
	@echo "Package URL: https://pypi.org/project/myconfig-osx/"

test-publish: check-package
	@echo "Publishing to Test PyPI..."
	@if [ -z "$$PYPI_TOKEN" ]; then \
		echo "Error: Please set PYPI_TOKEN environment variable"; \
		echo "Example: export PYPI_TOKEN=your_token_here"; \
		exit 1; \
	fi
	TWINE_PASSWORD=$$PYPI_TOKEN twine upload --repository testpypi dist/*
	@echo "Successfully published to Test PyPI!"
	@echo "Package URL: https://test.pypi.org/project/myconfig-osx/"

check-package: build
	@echo "Checking built package..."
	twine check dist/*
	@echo "Package check passed!"

# Enhanced cleaning targets
clean-build:
	@echo "Cleaning build directories..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf m'y'con'fi'g/*.egg-info/
	@echo "Build directories cleaned!"

clean-pyc:
	@echo "Cleaning Python cache..."
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	@echo "Python cache cleaned!"

clean-test:
	@echo "Cleaning test cache..."
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	@echo "Test cache cleaned!"

# Full release process
release: clean build check-package publish
	@echo "Release process completed successfully!"

test-release: clean build check-package test-publish
	@echo "Test release process completed successfully!"

# Version information
version:
	@echo "Current version information:"
	@python3 -c "from myconfig._version import VERSION; print(f'Version: {VERSION}')"
	@echo "Project name: myconfig-osx"
	@echo "Python version requirement: >=3.8"

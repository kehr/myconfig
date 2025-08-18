#!/usr/bin/env python3
"""
Test runner script for MyConfig.

This script provides convenient test execution with different options.
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n🔍 {description}")
    print("=" * 50)
    
    result = subprocess.run(cmd, shell=True)
    if result.returncode == 0:
        print(f"✅ {description} passed")
    else:
        print(f"❌ {description} failed")
        return False
    return True


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="MyConfig Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    import os
    os.chdir(project_root)
    
    # Build pytest command
    pytest_cmd = "python -m pytest"
    
    if args.verbose:
        pytest_cmd += " -v"
    
    if args.fast:
        pytest_cmd += " -m 'not slow'"
    
    if args.coverage:
        pytest_cmd += " --cov=myconfig --cov-report=term-missing --cov-report=html"
    
    # Determine which tests to run
    if args.unit:
        pytest_cmd += " tests/unit/"
        description = "Unit Tests"
    elif args.integration:
        pytest_cmd += " tests/integration/"
        description = "Integration Tests"
    else:
        pytest_cmd += " tests/"
        description = "All Tests"
    
    # Run tests
    success = run_command(pytest_cmd, description)
    
    if args.coverage and success:
        print(f"\n📊 Coverage report generated in htmlcov/index.html")
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

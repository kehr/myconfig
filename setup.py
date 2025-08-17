#!/usr/bin/env python3
"""
MyConfig - macOS Configuration Backup and Restore Tool
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read version information
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'src', 'cli.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('VERSION = '):
                return line.split('"')[1]
    return "0.0.0"

setup(
    name="myconfig",
    version=get_version(),
    description="macOS configuration backup and restore tool",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="Kyle",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/myconfig",
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Include non-Python files
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.toml", "*.md"],
    },
    
    # Dependencies
    python_requires=">=3.8",
    install_requires=[
        # Optional TOML parsing library (Python < 3.11)
        'tomli>=1.2.0; python_version<"3.11"',
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
        "encryption": [
            "cryptography>=3.4",
        ],
    },
    
    # Command line entry points
    entry_points={
        "console_scripts": [
            "myconfig=src.cli:main",
        ],
    },
    
    # Classification information
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    
    # Keywords
    keywords="macos backup restore configuration dotfiles homebrew",
    
    # Project links
    project_urls={
        "Documentation": "https://github.com/yourusername/myconfig/blob/main/docs/",
        "Bug Reports": "https://github.com/yourusername/myconfig/issues",
        "Source": "https://github.com/yourusername/myconfig",
    },
)

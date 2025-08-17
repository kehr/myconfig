#!/usr/bin/env python3
"""
MyConfig - macOS 配置备份与恢复工具
"""

from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# 读取版本信息
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
    description="macOS 配置备份与恢复工具",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="Kyle",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/myconfig",
    
    # 包配置
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # 包含非 Python 文件
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.toml", "*.md"],
    },
    
    # 依赖
    python_requires=">=3.8",
    install_requires=[
        # 可选的 TOML 解析库（Python < 3.11）
        'tomli>=1.2.0; python_version<"3.11"',
    ],
    
    # 可选依赖
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
    
    # 命令行入口点
    entry_points={
        "console_scripts": [
            "myconfig=src.cli:main",
        ],
    },
    
    # 分类信息
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
    
    # 关键词
    keywords="macos backup restore configuration dotfiles homebrew",
    
    # 项目链接
    project_urls={
        "Documentation": "https://github.com/yourusername/myconfig/blob/main/docs/",
        "Bug Reports": "https://github.com/yourusername/myconfig/issues",
        "Source": "https://github.com/yourusername/myconfig",
    },
)

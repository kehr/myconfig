---
layout: doc
title: Usage Guide
description: Complete command reference and common scenarios for MyConfig
---

# MyConfig Usage Guide

## Table of Contents

- [Installation](#installation)
- [Basic Concepts](#basic-concepts)
- [Command Reference](#command-reference)
- [Common Scenarios](#common-scenarios)
- [Advanced Features](#advanced-features)
- [CLI Tools Detection](#cli-tools-detection)
- [Template System](#template-system)
- [Troubleshooting](#troubleshooting)

## Installation

### PyPI Installation (Recommended)

```bash
# Install from PyPI
pip install myconfig-osx

# Verify installation
myconfig --version
myconfig doctor
```

### Development Installation

```bash
# Clone and install from source
git clone https://github.com/kehr/myconfig.git
cd myconfig
pip install -e .

# Verify installation
myconfig --version
myconfig doctor
```

### Direct Usage (No Installation)

```bash
# Clone repository
git clone https://github.com/kehr/myconfig.git
cd myconfig

# Set permissions and use directly
chmod +x bin/myconfig
./bin/myconfig --help
```

## Basic Concepts

MyConfig is a comprehensive configuration management tool with the following core functions:

- **Export**: Save current system configurations, applications, and CLI tools to a backup directory
- **Restore**: Restore configurations from a backup directory to a new system
- **Preview**: View what will be processed before executing operations
- **Compress**: Create compressed archive backups for easy storage and sharing
- **Scan**: Detect and display installed applications and CLI tools
- **Template System**: Generate professional documentation and metadata files

## Command Reference

### Export Commands

```bash
# Basic export (auto-generates directory name with timestamp)
myconfig export

# Export to specific directory
myconfig export my-backup

# Export with compression (creates .tar.gz archive)
myconfig export my-backup --compress

# Preview export contents (shows what will be backed up)
myconfig --preview export

# Non-interactive mode (auto-confirm all operations)
myconfig -y export

# Dry run (show what would be done without executing)
myconfig --dry-run export

# Verbose mode (detailed logging)
myconfig -v export

# Quiet mode (minimal output)
myconfig --quiet export
```

**Export Contents Include:**
- System environment information (macOS version, hostname, Xcode tools)
- Homebrew configuration (Brewfile with packages, casks, taps, version info)
- Mac App Store application list (with mas integration)
- VS Code extensions and settings
- npm/pip global package lists
- **Enhanced Application Detection**: 200+ applications across 15+ categories
- **CLI Tools Configuration**: Automatic detection and backup of 50+ development tools
  - Shell configurations: zsh, fish, bash, starship, oh-my-zsh
  - Development tools: git, vim, neovim, tmux, screen
  - Language environments: node.js, python, rust, go, java, php
  - Cloud tools: AWS CLI, Google Cloud SDK, Azure CLI, kubectl, helm
  - Database clients: mysql, postgresql, mongodb, redis
- Configuration files (dotfiles) with security filtering
- System preferences (defaults domains with curated lists)
- LaunchAgents user services
- Auto-generated README.md with detailed manifest and statistics
- Metadata files (MANIFEST.json, version info, component summaries)

### Restore Commands

```bash
# Basic restore from directory
myconfig restore backup-directory

# Restore from compressed archive
myconfig restore backup.tar.gz

# Preview restore contents (shows what will be restored)
myconfig --preview restore backup-directory

# Skip Mac App Store applications during restore
myconfig --no-mas restore backup-directory

# Non-interactive restore
myconfig -y restore backup-directory

# Verbose restore with detailed logging
myconfig -v restore backup-directory
```

**Restore Process:**
1. Verify backup integrity and compatibility
2. Install Homebrew (if not installed and required)
3. Restore brew packages, casks, and taps
4. Restore dotfiles (automatically backs up existing files)
5. Restore VS Code extensions and settings
6. Restore system preferences (defaults domains)
7. Restore LaunchAgents user services
8. Restore CLI tools configurations with proper permissions
9. Generate restoration report and summary

### Archive Management

```bash
# Unpack compressed backup archive
myconfig unpack backup.tar.gz

# Unpack to specific directory
myconfig unpack backup.tar.gz extracted-backup

# Unpack and then restore
myconfig unpack backup.tar.gz
myconfig restore backup  # Uses extracted directory name
```

### Scanning and Detection

```bash
# Scan installed applications and CLI tools
myconfig scan

# Scan with applications focus
myconfig scan --apps

# Preview scan results (same as scan)
myconfig --preview export
```

### System Diagnostics

```bash
# System health check and environment diagnostics
myconfig doctor

# Check specific components
myconfig doctor --verbose
```

### Configuration Management

```bash
# List available configuration profiles
myconfig profile list

# Use specific configuration profile
myconfig profile use dev-full
myconfig profile use minimal

# Save current configuration as new profile
myconfig profile save my-custom-profile
```

### System Defaults Operations

```bash
# Export all system defaults domains
myconfig defaults export-all

# Import defaults from directory
myconfig defaults import backup-directory/defaults
```

### Backup Comparison and Management

```bash
# Compare differences between two backups
myconfig diff backup1 backup2

# Pack backup with optional encryption
myconfig pack backup-directory
myconfig pack backup-directory --gpg  # With GPG encryption
```

### Global Options

```bash
# Configuration file options
myconfig -c ~/.myconfig/config.toml export    # Custom config file
myconfig -c ~/dev-config/ export              # Config directory

# Output control
myconfig -v export          # Verbose output
myconfig --quiet export     # Minimal output
myconfig -y export          # Non-interactive (yes to all)

# Operation modes
myconfig --dry-run export   # Test mode (no actual changes)
myconfig --preview export   # Preview mode (show what will be done)

# Version and help
myconfig --version          # Show version information
myconfig --help            # Show help message
```

## Common Scenarios

### Scenario 1: New Machine Setup

```bash
# On old machine: create comprehensive backup
myconfig export machine-backup --compress

# Transfer backup.tar.gz to new machine

# On new machine: restore complete environment
myconfig unpack machine-backup.tar.gz
myconfig restore machine-backup
```

### Scenario 2: Regular Development Environment Backups

```bash
# Create timestamped backup
myconfig export "dev-backup-$(date +%Y%m%d-%H%M%S)"

# Automated backup script
#!/bin/bash
BACKUP_NAME="automated-backup-$(date +%Y%m%d)"
myconfig export "$BACKUP_NAME" --compress
echo "Backup completed: $BACKUP_NAME.tar.gz"
```

### Scenario 3: Configuration Testing and Validation

```bash
# Preview what will be backed up
myconfig --preview export

# Test backup process without making changes
myconfig --dry-run export test-backup

# Actual backup after validation
myconfig export production-backup --compress
```

### Scenario 4: Selective Configuration Management

```bash
# Use minimal configuration profile
myconfig profile use minimal
myconfig export minimal-backup

# Switch to full development profile
myconfig profile use dev-full
myconfig export full-dev-backup

# Create custom profile
myconfig profile save my-workflow
```

### Scenario 5: CLI Tools Migration

```bash
# Preview detected CLI tools and configurations
myconfig --preview export

# Export development environment with CLI tools
myconfig export dev-environment

# On new machine: restore CLI tools and configurations
myconfig restore dev-environment

# Verify CLI tools restoration
myconfig scan
```

### Scenario 6: Team Environment Standardization

```bash
# Create team standard configuration
myconfig profile use team-standard
myconfig export team-config --compress

# Team members restore standard environment
myconfig restore team-config.tar.gz

# Verify environment consistency
myconfig doctor
```

## Advanced Features

### Configuration Profiles

MyConfig supports multiple configuration profiles for different use cases:

```bash
# Available profiles
myconfig profile list

# Development profiles
myconfig profile use dev-full      # Complete development environment
myconfig profile use dev-minimal   # Essential development tools only

# Specialized profiles
myconfig profile use designer      # Design and creative tools focus
myconfig profile use sysadmin      # System administration tools
```

### Custom Configuration Paths

```bash
# Use custom configuration file
myconfig -c ~/custom-config.toml export

# Use configuration directory
myconfig -c ~/.myconfig-custom/ export

# Configuration precedence:
# 1. CLI --config parameter
# 2. ~/.myconfig (file or directory)
# 3. ./config/config.toml (project default)
```

### Template Customization

```bash
# Templates are located in myconfig/templates/
# Customize README.md generation
vim myconfig/templates/README.md.template

# Customize environment information
vim myconfig/templates/ENVIRONMENT.txt.template

# Test template changes
myconfig export test-templates
cat test-templates/README.md
```

### Plugin System

```bash
# Plugins are auto-loaded from myconfig/plugins/
# Example: custom plugin adds new command
myconfig custom-command --help

# Plugin development
# Create myconfig/plugins/my_plugin.py
# Implement register() function
```

## CLI Tools Detection

MyConfig automatically detects and backs up configurations for 50+ CLI development tools:

### Detection Methods

1. **PATH-based Detection**: Scans system PATH for executables
2. **Homebrew Integration**: Queries installed Homebrew packages
3. **Package Manager Detection**: Checks npm, pip, cargo packages
4. **Configuration File Scanning**: Directly scans common config locations

### Supported Tool Categories

**Shell and Terminal**
- zsh, fish, bash configurations
- tmux, screen session managers
- starship, oh-my-zsh prompt customizations

**Development Tools**
- git version control settings
- vim, neovim, emacs editor configurations
- Language-specific tools (node, python, rust, go, java, php)

**Cloud and Infrastructure**
- AWS CLI, Google Cloud SDK, Azure CLI
- Kubernetes tools (kubectl, helm, kustomize)
- Container tools (docker, podman)

**Database Tools**
- mysql, postgresql, mongodb clients
- Redis, InfluxDB, Cassandra configurations

### CLI Tools Usage Examples

```bash
# Preview detected CLI tools
myconfig --preview export
# Shows: git, vim, tmux, zsh, node, python configurations found

# Export with CLI tools
myconfig export dev-backup
# Includes: ~/.gitconfig, ~/.vimrc, ~/.tmux.conf, ~/.zshrc, etc.

# Restore CLI tools (maintains permissions and symlinks)
myconfig restore dev-backup
```

## Template System

MyConfig uses a powerful template system for generating documentation:

### Available Templates

- `README.md.template`: Backup documentation with statistics
- `ENVIRONMENT.txt.template`: System environment information
- `MANIFEST.json.template`: Backup metadata and component details

### Template Variables

Templates have access to comprehensive context data:

```mustache
# Global variables
{{export_time}}           # Timestamp
{{hostname}}              # System hostname
{{total_components}}      # Number of components
{{total_files}}          # Total files backed up
{{total_size_formatted}} # Human-readable size

# Component-specific data
{{#homebrew}}
Homebrew: {{brew_count}} packages, {{cask_count}} casks
{{/homebrew}}

{{#vscode}}
VS Code: {{extension_count}} extensions
{{/vscode}}
```

### Template Customization

```bash
# Edit templates
vim myconfig/templates/README.md.template

# Test changes
myconfig export test-output
cat test-output/README.md
```

## Troubleshooting

### Common Issues

**1. Permission Errors**
```bash
# Fix permissions for executable
chmod +x bin/myconfig

# Fix Python path issues
export PYTHONPATH="$(pwd):$PYTHONPATH"
```

**2. Missing Dependencies**
```bash
# Install required packages
pip install tomli click rich

# Check system requirements
myconfig doctor
```

**3. Homebrew Issues**
```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Update Homebrew
brew update && brew upgrade
```

**4. Configuration Issues**
```bash
# Validate configuration
myconfig --dry-run export

# Use default configuration
myconfig -c config/config.toml export

# Reset to minimal configuration
myconfig profile use minimal
```

### Debug Mode

```bash
# Enable verbose logging
myconfig -v export

# Dry run for testing
myconfig --dry-run export

# Preview mode for inspection
myconfig --preview export
```

### Getting Help

```bash
# General help
myconfig --help

# Command-specific help
myconfig export --help
myconfig restore --help

# System diagnostics
myconfig doctor
```

### Log Files

MyConfig generates detailed logs during operations:

- Console output with progress indicators
- Error messages with context
- Component-specific status reports
- File operation summaries

### Performance Optimization

```bash
# Skip large components if needed
myconfig profile use minimal

# Use compression for large backups
myconfig export --compress

# Exclude specific directories in config.toml
```

For additional support, see the [GitHub Issues](https://github.com/kehr/myconfig/issues) page or consult the comprehensive documentation in the [docs](../docs/) directory.
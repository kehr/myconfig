---
layout: default
title: MyConfig
---

[![PyPI version](https://badge.fury.io/py/myconfig-osx.svg)](https://badge.fury.io/py/myconfig-osx)
[![Downloads](https://pepy.tech/badge/myconfig-osx)](https://pepy.tech/project/myconfig-osx)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)
[![GitHub stars](https://img.shields.io/github/stars/kehr/myconfig.svg)](https://github.com/kehr/myconfig/stargazers)

A comprehensive macOS system configuration backup and restore tool designed for developers and system administrators.

## Features

- **Complete System Backup**: Comprehensive backup of Homebrew packages, VS Code extensions, dotfiles, system preferences, and application configurations
- **Enhanced Application Detection**: Automatic detection and backup of 200+ applications across 15+ categories including development tools, design software, productivity apps, and system utilities
- **CLI Tools Support**: Intelligent detection and backup of 50+ command-line development tools including git, vim, tmux, zsh, node.js, python, rust, and more
- **Secure and Reliable**: Automatically excludes sensitive files (SSH keys, passwords) with built-in security filtering and backup integrity validation
- **Preview Mode**: Preview what will be backed up or restored before executing operations
- **Compression Support**: Create compressed backup archives (.tar.gz) for easy storage and sharing
- **Template System**: Professional documentation generation with customizable templates for README.md, manifests, and metadata files
- **Configuration Profiles**: Multiple configuration profiles for different use cases (minimal, development, full)
- **Plugin System**: Extensible architecture supporting custom plugins for additional functionality
- **Modern Architecture**: Class-based design with proper separation of concerns and comprehensive error handling
- **Cross-Platform Compatibility**: Optimized for macOS with support for various package managers and development environments

## Quick Start

### Installation

**Method 1: PyPI Installation (Recommended)**

```bash
# Install from PyPI
pip install myconfig-osx

# Verify installation
myconfig --version
myconfig doctor
```

**Method 2: Development Installation**

```bash
# Clone the repository
git clone https://github.com/kehr/myconfig.git
cd myconfig

# Install in development mode
pip install -e .

# Verify installation
myconfig --version
myconfig doctor
```

**Method 3: Direct Usage (No Installation)**

```bash
# Clone the repository
git clone https://github.com/kehr/myconfig.git
cd myconfig

# Set execution permissions
chmod +x bin/myconfig
chmod +x scripts/install.sh

# Use directly
./bin/myconfig --help

# Or install from source
./scripts/install.sh
```

### Basic Usage

```bash
# Export current system configuration
myconfig export

# Export with compression
myconfig export --compress

# Preview export contents (shows what will be backed up)
myconfig --preview export

# Restore configuration from backup
myconfig restore <backup-directory>

# Restore from compressed archive
myconfig restore backup.tar.gz

# System health check and diagnostics
myconfig doctor

# Scan and display detected applications and CLI tools
myconfig scan
```

## Main Commands

| Command | Description |
|---------|-------------|
| `export [dir]` | Export configuration to specified directory (auto-generates name if not provided) |
| `export --compress [dir]` | Create compressed backup archive (.tar.gz) |
| `restore <dir>` | Restore configuration from backup directory or archive |
| `unpack <archive>` | Unpack compressed backup archive |
| `scan` | Scan and display installed applications and CLI tools |
| `doctor` | System environment check and diagnostics |
| `--preview` | Preview mode - show what will be processed without executing |
| `--dry-run` | Test run mode - show operations without executing them |
| `profile list` | List available configuration profiles |
| `profile use <name>` | Apply specified configuration profile |
| `defaults export-all` | Export all system defaults domains |
| `diff <dir1> <dir2>` | Compare differences between two backup directories |

## Supported Components

### System Tools
- **Homebrew**: Complete package management (formulas, casks, taps) with automatic Brewfile generation
- **Mac App Store**: Application lists with mas integration
- **System Preferences**: macOS defaults domains with curated domain lists
- **LaunchAgents**: User services and background processes

### Development Environment
- **VS Code**: Extensions, settings, and workspace configurations
- **Package Managers**: npm global packages, pip user packages, pipx packages
- **Version Control**: Git configurations, SSH settings (excluding sensitive keys)
- **Shell Environments**: zsh, fish, bash configurations with prompt customizations

### Applications (200+ Supported)
- **Development Tools**: IDEs (IntelliJ, PyCharm, WebStorm, Xcode), editors (Sublime Text, Atom), database tools (TablePlus, Sequel Pro)
- **Design and Creative**: Adobe Creative Suite, Sketch, Figma, Canva, Affinity Suite
- **Productivity**: Office suites, note-taking apps, task managers, calendar applications
- **Communication**: Slack, Discord, Zoom, Microsoft Teams, messaging apps
- **System Utilities**: Alfred, Bartender, CleanMyMac, monitoring tools
- **Browsers**: Chrome, Firefox, Safari, Edge with extension and bookmark support
- **Media Tools**: VLC, IINA, Spotify, audio/video editing software

### CLI Development Tools (50+ Supported)
- **Editors**: vim, neovim, emacs with configuration files and plugins
- **Terminal Tools**: tmux, screen, terminal multiplexers and session managers
- **Shell Enhancement**: starship, oh-my-zsh, fish shell with themes and plugins
- **Development Languages**: node.js, python, rust, go, java, php configurations
- **Build Tools**: make, cmake, gradle, maven, cargo, npm, yarn, pnpm
- **Cloud Tools**: AWS CLI, Google Cloud SDK, Azure CLI, kubectl, helm
- **Database CLI**: mysql, postgresql, mongodb, redis command-line clients
- **Network Tools**: curl, wget, httpie, network utilities and configurations
- **Security Tools**: gpg, ssh, vault, encryption and security utilities

## Security Features

- **Automatic Security Filtering**: Excludes sensitive files (SSH private keys, password files, authentication tokens)
- **Backup Integrity Validation**: Verifies backup completeness and file integrity
- **Safe Restoration**: Creates automatic backups of existing files before restoration
- **Detailed Logging**: Comprehensive operation logging for audit trails
- **Permission Preservation**: Maintains file permissions and symbolic links during backup/restore

## Configuration

MyConfig uses TOML configuration files with support for:

- **Component Enablement**: Selectively enable/disable backup components
- **Custom Application Paths**: Define custom configuration paths for applications
- **CLI Tools Configuration**: Specify detection methods and configuration paths for command-line tools
- **Security Settings**: Configure exclusion patterns and sensitive file handling
- **Template Customization**: Customize generated documentation and metadata files
- **Profile Management**: Create and manage different configuration profiles

## Documentation

- [Installation Guide](docs/installation) - System requirements, installation methods, and troubleshooting
- [Usage Guide](docs/usage) - Complete command reference and common scenarios
- [Configuration](docs/configuration) - TOML configuration, profiles, and environment variables
- [CLI Tools](docs/cli-tools) - CLI tools detection and backup guide
- [Plugin Development](docs/plugins) - Plugin system and extension development
- [Template System](docs/templates) - Template system documentation

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Security

For security concerns, please see our [Security Policy](SECURITY.md).

## License

This project is licensed under the GPL v2 License - see the [LICENSE](LICENSE) file for details.
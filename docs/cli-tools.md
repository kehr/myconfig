# CLI Tools Detection and Backup Guide

## Table of Contents

- [Overview](#overview)
- [Supported CLI Tools](#supported-cli-tools)
- [Detection Methods](#detection-methods)
- [Configuration Paths](#configuration-paths)
- [Usage Examples](#usage-examples)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)

## Overview

MyConfig now includes comprehensive CLI tools detection and backup capabilities, automatically discovering and backing up configuration files for popular command-line development tools. This feature expands MyConfig's coverage from basic GUI applications to a complete developer ecosystem.

### Key Features

- **Automatic Detection**: Discovers CLI tools through multiple methods
- **Smart Path Resolution**: Handles environment variables and standard locations
- **Package Manager Integration**: Works with Homebrew, npm, pip, and cargo
- **Configuration Backup**: Preserves dotfiles, symlinks, and permissions
- **Cross-Platform Support**: Optimized for macOS with fallback mechanisms

## Supported CLI Tools

MyConfig automatically detects and backs up configurations for the following CLI tools:

### Development Tools
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **git** | `~/.gitconfig`, `~/.gitignore_global` | PATH + config files |
| **vim** | `~/.vimrc`, `~/.vim/` | PATH + config files |
| **neovim** | `~/.config/nvim/`, `~/.local/share/nvim/` | PATH + XDG config |
| **tmux** | `~/.tmux.conf`, `~/.tmux/` | PATH + config files |

### Shell Environments
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **zsh** | `~/.zshrc`, `~/.zprofile`, `~/.zshenv` | PATH + config files |
| **fish** | `~/.config/fish/` | PATH + XDG config |
| **starship** | `~/.config/starship.toml` | PATH + config files |
| **oh-my-zsh** | `~/.oh-my-zsh/`, `~/.zshrc` | Directory + config |

### Development Environments
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **node** | `~/.npmrc`, `~/.nvm/`, `~/.node_repl_history` | npm + config files |
| **python** | `~/.pip/pip.conf`, `~/.pypirc`, `~/.python_history` | pip + config files |
| **rust** | `~/.cargo/config.toml`, `~/.rustup/` | cargo + config files |

## Detection Methods

MyConfig uses four complementary detection methods to discover CLI tools:

### 1. PATH-Based Detection

Scans the system PATH for executable files and matches them against the known tools database.

```bash
# Example: Detecting git
which git  # /usr/bin/git or /usr/local/bin/git
# Then checks for ~/.gitconfig, ~/.gitignore_global
```

### 2. Homebrew Integration

Queries Homebrew for installed packages and maps them to configuration files.

```bash
# Example: Homebrew-installed tools
brew list --formula | grep -E "(git|vim|tmux|zsh)"
# Maps to corresponding config files
```

### 3. Package Manager Detection

Checks npm global packages and pip user packages for CLI tools.

```bash
# npm global packages
npm list -g --depth=0

# pip user packages  
pip list --user
```

### 4. Configuration File Scanning

Directly scans common configuration directories for tool-specific files.

```bash
# Common config locations
~/.config/          # XDG config directory
~/.local/share/     # XDG data directory
~/.*rc              # RC files (dotfiles)
```

## Configuration Paths

MyConfig handles various configuration path patterns with intelligent resolution:

### Environment Variable Expansion

```toml
# Example configuration in applications.default
[git]
config_paths = [
    "$HOME/.gitconfig",
    "$HOME/.gitignore_global",
    "$XDG_CONFIG_HOME/git/config"
]
```

### Standard Locations with Fallbacks

```python
# Path resolution logic
paths = [
    os.path.expandvars("$XDG_CONFIG_HOME/tool/config"),  # XDG first
    os.path.expanduser("~/.config/tool/config"),         # Standard fallback
    os.path.expanduser("~/.toolrc")                      # Legacy fallback
]
```

### Supported Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `$HOME` | User home directory | `/Users/username` |
| `$XDG_CONFIG_HOME` | XDG config directory | `~/.config` |
| `$XDG_DATA_HOME` | XDG data directory | `~/.local/share` |
| `$USER` | Current username | `username` |

## Usage Examples

### Basic CLI Tools Detection

```bash
# Preview detected CLI tools
myconfig --preview export

# Example output:
# ✓ Detected CLI Tools (11 found):
#   git: ~/.gitconfig, ~/.gitignore_global
#   vim: ~/.vimrc, ~/.vim/vimrc
#   tmux: ~/.tmux.conf
#   zsh: ~/.zshrc, ~/.oh-my-zsh/
#   node: ~/.npmrc, ~/.nvm/default-packages
#   python: ~/.pip/pip.conf
#   starship: ~/.config/starship.toml
```

### Export with CLI Tools

```bash
# Export including CLI tools
myconfig export dev-backup

# Verify CLI tools backup
ls dev-backup/applications/
# Output: cli_tools_config.json, detected_tools.txt, tool_configs/
```

### Restore CLI Tools

```bash
# Restore from backup (includes CLI tools)
myconfig restore dev-backup

# CLI tools are automatically restored with proper permissions
```

### Selective CLI Tools Backup

```bash
# Configure specific tools in config.toml
[applications]
cli_tools_whitelist = ["git", "vim", "tmux"]  # Only backup these
cli_tools_blacklist = ["node", "python"]      # Exclude these
```

## Advanced Configuration

### Custom Tool Detection

Add custom CLI tools to the detection system:

```toml
# config/config.toml
[applications.default.custom_tool]
config_paths = [
    "$HOME/.custom_toolrc",
    "$XDG_CONFIG_HOME/custom_tool/config.yaml"
]
detection_command = "custom_tool --version"
backup_permissions = true
```

### Detection Tuning

```toml
[applications]
# Performance tuning
max_detection_time = 30        # seconds
parallel_detection = true      # enable parallel scanning
cache_detection_results = true # cache results for session

# Path scanning options
scan_hidden_dirs = true        # scan .hidden directories
follow_symlinks = false        # don't follow symbolic links
max_scan_depth = 3            # maximum directory depth
```

### Backup Options

```toml
[applications.cli_tools]
# Backup behavior
preserve_permissions = true    # maintain file permissions
preserve_symlinks = true      # maintain symbolic links
compress_configs = true       # compress large config directories
exclude_cache_dirs = true     # skip cache directories

# Exclusion patterns
exclude_patterns = [
    "*.log",
    "*.cache",
    "node_modules/",
    "__pycache__/"
]
```

## Troubleshooting

### Common Issues

**1. CLI Tool Not Detected**

```bash
# Check if tool is in PATH
which tool_name

# Check if config files exist
ls -la ~/.toolrc ~/.config/tool/

# Enable debug logging
myconfig -v --preview export
```

**2. Configuration Files Not Found**

```bash
# Verify environment variables
echo $HOME $XDG_CONFIG_HOME

# Check file permissions
ls -la ~/.config/

# Test path expansion
python3 -c "import os; print(os.path.expandvars('$XDG_CONFIG_HOME/tool'))"
```

**3. Backup/Restore Issues**

```bash
# Check backup contents
ls -la backup-dir/applications/tool_configs/

# Verify permissions
ls -la ~/.toolrc

# Check restore logs
tail -f logs/myconfig.log
```

### Debug Commands

```bash
# Enable verbose CLI tools detection
export MYCONFIG_DEBUG_CLI_TOOLS=true
myconfig --preview export

# Test specific tool detection
myconfig debug detect-tool git

# Validate configuration paths
myconfig debug validate-paths
```

### Performance Optimization

```bash
# Reduce detection time
[applications]
enable_path_scanning = false      # disable PATH scanning
enable_package_managers = false   # disable package manager queries
cli_tools_whitelist = ["git", "vim"]  # limit to essential tools

# Cache detection results
cache_detection_results = true
detection_cache_ttl = 3600  # 1 hour cache
```

## Integration with Other Components

### Dotfiles Component

CLI tools configurations are automatically integrated with the dotfiles component:

```bash
# Dotfiles backup includes CLI tool configs
myconfig export --component dotfiles
# Includes: ~/.vimrc, ~/.tmux.conf, ~/.zshrc, etc.
```

### Homebrew Component

CLI tools installed via Homebrew are cross-referenced:

```bash
# Homebrew Brewfile includes CLI tools
brew bundle dump --file=Brewfile
# Includes: git, vim, tmux, etc.
```

### Template System

CLI tools information is available in templates:

```mustache
{{#cli_tools}}
## Detected CLI Tools
{{#tools}}
- **{{name}}**: {{config_files}}
{{/tools}}
{{/cli_tools}}
```

For more information about MyConfig's architecture and other components, see:
- [Configuration Reference](configuration.md)
- [Usage Guide](usage.md)
- [Plugin Development](plugins.md)
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

MyConfig includes comprehensive CLI tools detection and backup capabilities, automatically discovering and backing up configuration files for popular command-line development tools. This feature expands MyConfig's coverage from basic GUI applications to a complete developer ecosystem.

### Key Features

- **Automatic Detection**: Discovers CLI tools through multiple detection methods
- **Smart Path Resolution**: Handles environment variables and standard locations
- **Package Manager Integration**: Works with Homebrew, npm, pip, and cargo
- **Configuration Backup**: Preserves dotfiles, symlinks, and permissions
- **Cross-Platform Support**: Optimized for macOS with fallback mechanisms
- **Comprehensive Coverage**: Supports 50+ CLI development tools across multiple categories

## Supported CLI Tools

MyConfig automatically detects and backs up configurations for the following CLI tools:

### Version Control Systems
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **git** | `~/.gitconfig`, `~/.gitignore_global` | PATH + config files |
| **mercurial** | `~/.hgrc` | PATH + config files |
| **subversion** | `~/.subversion/` | PATH + config files |

### Text Editors and IDEs
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **vim** | `~/.vimrc`, `~/.vim/` | PATH + config files |
| **neovim** | `~/.config/nvim/`, `~/.local/share/nvim/` | PATH + XDG config |
| **emacs** | `~/.emacs`, `~/.emacs.d/` | PATH + config files |
| **nano** | `~/.nanorc` | PATH + config files |

### Shell Environments
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **zsh** | `~/.zshrc`, `~/.zprofile`, `~/.zshenv` | PATH + config files |
| **fish** | `~/.config/fish/` | PATH + XDG config |
| **bash** | `~/.bashrc`, `~/.bash_profile`, `~/.profile` | PATH + config files |
| **starship** | `~/.config/starship.toml` | PATH + config files |
| **oh-my-zsh** | `~/.oh-my-zsh/`, `~/.zshrc` | Directory + config |

### Terminal Multiplexers
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **tmux** | `~/.tmux.conf` | PATH + config files |
| **screen** | `~/.screenrc` | PATH + config files |

### Development Languages and Runtimes
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **node** | `~/.npmrc`, `~/.nvm/`, `~/.node_repl_history` | npm + config files |
| **python** | `~/.pip/pip.conf`, `~/.pypirc`, `~/.python_history` | pip + config files |
| **rust** | `~/.cargo/config.toml`, `~/.rustup/` | cargo + config files |
| **go** | `~/.config/go/`, `~/go/` | PATH + config files |
| **java** | `~/.java/`, `~/.m2/` | PATH + config files |
| **php** | `~/.composer/` | PATH + config files |
| **ruby** | `~/.gemrc`, `~/.rvm/` | PATH + config files |

### Build Tools and Package Managers
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **npm** | `~/.npmrc` | npm + config files |
| **yarn** | `~/.yarnrc` | PATH + config files |
| **pnpm** | `~/.pnpmrc` | PATH + config files |
| **pip** | `~/.pip/pip.conf` | pip + config files |
| **cargo** | `~/.cargo/config.toml` | cargo + config files |
| **maven** | `~/.m2/settings.xml` | PATH + config files |
| **gradle** | `~/.gradle/` | PATH + config files |

### Cloud and Infrastructure Tools
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **aws-cli** | `~/.aws/` | PATH + config files |
| **gcloud** | `~/.config/gcloud/` | PATH + XDG config |
| **azure-cli** | `~/.azure/` | PATH + config files |
| **kubectl** | `~/.kube/config` | PATH + config files |
| **helm** | `~/.config/helm/` | PATH + XDG config |
| **terraform** | `~/.terraformrc` | PATH + config files |
| **ansible** | `~/.ansible.cfg` | PATH + config files |

### Container Tools
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **docker** | `~/.docker/config.json` | PATH + config files |
| **podman** | `~/.config/containers/` | PATH + XDG config |
| **vagrant** | `~/.vagrant.d/` | PATH + config files |

### Database CLI Tools
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **mysql** | `~/.my.cnf` | PATH + config files |
| **postgresql** | `~/.psqlrc` | PATH + config files |
| **mongodb** | `~/.mongorc.js` | PATH + config files |
| **redis-cli** | `~/.rediscli_history` | PATH + config files |
| **sqlite3** | `~/.sqlite_history` | PATH + config files |

### Network and System Tools
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **curl** | `~/.curlrc` | PATH + config files |
| **wget** | `~/.wgetrc` | PATH + config files |
| **httpie** | `~/.config/httpie/` | PATH + XDG config |
| **ssh** | `~/.ssh/config`, `~/.ssh/known_hosts` | PATH + config files |

### File and Text Processing
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **ripgrep** | `~/.config/rg/` | PATH + XDG config |
| **fd** | `~/.config/fd/` | PATH + XDG config |
| **bat** | `~/.config/bat/` | PATH + XDG config |
| **exa** | `~/.config/exa/` | PATH + XDG config |
| **lsd** | `~/.config/lsd/` | PATH + XDG config |

### Security Tools
| Tool | Configuration Files | Detection Method |
|------|-------------------|------------------|
| **gpg** | `~/.gnupg/` | PATH + config files |
| **age** | `~/.config/age/` | PATH + XDG config |
| **vault** | `~/.vault-token` | PATH + config files |

## Detection Methods

MyConfig uses four complementary detection methods to discover CLI tools:

### 1. PATH-Based Detection

Scans the system PATH for executable files and matches them against the known tools database.

```bash
# Example: Detecting git
which git  # /usr/bin/git or /usr/local/bin/git
# Then checks for ~/.gitconfig, ~/.gitignore_global
```

**Advantages:**
- Fast and reliable
- Detects system-installed tools
- Works with custom installations

### 2. Homebrew Integration

Queries Homebrew for installed packages and maps them to configuration files.

```bash
# Example: Homebrew-installed tools
brew list --formula | grep -E "(git|vim|tmux|zsh)"
# Maps to corresponding config files
```

**Advantages:**
- Comprehensive package information
- Version tracking
- Dependency mapping

### 3. Package Manager Detection

Checks npm global packages, pip user packages, and cargo packages for CLI tools.

```bash
# npm global packages
npm list -g --depth=0

# pip user packages  
pip list --user

# cargo packages
cargo install --list
```

**Advantages:**
- Language-specific tool detection
- Package manager integration
- Development environment awareness

### 4. Configuration File Scanning

Directly scans common configuration directories for tool-specific files.

```bash
# Common config locations
~/.config/          # XDG config directory
~/.local/share/     # XDG data directory
~/.*rc              # RC files (dotfiles)
```

**Advantages:**
- Finds tools without PATH presence
- Detects configuration-only installations
- Comprehensive coverage

## Configuration Paths

MyConfig handles various configuration path patterns with intelligent resolution:

### Environment Variable Expansion

```toml
# Example configuration in cli_tools.default
[cli_tools.default]
git = [
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

### Path Pattern Examples

```toml
[cli_tools.default]
# Simple home directory paths
vim = ["~/.vimrc", "~/.vim/"]

# XDG-compliant paths with fallbacks
neovim = [
    "$XDG_CONFIG_HOME/nvim/",
    "~/.config/nvim/",
    "$XDG_DATA_HOME/nvim/",
    "~/.local/share/nvim/"
]

# Complex patterns with wildcards
"IntelliJ IDEA" = [
    "~/Library/Preferences/IntelliJIdea*",
    "~/Library/Application Support/JetBrains/IntelliJIdea*"
]
```

## Usage Examples

### Basic CLI Tools Detection

```bash
# Preview detected CLI tools
myconfig --preview export

# Example output:
# Detected CLI Tools (25 found):
#   git: ~/.gitconfig, ~/.gitignore_global
#   vim: ~/.vimrc, ~/.vim/vimrc
#   tmux: ~/.tmux.conf
#   zsh: ~/.zshrc, ~/.oh-my-zsh/
#   node: ~/.npmrc, ~/.nvm/default-packages
#   python: ~/.pip/pip.conf
#   starship: ~/.config/starship.toml
#   kubectl: ~/.kube/config
#   docker: ~/.docker/config.json
#   aws-cli: ~/.aws/config, ~/.aws/credentials
```

### Export with CLI Tools

```bash
# Export including CLI tools
myconfig export dev-backup

# Verify CLI tools backup
ls dev-backup/applications/
# Output: cli_tools_config.json, detected_tools.txt, tool_configs/

# Check specific tool configurations
ls dev-backup/applications/tool_configs/
# Output: git/, vim/, tmux/, zsh/, node/, python/, etc.
```

### Restore CLI Tools

```bash
# Restore from backup (includes CLI tools)
myconfig restore dev-backup

# CLI tools are automatically restored with proper permissions
# Symlinks and file permissions are preserved
```

### Scan Only CLI Tools

```bash
# Scan and display detected CLI tools
myconfig scan

# Focus on applications (includes CLI tools)
myconfig scan --apps
```

## Advanced Configuration

### Custom Tool Detection

Add custom CLI tools to the detection system:

```toml
# config/config.toml
[cli_tools.default]
my_custom_tool = [
    "$HOME/.my_custom_toolrc",
    "$XDG_CONFIG_HOME/my_custom_tool/config.yaml"
]
```

### Detection Method Configuration

```toml
[cli_tools.detection]
# Enable/disable detection methods
enable_path_detection = true
enable_homebrew_detection = true
enable_package_manager = true
enable_config_scanning = true

# Performance tuning
max_scan_depth = 3
scan_timeout = 30
cache_results = true
```

### Selective Tool Backup

```toml
# Include only specific tools
[cli_tools]
whitelist = ["git", "vim", "tmux", "zsh"]

# Exclude specific tools
blacklist = ["node", "python"]

# Category-based selection
categories = ["version_control", "editors", "shell"]
```

### Custom Configuration Paths

```toml
[cli_tools.default]
# Override default paths for specific tools
git = [
    "~/custom-git/.gitconfig",
    "~/custom-git/.gitignore_global"
]

# Add additional paths
vim = [
    "~/.vimrc",
    "~/.vim/",
    "~/custom-vim-config/"
]
```

### Detection Performance Tuning

```toml
[cli_tools.detection]
# Scan performance
max_scan_depth = 2          # Reduce depth for faster scanning
scan_timeout = 15           # Shorter timeout
parallel_detection = true   # Enable parallel processing
cache_ttl = 3600           # Cache results for 1 hour

# Custom patterns
config_patterns = [
    ".*rc$",
    ".*conf$",
    "config.*",
    ".*\.toml$"
]

# Directories to scan
scan_directories = [
    "~/.config",
    "~/.local/share",
    "~/Library/Application Support"
]
```

## Troubleshooting

### Common Issues

**1. CLI Tool Not Detected**

```bash
# Check if tool is in PATH
which my-tool

# Verify configuration paths exist
ls ~/.my-toolrc

# Add custom detection
# Edit config/config.toml:
[cli_tools.default]
my-tool = ["~/.my-toolrc"]
```

**2. Configuration Files Not Backed Up**

```bash
# Check file permissions
ls -la ~/.config/my-tool/

# Verify paths in preview
myconfig --preview export | grep my-tool

# Check for symlinks
ls -la ~/.my-toolrc
```

**3. Detection Performance Issues**

```bash
# Reduce scan depth
# Edit config/config.toml:
[cli_tools.detection]
max_scan_depth = 2
scan_timeout = 15

# Enable caching
cache_results = true
```

**4. Missing Environment Variables**

```bash
# Check environment variables
echo $XDG_CONFIG_HOME
echo $HOME

# Set missing variables
export XDG_CONFIG_HOME="$HOME/.config"
```

### Debug Mode

```bash
# Enable verbose logging for CLI tools detection
myconfig -v --preview export

# Check detection methods
myconfig doctor

# Test specific tool detection
myconfig --dry-run export
```

### Performance Optimization

```bash
# Use minimal detection for faster scanning
myconfig profile use minimal

# Disable expensive detection methods
# Edit config/config.toml:
[cli_tools.detection]
enable_config_scanning = false
enable_package_manager = false
```

### Validation

```bash
# Validate CLI tools configuration
myconfig --dry-run export

# Check for configuration errors
myconfig doctor

# Verify backup integrity
myconfig restore --preview backup-directory
```

## Integration with Other Components

### Homebrew Integration

CLI tools detected through Homebrew are automatically included in the Brewfile:

```bash
# Brewfile includes CLI tools
cat backup/Brewfile | grep -E "(git|vim|tmux)"
```

### Package Manager Integration

Package manager configurations are backed up alongside CLI tools:

```bash
# npm configuration
cat backup/applications/tool_configs/node/.npmrc

# pip configuration  
cat backup/applications/tool_configs/python/pip.conf
```

### Dotfiles Integration

CLI tool configurations are included in dotfiles backup:

```bash
# Dotfiles include CLI configurations
tar -tzf backup/dotfiles.tar.gz | grep -E "(\.vimrc|\.tmux\.conf)"
```

For additional information and advanced usage patterns, see the [Configuration Reference](./configuration.md) and [Usage Guide](./usage.md).
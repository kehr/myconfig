# Configuration Reference

## Table of Contents

- [Configuration File Structure](#configuration-file-structure)
- [Main Configuration Options](#main-configuration-options)
- [Applications Configuration](#applications-configuration)
- [CLI Tools Configuration](#cli-tools-configuration)
- [Domain Configuration Files](#domain-configuration-files)
- [Configuration Profile System](#configuration-profile-system)
- [Template Configuration](#template-configuration)
- [Environment Variables](#environment-variables)
- [Advanced Configuration](#advanced-configuration)

## Configuration File Structure

MyConfig uses TOML format configuration files, with the main configuration located at `config/config.toml`.

```
myconfig/
├── config/
│   ├── config.toml          # Main configuration file
│   ├── defaults/
│   │   ├── domains.txt      # System defaults domain list
│   │   └── exclude.txt      # Excluded domains list
│   └── profiles/            # Configuration profiles
│       ├── dev-full.toml    # Full development profile
│       └── minimal.toml     # Minimal profile
├── myconfig/
│   └── templates/           # Template files
│       ├── README.md.template
│       ├── ENVIRONMENT.txt.template
│       └── MANIFEST.json.template
```

## Main Configuration Options

### Basic Settings

```toml
# config/config.toml

# Interactive mode - prompt for user confirmation
interactive = true

# Component enablement
enable_npm = false         # npm global packages
enable_pip_user = false    # pip user packages
enable_pipx = false        # pipx packages
enable_defaults = true     # System preferences (defaults)
enable_vscode = true       # VS Code extensions
enable_launchagents = true # LaunchAgents services
enable_mas = true          # Mac App Store applications

# Advanced features
enable_incremental = false # Incremental backups (future feature)
```

### File Paths

```toml
# Base backup directory (empty = auto-generate with timestamp)
base_backup_dir = ""

# System defaults configuration
defaults_domains_file = "config/defaults/domains.txt"
defaults_exclude_file = "config/defaults/exclude.txt"
```

## Applications Configuration

### GUI Applications Detection

```toml
[applications]
# Enable applications scanning and export
enable = true

# Known GUI application configuration paths mapping
# This section is for GUI applications with graphical interfaces
[applications.default]

# Development Tools (IDEs and Editors)
"Visual Studio Code" = [
  "~/Library/Application Support/Code/User"
]
"Sublime Text" = [
  "~/Library/Application Support/Sublime Text*/Packages/User"
]
"IntelliJ IDEA" = [
  "~/Library/Preferences/IntelliJIdea*",
  "~/Library/Application Support/JetBrains/IntelliJIdea*"
]
"PyCharm" = [
  "~/Library/Preferences/PyCharm*",
  "~/Library/Application Support/JetBrains/PyCharm*"
]
"Xcode" = [
  "~/Library/Developer/Xcode/UserData"
]

# Design and Creative Tools
"Sketch" = [
  "~/Library/Application Support/com.bohemiancoding.sketch3"
]
"Figma" = [
  "~/Library/Application Support/Figma"
]
"Adobe Photoshop" = [
  "~/Library/Preferences/Adobe Photoshop*/Adobe Photoshop * Settings"
]

# Database Tools
"TablePlus" = [
  "~/Library/Application Support/com.tinyapp.TablePlus"
]
"Sequel Pro" = [
  "~/Library/Application Support/Sequel Pro"
]

# Communication Tools
"Slack" = [
  "~/Library/Application Support/Slack"
]
"Discord" = [
  "~/Library/Application Support/discord"
]

# And many more applications...
```

## CLI Tools Configuration

### CLI Tools Detection and Configuration

```toml
[cli_tools]
# CLI tools configuration paths mapping
# This section is dedicated to command-line tools and their configurations

[cli_tools.default]

# Version Control
"git" = [
  "~/.gitconfig",
  "~/.gitignore_global"
]

# Text Editors
"vim" = [
  "~/.vimrc",
  "~/.vim"
]
"neovim" = [
  "~/.config/nvim",
  "~/.local/share/nvim"
]

# Shell Configuration
"zsh" = [
  "~/.zshrc",
  "~/.zprofile",
  "~/.zshenv"
]
"fish" = [
  "~/.config/fish"
]
"bash" = [
  "~/.bashrc",
  "~/.bash_profile",
  "~/.profile"
]

# Terminal Multiplexers
"tmux" = [
  "~/.tmux.conf"
]
"screen" = [
  "~/.screenrc"
]

# Development Languages
"node" = [
  "~/.npmrc",
  "~/.nvm"
]
"python" = [
  "~/.pip/pip.conf",
  "~/.pypirc"
]
"rust" = [
  "~/.cargo/config.toml",
  "~/.rustup"
]

# Cloud Tools
"aws-cli" = [
  "~/.aws"
]
"gcloud" = [
  "~/.config/gcloud"
]
"kubectl" = [
  "~/.kube/config"
]

# Database CLI Tools
"mysql" = [
  "~/.my.cnf"
]
"postgresql" = [
  "~/.psqlrc"
]

# And many more CLI tools...
```

### CLI Tools Detection Settings

```toml
[cli_tools.detection]
# Enable different detection methods
enable_path_detection = true      # Scan system PATH
enable_homebrew_detection = true  # Query Homebrew packages
enable_package_manager = true     # Check npm, pip, cargo
enable_config_scanning = true     # Scan config directories

# Detection performance settings
max_scan_depth = 3                # Maximum directory depth for scanning
scan_timeout = 30                 # Timeout in seconds for detection
cache_results = true              # Cache detection results
```

## Domain Configuration Files

### Defaults Domains (`config/defaults/domains.txt`)

List of macOS defaults domains to export:

```txt
# System domains
com.apple.dock
com.apple.finder
com.apple.Safari
com.apple.screencapture
com.apple.symbolichotkeys

# Accessibility
com.apple.Accessibility
com.apple.universalaccess

# Hardware
com.apple.AppleMultitouchTrackpad
com.apple.AppleMultitouchMouse

# Window management
com.apple.WindowManager
com.apple.spaces
com.apple.controlcenter

# Software Update
com.apple.SoftwareUpdate
com.apple.loginwindow

# Third-party applications
com.googlecode.iterm2
```

### Exclude Domains (`config/defaults/exclude.txt`)

Domains to explicitly exclude from export:

```txt
# Sensitive or temporary domains
com.apple.accountsd
com.apple.security.*
*.keychain*
*.password*

# Large or changing domains
com.apple.LaunchServices*
com.apple.spotlight*
```

## Configuration Profile System

### Profile Structure

Profiles allow you to create different configuration sets for different use cases:

```toml
# config/profiles/dev-full.toml
[profile]
name = "Development Full"
description = "Complete development environment backup"

# Override main config settings
interactive = false
enable_npm = true
enable_pip_user = true
enable_pipx = true
enable_defaults = true
enable_vscode = true
enable_launchagents = true
enable_mas = true

[applications]
enable = true

[cli_tools]
# Enable all CLI tools detection
enable_path_detection = true
enable_homebrew_detection = true
enable_package_manager = true
enable_config_scanning = true
```

### Minimal Profile

```toml
# config/profiles/minimal.toml
[profile]
name = "Minimal"
description = "Essential configurations only"

interactive = true
enable_npm = false
enable_pip_user = false
enable_pipx = false
enable_defaults = false
enable_vscode = true
enable_launchagents = false
enable_mas = false

[applications]
enable = false

[cli_tools]
enable_path_detection = true
enable_homebrew_detection = false
enable_package_manager = false
enable_config_scanning = false
```

### Using Profiles

```bash
# List available profiles
myconfig profile list

# Use specific profile
myconfig profile use dev-full
myconfig profile use minimal

# Save current configuration as new profile
myconfig profile save my-custom-profile
```

## Template Configuration

### Template System Settings

```toml
[templates]
# Template directory (relative to myconfig/)
template_dir = "templates"

# Enable template processing
enable_templates = true

# Template variables (custom context)
[templates.variables]
company_name = "Your Company"
department = "IT Department"
contact_email = "admin@example.com"
```

### Export Options

```toml
[export]
# Default compression format
default_compression = "gzip"  # gzip, bzip2, xz

# Compression level (1-9 for gzip)
compression_level = 6

# Include hidden files in dotfiles
include_hidden = true

# Maximum archive size (MB, 0 = unlimited)
max_archive_size = 1000
```

### Security Settings

```toml
[security]
# Automatically skip sensitive files
skip_sensitive = true

# Additional patterns to exclude (regex)
exclude_patterns = [
    ".*\\.key$",
    ".*\\.pem$",
    ".*password.*",
    ".*secret.*"
]

# Directories to always exclude
exclude_directories = [
    ".ssh",
    ".gnupg",
    ".aws"
]
```

## Environment Variables

### Supported Variables

MyConfig supports environment variable expansion in configuration paths:

| Variable | Purpose | Example |
|----------|---------|---------|
| `$HOME` | User home directory | `/Users/username` |
| `$XDG_CONFIG_HOME` | XDG config directory | `~/.config` |
| `$XDG_DATA_HOME` | XDG data directory | `~/.local/share` |
| `$USER` | Current username | `username` |

### Usage Examples

```toml
[cli_tools.default]
"custom_tool" = [
    "$HOME/.custom_toolrc",
    "$XDG_CONFIG_HOME/custom_tool/config.yaml",
    "$HOME/.config/custom_tool/settings.json"
]
```

## Advanced Configuration

### Custom Application Detection

Add custom applications to the detection system:

```toml
[applications.default]
"My Custom App" = [
    "~/Library/Application Support/MyCustomApp",
    "~/Library/Preferences/com.company.mycustomapp.plist"
]
```

### Custom CLI Tool Detection

Add custom CLI tools:

```toml
[cli_tools.default]
"my_cli_tool" = [
    "$HOME/.my_cli_toolrc",
    "$XDG_CONFIG_HOME/my_cli_tool/config.yaml"
]
```

### Detection Tuning

```toml
[cli_tools.detection]
# Performance tuning
max_scan_depth = 2
scan_timeout = 15
cache_results = true

# Custom detection patterns
custom_config_patterns = [
    ".*rc$",
    ".*conf$",
    "config.*"
]

# Directories to scan for configs
config_directories = [
    "~/.config",
    "~/.local/share",
    "~/Library/Application Support"
]
```

### Backup Filtering

```toml
[backup]
# File size limits
max_file_size = "100MB"
max_total_size = "10GB"

# File type exclusions
exclude_extensions = [
    ".tmp",
    ".cache",
    ".log"
]

# Path exclusions (regex patterns)
exclude_paths = [
    ".*/node_modules/.*",
    ".*/\\.git/.*",
    ".*/cache/.*"
]
```

### Logging Configuration

```toml
[logging]
# Log level (DEBUG, INFO, WARNING, ERROR)
level = "INFO"

# Log file location
log_file = "~/.myconfig/logs/myconfig.log"

# Enable component-specific logging
component_logging = true

# Log rotation
max_log_size = "10MB"
backup_count = 5
```

### Performance Settings

```toml
[performance]
# Parallel processing
max_workers = 4

# Memory limits
max_memory_usage = "1GB"

# Timeout settings
command_timeout = 300
network_timeout = 30

# Cache settings
enable_cache = true
cache_ttl = 3600  # seconds
```

## Configuration Validation

### Validation Rules

MyConfig automatically validates configuration files:

- TOML syntax validation
- Required field checking
- Path existence verification
- Permission validation
- Circular dependency detection

### Validation Commands

```bash
# Validate current configuration
myconfig --dry-run export

# Validate specific configuration file
myconfig -c custom-config.toml --dry-run export

# Check configuration syntax
myconfig doctor
```

### Common Configuration Errors

1. **Invalid TOML Syntax**
   ```bash
   # Error: Invalid TOML format
   # Fix: Check brackets, quotes, and indentation
   ```

2. **Missing Required Fields**
   ```bash
   # Error: Missing required configuration
   # Fix: Add required fields to config.toml
   ```

3. **Invalid Paths**
   ```bash
   # Error: Configuration path does not exist
   # Fix: Verify paths and permissions
   ```

## Configuration Examples

### Developer Workstation

```toml
# Complete development environment
interactive = false
enable_npm = true
enable_pip_user = true
enable_pipx = true
enable_defaults = true
enable_vscode = true
enable_launchagents = true
enable_mas = true

[applications]
enable = true

[cli_tools]
enable_path_detection = true
enable_homebrew_detection = true
enable_package_manager = true
enable_config_scanning = true

[export]
default_compression = "gzip"
compression_level = 9
include_hidden = true
```

### Server Environment

```toml
# Minimal server configuration
interactive = false
enable_npm = false
enable_pip_user = true
enable_pipx = false
enable_defaults = false
enable_vscode = false
enable_launchagents = true
enable_mas = false

[applications]
enable = false

[cli_tools]
enable_path_detection = true
enable_homebrew_detection = true
enable_package_manager = false
enable_config_scanning = true
```

### Designer Workstation

```toml
# Design-focused configuration
interactive = true
enable_npm = false
enable_pip_user = false
enable_pipx = false
enable_defaults = true
enable_vscode = true
enable_launchagents = true
enable_mas = true

[applications]
enable = true
# Focus on design applications
focus_categories = ["design", "creative", "productivity"]

[cli_tools]
enable_path_detection = false
enable_homebrew_detection = true
enable_package_manager = false
enable_config_scanning = false
```

For more configuration examples and advanced usage patterns, see the [Usage Guide](./usage.md) and [CLI Tools Guide](./cli-tools.md).
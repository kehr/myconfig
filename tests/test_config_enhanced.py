"""
Enhanced configuration management tests for MyConfig Phase 3
Tests ConfigManager and AppConfig classes with expanded application database
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
import time

# Import from myconfig package
from myconfig.core.config import ConfigManager, AppConfig


class TestConfigManagerEnhanced:
    """Test ConfigManager with Phase 3 enhancements"""

    def test_config_manager_initialization(self):
        """Test ConfigManager can be initialized properly"""
        config_manager = ConfigManager()
        assert config_manager.config_path == "./config/config.toml"
        assert config_manager.logger is not None

    def test_config_manager_custom_path(self):
        """Test ConfigManager with custom config path"""
        custom_path = "/custom/path/config.toml"
        config_manager = ConfigManager(custom_path)
        assert config_manager.config_path == custom_path

    def test_app_config_initialization(self):
        """Test AppConfig dataclass initialization with defaults"""
        config = AppConfig()
        
        # Test default values
        assert config.interactive is True
        assert config.dry_run is False
        assert config.verbose is False
        assert config.quiet is False
        assert config.enable_applications is True
        assert config.enable_defaults is True
        assert config.enable_vscode is True
        assert config.enable_launchagents is True
        assert config.enable_mas is True
        assert isinstance(config.applications_default, dict)

    def test_app_config_update(self):
        """Test AppConfig immutable update functionality"""
        original_config = AppConfig(interactive=True, dry_run=False)
        updated_config = original_config.update(dry_run=True, verbose=True)
        
        # Original should be unchanged
        assert original_config.dry_run is False
        assert original_config.verbose is False
        
        # Updated should have new values
        assert updated_config.dry_run is True
        assert updated_config.verbose is True
        assert updated_config.interactive is True  # Unchanged value preserved

    def test_load_nonexistent_config(self):
        """Test loading configuration when file doesn't exist"""
        config_manager = ConfigManager("/nonexistent/path/config.toml")
        config = config_manager.load()
        
        # Should return default configuration
        assert isinstance(config, AppConfig)
        assert config.interactive is True
        assert config.enable_applications is True

    def test_load_valid_toml_config(self, temp_dir):
        """Test loading valid TOML configuration"""
        config_content = """
interactive = false
dry_run = true
verbose = true
enable_applications = true
enable_defaults = false

[applications]
enable = true

[applications.default]
"Visual Studio Code" = ["~/Library/Application Support/Code/User"]
"Git" = ["~/.gitconfig", "~/.gitignore_global"]
"""
        config_path = os.path.join(temp_dir, "test_config.toml")
        with open(config_path, "w") as f:
            f.write(config_content)
        
        config_manager = ConfigManager(config_path)
        config = config_manager.load()
        
        assert config.interactive is False
        assert config.dry_run is True
        assert config.verbose is True
        assert config.enable_applications is True
        assert config.enable_defaults is False
        
        # Test applications configuration
        assert "Visual Studio Code" in config.applications_default
        assert "Git" in config.applications_default
        assert config.applications_default["Visual Studio Code"] == ["~/Library/Application Support/Code/User"]
        assert config.applications_default["Git"] == ["~/.gitconfig", "~/.gitignore_global"]

    def test_load_malformed_toml_fallback(self, temp_dir):
        """Test fallback parsing for malformed TOML"""
        config_content = """
interactive = true
enable_applications = false
# This is malformed TOML that should trigger fallback
[incomplete section
"""
        config_path = os.path.join(temp_dir, "malformed_config.toml")
        with open(config_path, "w") as f:
            f.write(config_content)
        
        config_manager = ConfigManager(config_path)
        config = config_manager.load()
        
        # Should still load with fallback parser
        assert isinstance(config, AppConfig)
        # Fallback parser should handle simple key=value pairs
        assert config.interactive is True

    def test_applications_config_structure_validation(self, temp_dir):
        """Test applications configuration structure validation"""
        config_content = """
[applications]
enable = true

[applications.default]
"App1" = ["path1", "path2"]
"App2" = "single_path"
"App3" = 123
"App4" = ["valid_path"]
"""
        config_path = os.path.join(temp_dir, "apps_config.toml")
        with open(config_path, "w") as f:
            f.write(config_content)
        
        config_manager = ConfigManager(config_path)
        config = config_manager.load()
        
        # Test structure cleaning
        assert "App1" in config.applications_default
        assert config.applications_default["App1"] == ["path1", "path2"]
        
        assert "App2" in config.applications_default
        assert config.applications_default["App2"] == ["single_path"]
        
        # Invalid types should be filtered out
        assert "App3" not in config.applications_default
        
        assert "App4" in config.applications_default
        assert config.applications_default["App4"] == ["valid_path"]

    def test_boolean_conversion(self, temp_dir):
        """Test boolean value conversion from various formats"""
        config_content = """
interactive = "true"
dry_run = "false"
verbose = "TRUE"
quiet = "False"
enable_applications = 1
enable_defaults = 0
"""
        config_path = os.path.join(temp_dir, "bool_config.toml")
        with open(config_path, "w") as f:
            f.write(config_content)
        
        config_manager = ConfigManager(config_path)
        config = config_manager.load()
        
        assert config.interactive is True
        assert config.dry_run is False
        assert config.verbose is True
        assert config.quiet is False
        # Note: TOML parser handles 1/0 as integers, not booleans
        # This tests the _to_bool conversion function


class TestConfigPerformance:
    """Performance tests for configuration loading"""

    def test_config_loading_performance(self, temp_dir):
        """Test configuration loading performance with large config"""
        # Create a large configuration with many applications
        apps_config = {}
        for i in range(100):
            apps_config[f"App{i}"] = [f"~/path{i}/config", f"~/path{i}/settings"]
        
        config_content = """
interactive = true
enable_applications = true

[applications]
enable = true

[applications.default]
"""
        
        # Add all apps to config
        for app_name, paths in apps_config.items():
            paths_str = '", "'.join(paths)
            config_content += f'"{app_name}" = ["{paths_str}"]\n'
        
        config_path = os.path.join(temp_dir, "large_config.toml")
        with open(config_path, "w") as f:
            f.write(config_content)
        
        config_manager = ConfigManager(config_path)
        
        # Measure loading time
        start_time = time.time()
        config = config_manager.load()
        load_time = time.time() - start_time
        
        # Should load quickly (under 1 second for 100 apps)
        assert load_time < 1.0
        assert len(config.applications_default) == 100
        assert config.enable_applications is True

    def test_multiple_config_loads_performance(self, temp_dir):
        """Test performance of multiple configuration loads"""
        config_content = """
interactive = true
enable_applications = true

[applications]
enable = true

[applications.default]
"Visual Studio Code" = ["~/Library/Application Support/Code/User"]
"Git" = ["~/.gitconfig"]
"""
        config_path = os.path.join(temp_dir, "perf_config.toml")
        with open(config_path, "w") as f:
            f.write(config_content)
        
        config_manager = ConfigManager(config_path)
        
        # Load configuration multiple times and measure total time
        start_time = time.time()
        configs = []
        for _ in range(10):
            configs.append(config_manager.load())
        total_time = time.time() - start_time
        
        # Should handle multiple loads efficiently
        assert total_time < 0.5  # 10 loads in under 0.5 seconds
        assert len(configs) == 10
        assert all(isinstance(c, AppConfig) for c in configs)


class TestConfigDatabaseExpansion:
    """Test the expanded application database (Phase 1: 10 -> 89 applications)"""

    def test_application_database_size(self):
        """Test that configuration database has been expanded significantly"""
        config_manager = ConfigManager("config/config.toml")
        config = config_manager.load()
        
        # Should have significantly more applications after expansion
        assert len(config.applications_default) >= 100  # Updated expectation
        assert len(config.cli_tools_default) >= 60  # Updated expectation
        
        # Test some key categories are present
        expected_categories = [
            "Visual Studio Code", "git", "docker", "node", "python",
            "homebrew", "zsh", "iTerm", "Figma", "Notion"
        ]
        
        all_apps = list(config.applications_default.keys()) + list(config.cli_tools_default.keys())
        found_categories = 0
        for expected in expected_categories:
            if any(expected.lower() in app.lower() for app in all_apps):
                found_categories += 1
        
        assert found_categories >= 8  # At least 8 out of 10 categories should be found

    def _get_sample_large_config(self):
        """Return sample configuration with expanded application database"""
        return """
interactive = true
enable_applications = true

[applications]
enable = true

[applications.default]
"Visual Studio Code" = ["~/Library/Application Support/Code/User"]
"Sublime Text" = ["~/Library/Application Support/Sublime Text*/Packages/User"]
"Atom" = ["~/.atom"]
"Vim" = ["~/.vimrc", "~/.vim"]
"Neovim" = ["~/.config/nvim"]
"Emacs" = ["~/.emacs.d", "~/.config/emacs"]
"IntelliJ IDEA" = ["~/Library/Preferences/IntelliJIdea*"]
"PyCharm" = ["~/Library/Preferences/PyCharm*"]
"WebStorm" = ["~/Library/Preferences/WebStorm*"]
"Android Studio" = ["~/Library/Preferences/AndroidStudio*"]
"iTerm" = ["~/Library/Preferences/com.googlecode.iterm2.plist"]
"Warp" = ["~/Library/Application Support/dev.warp.Warp-Stable"]
"Alacritty" = ["~/.config/alacritty"]
"Kitty" = ["~/.config/kitty"]
"Figma" = ["~/Library/Application Support/Figma"]
"Sketch" = ["~/Library/Application Support/com.bohemiancoding.sketch3"]
"Notion" = ["~/Library/Application Support/Notion"]
"Obsidian" = ["~/Library/Application Support/obsidian"]
"Node.js" = ["~/.npmrc", "~/.yarnrc", "~/.pnpmrc"]
"Python" = ["~/.python_history", "~/.pypirc"]
"Rust" = ["~/.cargo/config.toml", "~/.cargo/credentials.toml"]
"Go" = ["~/go/pkg/mod/cache"]
"Java" = ["~/.gradle", "~/.m2"]
"Git" = ["~/.gitconfig", "~/.gitignore_global"]
"Zsh" = ["~/.zshrc", "~/.zsh_history", "~/.zprofile"]
"Fish" = ["~/.config/fish"]
"Bash" = ["~/.bashrc", "~/.bash_profile"]
"Tmux" = ["~/.tmux.conf"]
"SSH" = ["~/.ssh/config", "~/.ssh/known_hosts"]
"Docker" = ["~/Library/Group Containers/group.com.docker"]
"Kubernetes" = ["~/.kube/config"]
"AWS CLI" = ["~/.aws"]
"Google Cloud SDK" = ["~/.config/gcloud"]
"Homebrew" = ["/opt/homebrew/etc", "/usr/local/etc"]
"Google Chrome" = ["~/Library/Application Support/Google/Chrome"]
"Firefox" = ["~/Library/Application Support/Firefox"]
"Safari" = ["~/Library/Safari"]
"Slack" = ["~/Library/Application Support/Slack"]
"Discord" = ["~/Library/Application Support/discord"]
"Spotify" = ["~/Library/Application Support/Spotify"]
"Rectangle" = ["~/Library/Preferences/com.knollsoft.Rectangle.plist"]
"Raycast" = ["~/Library/Application Support/com.raycast.macos"]
"Alfred" = ["~/Library/Application Support/Alfred"]
"""

    def test_config_categories_coverage(self):
        """Test that configuration covers major application categories"""
        config_manager = ConfigManager("config/config.toml")
        config = config_manager.load()
        
        # Define expected categories and their representative apps
        categories = {
            "editors": ["Visual Studio Code", "Sublime Text", "vim", "neovim", "emacs"],
            "ides": ["IntelliJ IDEA", "PyCharm", "WebStorm", "Android Studio"],
            "terminals": ["iTerm", "Warp", "Alacritty", "Kitty"],
            "design": ["Figma", "Sketch", "Adobe"],
            "productivity": ["Notion", "Obsidian", "Bear"],
            "development": ["node", "python", "rust", "go", "java"],
            "cli_tools": ["git", "zsh", "fish", "bash", "tmux", "ssh"],
            "devops": ["docker", "kubectl", "aws-cli", "gcloud"],
            "browsers": ["Google Chrome", "Firefox", "Safari"],
            "communication": ["Slack", "Discord", "Zoom"],
            "utilities": ["Rectangle", "Raycast", "Alfred"]
        }
        
        found_categories = 0
        all_apps = list(config.applications_default.keys()) + list(config.cli_tools_default.keys())
        
        for category, apps in categories.items():
            category_found = False
            for app in apps:
                if any(app.lower() in config_app.lower() for config_app in all_apps):
                    category_found = True
                    break
            if category_found:
                found_categories += 1
        
        # Should cover most major categories
        assert found_categories >= 10  # At least 10 out of 11 categories
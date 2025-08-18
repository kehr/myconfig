"""
Unit tests for configuration management.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, mock_open

from myconfig.core.config import AppConfig, ConfigManager


class TestAppConfig:
    """Test AppConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = AppConfig()
        assert config.interactive is True
        assert config.dry_run is False
        assert config.verbose is False
        assert config.quiet is False
        assert config.enable_mas is True
        assert config.enable_vscode is True
    
    def test_config_update(self):
        """Test configuration update method."""
        config = AppConfig()
        updated = config.update(dry_run=True, verbose=True)
        
        assert updated.dry_run is True
        assert updated.verbose is True
        assert updated.interactive is True  # unchanged
        assert config.dry_run is False  # original unchanged
    
    def test_config_immutability(self):
        """Test that config is immutable."""
        config = AppConfig()
        with pytest.raises(AttributeError):
            config.dry_run = True


class TestConfigManager:
    """Test ConfigManager class."""
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent config file."""
        manager = ConfigManager("/nonexistent/config.toml")
        config = manager.load()
        assert isinstance(config, AppConfig)
        assert config.interactive is True  # default values
    
    def test_load_valid_config(self, sample_config_file):
        """Test loading valid TOML config."""
        manager = ConfigManager(sample_config_file)
        config = manager.load()
        
        assert config.interactive is False
        assert config.dry_run is True
        assert config.enable_mas is False
        assert config.enable_vscode is True
    
    def test_load_invalid_toml(self, temp_dir):
        """Test loading invalid TOML file."""
        invalid_config = os.path.join(temp_dir, "invalid.toml")
        with open(invalid_config, "w") as f:
            f.write("invalid toml content [[[")
        
        manager = ConfigManager(invalid_config)
        config = manager.load()
        # Should return default config on parse error
        assert isinstance(config, AppConfig)
        assert config.interactive is True
    
    @patch('builtins.open', mock_open(read_data=''))
    def test_load_empty_file(self):
        """Test loading empty config file."""
        manager = ConfigManager("empty.toml")
        config = manager.load()
        assert isinstance(config, AppConfig)
    
    def test_profile_config_loading(self, temp_dir):
        """Test loading configuration with profile settings."""
        profile_content = """
[settings]
interactive = false
verbose = true

[components]
enable_mas = false
enable_vscode = false
"""
        profile_path = os.path.join(temp_dir, "profile.toml")
        with open(profile_path, "w") as f:
            f.write(profile_content)
        
        manager = ConfigManager(profile_path)
        config = manager.load()
        
        assert config.interactive is False
        assert config.verbose is True
        assert config.enable_mas is False
        assert config.enable_vscode is False
        assert config.enable_defaults is True  # default value

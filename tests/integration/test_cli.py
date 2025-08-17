"""
Integration tests for CLI interface.
"""
import pytest
import subprocess
import sys
import os
from pathlib import Path


class TestCLIIntegration:
    """Test CLI integration."""
    
    @property
    def cli_path(self):
        """Get path to CLI module."""
        return str(Path(__file__).parent.parent.parent / "src" / "cli.py")
    
    def test_version_command(self):
        """Test --version command."""
        result = subprocess.run(
            [sys.executable, self.cli_path, "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "1.0.0" in result.stdout
    
    def test_help_command(self):
        """Test --help command."""
        result = subprocess.run(
            [sys.executable, self.cli_path, "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "macOS configuration" in result.stdout
        assert "export" in result.stdout
        assert "restore" in result.stdout
    
    def test_doctor_command(self):
        """Test doctor command."""
        result = subprocess.run(
            [sys.executable, self.cli_path, "doctor"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "System health check" in result.stdout
    
    def test_preview_export(self, temp_dir):
        """Test preview export command."""
        result = subprocess.run(
            [sys.executable, self.cli_path, "--preview", "export", temp_dir],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Preview export operation" in result.stdout
    
    def test_profile_list(self):
        """Test profile list command."""
        result = subprocess.run(
            [sys.executable, self.cli_path, "profile", "list"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Available profiles" in result.stdout
    
    def test_invalid_command(self):
        """Test invalid command handling."""
        result = subprocess.run(
            [sys.executable, self.cli_path, "invalid-command"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
    
    def test_dry_run_flag(self, temp_dir):
        """Test dry run flag."""
        result = subprocess.run(
            [sys.executable, self.cli_path, "--dry-run", "export", temp_dir],
            capture_output=True,
            text=True
        )
        # Should complete successfully in dry run mode
        assert result.returncode == 0
    
    def test_verbose_flag(self):
        """Test verbose flag."""
        result = subprocess.run(
            [sys.executable, self.cli_path, "--verbose", "doctor"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
    
    def test_quiet_flag(self):
        """Test quiet flag."""
        result = subprocess.run(
            [sys.executable, self.cli_path, "--quiet", "doctor"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

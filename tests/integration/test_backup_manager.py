"""
Integration tests for BackupManager.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from core.backup import BackupManager
from core.config import AppConfig


class TestBackupManagerIntegration:
    """Test BackupManager integration."""
    
    @pytest.fixture
    def backup_manager(self, mock_config):
        """Create BackupManager instance."""
        return BackupManager(mock_config)
    
    def test_preview_export(self, backup_manager, temp_dir):
        """Test preview export functionality."""
        with patch.object(backup_manager, '_get_available_components') as mock_components:
            mock_component = MagicMock()
            mock_component.name = "TestComponent"
            mock_component.is_available.return_value = True
            mock_component.preview.return_value = {"test": "data"}
            mock_components.return_value = [mock_component]
            
            result = backup_manager.preview_export(temp_dir)
            assert result is True
    
    def test_preview_restore(self, backup_manager, temp_dir):
        """Test preview restore functionality."""
        # Create some test backup files
        os.makedirs(temp_dir, exist_ok=True)
        test_files = ['Brewfile', 'vscode_extensions.txt', 'dotfiles/.zshrc']
        
        for file_path in test_files:
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write("test content")
        
        result = backup_manager.preview_restore(temp_dir)
        assert result is True
    
    @patch('tarfile.open')
    def test_unpack_compressed_backup(self, mock_tarfile, backup_manager, temp_dir):
        """Test unpacking compressed backup."""
        mock_tar = MagicMock()
        mock_tarfile.return_value.__enter__.return_value = mock_tar
        
        archive_path = os.path.join(temp_dir, "backup.tar.gz")
        result = backup_manager.unpack(archive_path, temp_dir)
        
        assert result is not None
        mock_tar.extractall.assert_called_once()
    
    def test_export_dry_run(self, backup_manager, temp_dir):
        """Test export in dry run mode."""
        # Dry run should not create actual files
        with patch.object(backup_manager, '_get_available_components') as mock_components:
            mock_component = MagicMock()
            mock_component.name = "TestComponent"
            mock_component.is_available.return_value = True
            mock_component.export.return_value = True
            mock_components.return_value = [mock_component]
            
            result = backup_manager.export(temp_dir)
            assert result is True
    
    def test_get_available_components(self, backup_manager):
        """Test getting available components."""
        components = backup_manager._get_available_components()
        assert len(components) > 0
        
        # Check that all components have required interface
        for component in components:
            assert hasattr(component, 'name')
            assert hasattr(component, 'is_available')
            assert hasattr(component, 'export')
            assert hasattr(component, 'preview')
    
    def test_create_export_readme(self, backup_manager, temp_dir):
        """Test README generation."""
        test_components = ["Homebrew", "VS Code", "Dotfiles"]
        backup_manager._create_export_readme(temp_dir, test_components)
        
        readme_path = os.path.join(temp_dir, "README.md")
        assert os.path.exists(readme_path)
        
        with open(readme_path, 'r') as f:
            content = f.read()
            assert "MyConfig Backup Export" in content
            for component in test_components:
                assert component in content
    
    def test_create_templated_files(self, backup_manager, temp_dir):
        """Test template-based file creation."""
        test_context = {
            'backup_date': '2024-01-01',
            'hostname': 'test-host',
            'components': ['test1', 'test2']
        }
        
        # This should not raise an exception
        backup_manager._create_templated_files(temp_dir, test_context)
    
    def test_compress_backup(self, backup_manager, temp_dir):
        """Test backup compression."""
        # Create some test files in backup directory
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        archive_path = backup_manager._create_compressed_backup(temp_dir)
        assert archive_path is not None
        assert archive_path.endswith('.tar.gz')
        assert os.path.exists(archive_path)

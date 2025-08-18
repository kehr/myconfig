"""
Enhanced applications detection tests for MyConfig Phase 3
Tests CLI tools detection, GUI application scanning, and path resolution
"""

import pytest
import tempfile
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Import from myconfig package

from myconfig.core.components.applications import ApplicationsComponent
from myconfig.core.config import AppConfig


class TestApplicationsComponentEnhanced:
    """Test ApplicationsComponent with Phase 3 enhancements"""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration with applications enabled"""
        return AppConfig(
            interactive=False,
            dry_run=True,
            enable_applications=True,
            applications_default={
                "Visual Studio Code": ["~/Library/Application Support/Code/User"],
                "Git": ["~/.gitconfig", "~/.gitignore_global"],
                "Node.js": ["~/.npmrc", "~/.yarnrc"],
                "Docker": ["~/Library/Group Containers/group.com.docker"],
                "Zsh": ["~/.zshrc", "~/.zsh_history"],
                "Vim": ["~/.vimrc", "~/.vim"],
                "Tmux": ["~/.tmux.conf"],
                "SSH": ["~/.ssh/config"],
                "Python": ["~/.python_history", "~/.pypirc"],
                "Homebrew": ["/opt/homebrew/etc", "/usr/local/etc"]
            }
        )

    @pytest.fixture
    def mock_executor(self, mock_config):
        """Create mock executor"""
        executor = MagicMock()
        executor.config = mock_config
        executor.confirm = MagicMock(return_value=True)
        executor.run = MagicMock(return_value=0)
        executor.run_output = MagicMock(return_value=(0, ""))
        executor.which = MagicMock(return_value="/usr/bin/tool")
        return executor

    @pytest.fixture
    def apps_component(self, mock_executor):
        """Create ApplicationsComponent instance"""
        return ApplicationsComponent(mock_executor)

    def test_component_initialization(self, apps_component, mock_config):
        """Test ApplicationsComponent initialization"""
        assert apps_component.is_available() is True
        assert apps_component.is_enabled() is True
        assert len(apps_component.known_app_config_map) == len(mock_config.applications_default)
        
        # Test CLI tools detection list
        assert len(apps_component.cli_tools_to_detect) >= 30  # Should have many CLI tools
        assert 'git' in apps_component.cli_tools_to_detect
        assert 'vim' in apps_component.cli_tools_to_detect
        assert 'docker' in apps_component.cli_tools_to_detect
        assert 'node' in apps_component.cli_tools_to_detect

    def test_list_installed_apps(self, apps_component):
        """Test GUI applications listing"""
        with patch('os.path.isdir') as mock_isdir, \
             patch('os.listdir') as mock_listdir:
            
            mock_isdir.return_value = True
            mock_listdir.return_value = [
                'Visual Studio Code.app',
                'Google Chrome.app',
                'iTerm.app',
                'Figma.app',
                'not_an_app.txt'
            ]
            
            apps = apps_component._list_installed_apps()
            
            assert 'Visual Studio Code' in apps
            assert 'Google Chrome' in apps
            assert 'iTerm' in apps
            assert 'Figma' in apps
            assert 'not_an_app' not in apps
            assert len(apps) == 4

    def test_slugify(self, apps_component):
        """Test application name slugification"""
        assert apps_component._slugify("Visual Studio Code") == "visual-studio-code"
        assert apps_component._slugify("IntelliJ IDEA") == "intellij-idea"
        assert apps_component._slugify("Node.js") == "node-js"
        assert apps_component._slugify("AWS CLI") == "aws-cli"

    def test_cli_tool_detection(self, apps_component):
        """Test CLI tool detection using which/command -v"""
        # Test successful detection
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert apps_component._detect_cli_tool('git') is True
            
        # Test failed detection
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            assert apps_component._detect_cli_tool('nonexistent_tool') is False
            
        # Test timeout handling
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('which', 5)
            assert apps_component._detect_cli_tool('slow_tool') is False

    def test_environment_variable_expansion(self, apps_component):
        """Test environment variable expansion in paths"""
        with patch.dict(os.environ, {'HOME': '/Users/testuser', 'CUSTOM_PATH': '/custom'}):
            # Test basic expansion
            assert apps_component._expand_env_vars('~/config') == '/Users/testuser/config'
            assert apps_component._expand_env_vars('$HOME/.config') == '/Users/testuser/.config'
            assert apps_component._expand_env_vars('${CUSTOM_PATH}/app') == '/custom/app'

    def test_config_path_resolution(self, apps_component):
        """Test configuration path resolution with glob patterns"""
        test_paths = [
            '~/.config/app',
            '~/Library/Application Support/App*',
            '/nonexistent/path'
        ]
        
        with patch('os.path.exists') as mock_exists, \
             patch('glob.glob') as mock_glob, \
             patch('os.path.expanduser') as mock_expand, \
             patch('os.path.expandvars') as mock_expandvars:
            
            mock_expand.side_effect = lambda x: x.replace('~', '/Users/testuser')
            mock_expandvars.side_effect = lambda x: x
            mock_glob.return_value = ['/Users/testuser/Library/Application Support/App1']
            mock_exists.side_effect = lambda x: x != '/nonexistent/path'
            
            resolved = apps_component._resolve_config_paths(test_paths)
            
            assert '/Users/testuser/.config/app' in resolved
            assert '/Users/testuser/Library/Application Support/App1' in resolved
            assert '/nonexistent/path' not in resolved

    def test_normalize_tool_name(self, apps_component):
        """Test tool name normalization for matching"""
        assert apps_component._normalize_tool_name('nvim') == 'neovim'
        assert apps_component._normalize_tool_name('code') == 'visual studio code'
        assert apps_component._normalize_tool_name('git') == 'git'
        assert apps_component._normalize_tool_name('node') == 'node.js'
        assert apps_component._normalize_tool_name('kubectl') == 'kubernetes'

    def test_detect_installed_cli_tools(self, apps_component):
        """Test detection of installed CLI tools with configurations"""
        with patch.object(apps_component, '_detect_cli_tool') as mock_detect, \
             patch.object(apps_component, '_resolve_config_paths') as mock_resolve:
            
            # Mock some tools as installed
            mock_detect.side_effect = lambda tool: tool in ['git', 'vim', 'node', 'docker']
            mock_resolve.return_value = ['/Users/testuser/.gitconfig']
            
            detected = apps_component._detect_installed_cli_tools()
            
            # Should find Git configuration (now with source indicator)
            git_keys = [k for k in detected.keys() if 'git' in k.lower()]
            assert len(git_keys) > 0, f"Expected git configuration, got: {list(detected.keys())}"
            git_key = git_keys[0]  # Get the first git-related key
            assert detected[git_key] == ['/Users/testuser/.gitconfig']

    def test_detect_package_manager_tools(self, apps_component):
        """Test detection of tools installed via package managers"""
        # Test Homebrew detection
        apps_component.executor.which.return_value = "/opt/homebrew/bin/brew"
        apps_component.executor.run_output.return_value = (0, "git\nvim\nnode\ndocker")
        
        with patch.object(apps_component, '_resolve_config_paths') as mock_resolve:
            mock_resolve.return_value = ['/Users/testuser/.gitconfig']
            
            detected = apps_component._detect_package_manager_tools()
            
            # Should detect tools installed via brew
            assert any('brew' in key for key in detected.keys())

    def test_backup_cli_config(self, apps_component, temp_dir):
        """Test CLI configuration backup functionality"""
        # Create test files
        test_file = os.path.join(temp_dir, 'test_config')
        test_dir = os.path.join(temp_dir, 'test_config_dir')
        test_link = os.path.join(temp_dir, 'test_link')
        
        with open(test_file, 'w') as f:
            f.write('test config content')
        
        os.makedirs(test_dir)
        with open(os.path.join(test_dir, 'nested_config'), 'w') as f:
            f.write('nested config')
        
        os.symlink(test_file, test_link)
        
        backup_dir = os.path.join(temp_dir, 'backup')
        os.makedirs(backup_dir)
        
        # Test file backup
        assert apps_component._backup_cli_config(test_file, backup_dir) is True
        assert os.path.exists(os.path.join(backup_dir, 'test_config'))
        
        # Test directory backup
        assert apps_component._backup_cli_config(test_dir, backup_dir) is True
        assert os.path.exists(os.path.join(backup_dir, 'test_config_dir'))
        
        # Test symlink backup
        assert apps_component._backup_cli_config(test_link, backup_dir) is True
        assert os.path.islink(os.path.join(backup_dir, 'test_link'))

    def test_export_functionality(self, apps_component, temp_dir):
        """Test export functionality with CLI and GUI detection"""
        with patch.object(apps_component, '_list_installed_apps') as mock_gui, \
             patch.object(apps_component, '_detect_installed_cli_tools') as mock_cli, \
             patch.object(apps_component, '_detect_package_manager_tools') as mock_pkg, \
             patch.object(apps_component, '_generate_install_hints') as mock_hints:
            
            mock_gui.return_value = ['Visual Studio Code', 'Google Chrome']
            mock_cli.return_value = {'Git': ['/Users/testuser/.gitconfig']}
            mock_pkg.return_value = {'Node.js (brew)': ['/Users/testuser/.npmrc']}
            
            result = apps_component.export(temp_dir)
            
            assert result is True
            
            # Check that files were created
            apps_dir = os.path.join(temp_dir, 'Applications')
            assert os.path.exists(apps_dir)
            
            # Check GUI apps list
            gui_list = os.path.join(apps_dir, 'Applications_list.txt')
            assert os.path.exists(gui_list)
            
            # Check CLI tools list
            cli_list = os.path.join(apps_dir, 'CLI_tools_list.txt')
            assert os.path.exists(cli_list)

    def test_generate_install_hints(self, apps_component, temp_dir):
        """Test installation hints generation"""
        apps_component.executor.which.side_effect = lambda cmd: f"/usr/bin/{cmd}" if cmd in ['brew', 'mas', 'code', 'npm'] else None
        
        # Mock command outputs
        def mock_run_output(cmd):
            if 'brew list --formula' in cmd:
                return (0, 'git\nvim\nnode')
            elif 'brew list --cask' in cmd:
                return (0, 'visual-studio-code\ngoogle-chrome')
            elif 'mas list' in cmd:
                return (0, '12345 Xcode\n67890 TestFlight')
            elif 'code --list-extensions' in cmd:
                return (0, 'ms-python.python\nms-vscode.cpptools')
            elif 'npm list -g' in cmd:
                return (0, '/usr/local/lib/node_modules/typescript\n/usr/local/lib/node_modules/eslint')
            return (1, '')
        
        apps_component.executor.run_output.side_effect = mock_run_output
        
        apps_component._generate_install_hints(temp_dir)
        
        install_script = os.path.join(temp_dir, 'INSTALL_COMMANDS.sh')
        assert os.path.exists(install_script)
        
        with open(install_script, 'r') as f:
            content = f.read()
            assert 'brew install git' in content
            assert 'brew install --cask visual-studio-code' in content
            assert 'mas install 12345' in content
            assert 'code --install-extension ms-python.python' in content

    def test_preview_export(self, apps_component):
        """Test export preview functionality"""
        with patch.object(apps_component, '_list_installed_apps') as mock_gui, \
             patch.object(apps_component, '_detect_installed_cli_tools') as mock_cli, \
             patch.object(apps_component, '_detect_package_manager_tools') as mock_pkg:
            
            mock_gui.return_value = ['Visual Studio Code', 'Google Chrome']
            mock_cli.return_value = {'Git': ['/Users/testuser/.gitconfig']}
            mock_pkg.return_value = {'Node.js (brew)': ['/Users/testuser/.npmrc']}
            
            preview = apps_component.preview_export('/tmp')
            
            assert len(preview) > 0
            assert any('GUI Applications' in item for item in preview)
            assert any('CLI Tools detected' in item for item in preview)

    def test_preview_restore(self, apps_component, temp_dir):
        """Test restore preview functionality"""
        # Create mock backup structure
        apps_dir = os.path.join(temp_dir, 'Applications')
        os.makedirs(apps_dir)
        
        # Create some backup directories
        os.makedirs(os.path.join(apps_dir, 'GUI_visual-studio-code'))
        os.makedirs(os.path.join(apps_dir, 'CLI_git'))
        os.makedirs(os.path.join(apps_dir, 'legacy_app'))
        
        # Create install script
        with open(os.path.join(apps_dir, 'INSTALL_COMMANDS.sh'), 'w') as f:
            f.write('#!/bin/bash\necho "Install commands"')
        
        preview = apps_component.preview_restore(temp_dir)
        
        assert len(preview) > 0
        assert any('GUI application configuration' in item for item in preview)
        assert any('CLI tool configuration' in item for item in preview)
        assert any('legacy configuration' in item for item in preview)
        assert any('Installation commands script' in item for item in preview)


class TestCLIToolsDetection:
    """Specific tests for CLI tools detection (Phase 2 feature)"""

    @pytest.fixture
    def cli_component(self):
        """Create component for CLI testing"""
        mock_executor = MagicMock()
        mock_executor.config = AppConfig(
            enable_applications=True,
            applications_default={
                "Git": ["~/.gitconfig", "~/.gitignore_global"],
                "Vim": ["~/.vimrc", "~/.vim"],
                "Zsh": ["~/.zshrc", "~/.zsh_history"],
                "Node.js": ["~/.npmrc", "~/.yarnrc"],
                "Docker": ["~/Library/Group Containers/group.com.docker"],
                "SSH": ["~/.ssh/config", "~/.ssh/known_hosts"],
                "Tmux": ["~/.tmux.conf"],
                "Python": ["~/.python_history", "~/.pypirc"],
                "AWS CLI": ["~/.aws"],
                "Homebrew": ["/opt/homebrew/etc"],
                "Starship": ["~/.config/starship.toml"]
            }
        )
        return ApplicationsComponent(mock_executor)

    def test_cli_tools_coverage(self, cli_component):
        """Test that CLI tools detection covers major tool categories"""
        expected_tools = {
            'git', 'vim', 'nvim', 'tmux', 'zsh', 'fish', 'bash',
            'node', 'npm', 'yarn', 'python', 'pip', 'docker',
            'kubectl', 'terraform', 'aws', 'brew', 'code'
        }
        
        detected_tools = cli_component.cli_tools_to_detect
        
        # Should detect most common CLI tools
        found_tools = expected_tools.intersection(detected_tools)
        assert len(found_tools) >= 15  # At least 15 out of 19 tools

    def test_tool_detection_methods(self, cli_component):
        """Test different CLI tool detection methods"""
        with patch('subprocess.run') as mock_run:
            # Test 'which' success
            mock_run.return_value = MagicMock(returncode=0)
            assert cli_component._detect_cli_tool('git') is True
            
            # Test 'which' failure, 'command -v' success
            mock_run.side_effect = [
                MagicMock(returncode=1),  # which fails
                MagicMock(returncode=0)   # command -v succeeds
            ]
            assert cli_component._detect_cli_tool('git') is True
            
            # Test both methods fail
            mock_run.side_effect = [
                MagicMock(returncode=1),  # which fails
                MagicMock(returncode=1)   # command -v fails
            ]
            assert cli_component._detect_cli_tool('nonexistent') is False

    def test_package_manager_integration(self, cli_component):
        """Test integration with package managers for tool detection"""
        # Test Homebrew integration
        cli_component.executor.which.return_value = "/opt/homebrew/bin/brew"
        cli_component.executor.run_output.return_value = (0, "git\nvim\nnode\ntmux\nstarship")
        
        with patch.object(cli_component, '_resolve_config_paths') as mock_resolve:
            mock_resolve.return_value = ['/Users/testuser/.gitconfig']
            
            detected = cli_component._detect_package_manager_tools()
            
            # Should detect tools and map to configurations
            assert len(detected) > 0
            
        # Test npm integration
        cli_component.executor.run_output.return_value = (0, "/usr/local/lib/node_modules/typescript\n/usr/local/lib/node_modules/eslint")
        
        detected_npm = cli_component._detect_package_manager_tools()
        # Should handle npm global packages

    def test_path_resolution_edge_cases(self, cli_component):
        """Test edge cases in path resolution"""
        # Test with environment variables
        test_paths = [
            "$HOME/.config/app",
            "${XDG_CONFIG_HOME:-$HOME/.config}/app",
            "~/Library/Application Support/App*/Settings",
            "/absolute/path/config"
        ]
        
        with patch.dict(os.environ, {'HOME': '/Users/testuser', 'XDG_CONFIG_HOME': '/Users/testuser/.config'}):
            with patch('os.path.exists') as mock_exists, \
                 patch('glob.glob') as mock_glob:
                
                mock_exists.return_value = True
                mock_glob.return_value = ['/Users/testuser/Library/Application Support/App1/Settings']
                
                resolved = cli_component._resolve_config_paths(test_paths)
                
                assert len(resolved) > 0
                assert any('/Users/testuser' in path for path in resolved)

    def test_cli_tool_configuration_mapping(self, cli_component):
        """Test mapping between detected CLI tools and their configurations"""
        # Mock tool detection
        with patch.object(cli_component, '_detect_cli_tool') as mock_detect:
            mock_detect.side_effect = lambda tool: tool in ['git', 'vim', 'zsh', 'node', 'docker']
            
            with patch.object(cli_component, '_resolve_config_paths') as mock_resolve:
                mock_resolve.side_effect = lambda paths: [p.replace('~', '/Users/testuser') for p in paths if 'git' in p or 'vim' in p]
                
                detected = cli_component._detect_installed_cli_tools()
                
                # Should map tools to their configuration paths (now with source indicator)
                git_keys = [k for k in detected.keys() if 'git' in k.lower()]
                assert len(git_keys) > 0, f"Expected git configuration, got: {list(detected.keys())}"
                git_key = git_keys[0]  # Get the first git-related key
                assert len(detected[git_key]) > 0
                assert any('.gitconfig' in path for path in detected[git_key])
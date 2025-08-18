"""
Performance benchmark tests for MyConfig Phase 3
Measures configuration loading, CLI/GUI detection speed, and performance comparisons
"""

import pytest
import tempfile
import os
import time
import statistics
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add myconfig to path for imports
# Import from myconfig package

from myconfig.core.config import ConfigManager, AppConfig
from myconfig.core.components.applications import ApplicationsComponent


class TestConfigurationPerformance:
    """Performance tests for configuration management"""

    def test_config_loading_speed(self, temp_dir):
        """Test configuration loading performance with various sizes"""
        # Test small config (baseline)
        small_config = """
interactive = true
enable_applications = true

[applications]
enable = true

[applications.default]
"Git" = ["~/.gitconfig"]
"Vim" = ["~/.vimrc"]
"""
        
        small_config_path = os.path.join(temp_dir, "small_config.toml")
        with open(small_config_path, "w") as f:
            f.write(small_config)
        
        # Measure small config loading
        config_manager = ConfigManager(small_config_path)
        times = []
        for _ in range(10):
            start = time.time()
            config_manager.load()
            times.append(time.time() - start)
        
        small_avg_time = statistics.mean(times)
        assert small_avg_time < 0.1  # Should load in under 100ms
        
        # Test large config (89 applications)
        large_config = self._generate_large_config()
        large_config_path = os.path.join(temp_dir, "large_config.toml")
        with open(large_config_path, "w") as f:
            f.write(large_config)
        
        # Measure large config loading
        large_config_manager = ConfigManager(large_config_path)
        large_times = []
        for _ in range(10):
            start = time.time()
            large_config_manager.load()
            large_times.append(time.time() - start)
        
        large_avg_time = statistics.mean(large_times)
        assert large_avg_time < 0.5  # Should load in under 500ms even with 89 apps
        
        # Performance should scale reasonably
        performance_ratio = large_avg_time / small_avg_time
        assert performance_ratio < 10  # Large config shouldn't be more than 10x slower

    def test_config_parsing_performance(self, temp_dir):
        """Test TOML parsing performance vs fallback parsing"""
        config_content = self._generate_large_config()
        config_path = os.path.join(temp_dir, "perf_config.toml")
        with open(config_path, "w") as f:
            f.write(config_content)
        
        config_manager = ConfigManager(config_path)
        
        # Test TOML parsing performance
        toml_times = []
        for _ in range(5):
            start = time.time()
            config_manager._parse_toml(config_path)
            toml_times.append(time.time() - start)
        
        toml_avg_time = statistics.mean(toml_times)
        
        # Test fallback parsing performance
        fallback_times = []
        for _ in range(5):
            start = time.time()
            config_manager._fallback_parse(config_path)
            fallback_times.append(time.time() - start)
        
        fallback_avg_time = statistics.mean(fallback_times)
        
        # TOML parsing should be reasonably fast
        assert toml_avg_time < 0.2
        assert fallback_avg_time < 0.3

    def test_memory_usage_during_config_loading(self, temp_dir):
        """Test memory efficiency during configuration loading"""
        import psutil
        import gc
        
        # Get baseline memory
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss
        
        # Load large configuration multiple times
        large_config = self._generate_large_config()
        config_path = os.path.join(temp_dir, "memory_test_config.toml")
        with open(config_path, "w") as f:
            f.write(large_config)
        
        config_manager = ConfigManager(config_path)
        configs = []
        
        for i in range(20):
            configs.append(config_manager.load())
            if i % 5 == 0:  # Check memory every 5 iterations
                current_memory = process.memory_info().rss
                memory_increase = current_memory - baseline_memory
                # Memory increase should be reasonable (less than 50MB for 20 configs)
                assert memory_increase < 50 * 1024 * 1024
        
        # Clean up
        del configs
        gc.collect()

    def _generate_large_config(self):
        """Generate a large configuration with 89 applications"""
        apps = [
            ("Visual Studio Code", ["~/Library/Application Support/Code/User"]),
            ("Sublime Text", ["~/Library/Application Support/Sublime Text*/Packages/User"]),
            ("Atom", ["~/.atom"]),
            ("Brackets", ["~/Library/Application Support/Brackets/extensions/user"]),
            ("Vim", ["~/.vimrc", "~/.vim"]),
            ("Neovim", ["~/.config/nvim"]),
            ("Emacs", ["~/.emacs.d", "~/.config/emacs"]),
            ("Android Studio", ["~/Library/Preferences/AndroidStudio*"]),
            ("IntelliJ IDEA", ["~/Library/Preferences/IntelliJIdea*"]),
            ("PyCharm", ["~/Library/Preferences/PyCharm*"]),
            ("WebStorm", ["~/Library/Preferences/WebStorm*"]),
            ("PhpStorm", ["~/Library/Preferences/PhpStorm*"]),
            ("CLion", ["~/Library/Preferences/CLion*"]),
            ("GoLand", ["~/Library/Preferences/GoLand*"]),
            ("RustRover", ["~/Library/Preferences/RustRover*"]),
            ("Xcode", ["~/Library/Developer/Xcode/UserData"]),
            ("iTerm", ["~/Library/Preferences/com.googlecode.iterm2.plist"]),
            ("Warp", ["~/Library/Application Support/dev.warp.Warp-Stable"]),
            ("Alacritty", ["~/.config/alacritty"]),
            ("Kitty", ["~/.config/kitty"]),
            ("Hyper", ["~/.hyper.js"]),
            ("Terminal", ["~/Library/Preferences/com.apple.Terminal.plist"]),
            ("Figma", ["~/Library/Application Support/Figma"]),
            ("Sketch", ["~/Library/Application Support/com.bohemiancoding.sketch3"]),
            ("Adobe Photoshop", ["~/Library/Preferences/Adobe Photoshop*"]),
            ("Adobe Illustrator", ["~/Library/Preferences/Adobe Illustrator*"]),
            ("Notion", ["~/Library/Application Support/Notion"]),
            ("Obsidian", ["~/Library/Application Support/obsidian"]),
            ("Logseq", ["~/Library/Application Support/Logseq"]),
            ("Bear", ["~/Library/Containers/net.shinyfrog.bear/Data/Library/Application Support/database.sqlite"]),
            ("Node.js", ["~/.npmrc", "~/.yarnrc", "~/.pnpmrc"]),
            ("Python", ["~/.python_history", "~/.pypirc"]),
            ("Rust", ["~/.cargo/config.toml", "~/.cargo/credentials.toml"]),
            ("Go", ["~/go/pkg/mod/cache"]),
            ("Java", ["~/.gradle", "~/.m2"]),
            ("PHP", ["~/.composer"]),
            ("Ruby", ["~/.gemrc", "~/.bundle"]),
            ("Git", ["~/.gitconfig", "~/.gitignore_global"]),
            ("Zsh", ["~/.zshrc", "~/.zsh_history"]),
            ("Fish", ["~/.config/fish"]),
            ("Bash", ["~/.bashrc", "~/.bash_profile"]),
            ("Tmux", ["~/.tmux.conf"]),
            ("SSH", ["~/.ssh/config", "~/.ssh/known_hosts"]),
            ("Docker", ["~/Library/Group Containers/group.com.docker"]),
            ("Kubernetes", ["~/.kube/config"]),
            ("AWS CLI", ["~/.aws"]),
            ("Google Cloud SDK", ["~/.config/gcloud"]),
            ("Homebrew", ["/opt/homebrew/etc", "/usr/local/etc"]),
            ("Google Chrome", ["~/Library/Application Support/Google/Chrome"]),
            ("Firefox", ["~/Library/Application Support/Firefox"]),
            ("Safari", ["~/Library/Safari"]),
            ("Slack", ["~/Library/Application Support/Slack"]),
            ("Discord", ["~/Library/Application Support/discord"]),
            ("Spotify", ["~/Library/Application Support/Spotify"]),
            ("Rectangle", ["~/Library/Preferences/com.knollsoft.Rectangle.plist"]),
            ("Raycast", ["~/Library/Application Support/com.raycast.macos"]),
            ("Alfred", ["~/Library/Application Support/Alfred"])
        ]
        
        # Add more apps to reach 89
        for i in range(len(apps), 89):
            apps.append((f"TestApp{i}", [f"~/Library/Application Support/TestApp{i}"]))
        
        config_content = """
interactive = true
enable_applications = true

[applications]
enable = true

[applications.default]
"""
        
        for app_name, paths in apps:
            paths_str = '", "'.join(paths)
            config_content += f'"{app_name}" = ["{paths_str}"]\n'
        
        return config_content


class TestApplicationDetectionPerformance:
    """Performance tests for application detection"""

    @pytest.fixture
    def perf_component(self):
        """Create ApplicationsComponent for performance testing"""
        mock_executor = MagicMock()
        mock_executor.config = AppConfig(
            enable_applications=True,
            applications_default=self._get_large_app_config()
        )
        mock_executor.confirm = MagicMock(return_value=True)
        mock_executor.run = MagicMock(return_value=0)
        mock_executor.run_output = MagicMock(return_value=(0, ""))
        mock_executor.which = MagicMock(return_value="/usr/bin/tool")
        return ApplicationsComponent(mock_executor)

    def _get_large_app_config(self):
        """Get large application configuration for testing"""
        return {
            "Visual Studio Code": ["~/Library/Application Support/Code/User"],
            "Git": ["~/.gitconfig", "~/.gitignore_global"],
            "Node.js": ["~/.npmrc", "~/.yarnrc"],
            "Docker": ["~/Library/Group Containers/group.com.docker"],
            "Zsh": ["~/.zshrc", "~/.zsh_history"],
            "Vim": ["~/.vimrc", "~/.vim"],
            "Python": ["~/.python_history", "~/.pypirc"],
            "Homebrew": ["/opt/homebrew/etc"],
            "IntelliJ IDEA": ["~/Library/Preferences/IntelliJIdea*"],
            "PyCharm": ["~/Library/Preferences/PyCharm*"],
            "WebStorm": ["~/Library/Preferences/WebStorm*"],
            "iTerm": ["~/Library/Preferences/com.googlecode.iterm2.plist"],
            "Figma": ["~/Library/Application Support/Figma"],
            "Notion": ["~/Library/Application Support/Notion"],
            "Slack": ["~/Library/Application Support/Slack"]
        }

    def test_gui_app_detection_speed(self, perf_component):
        """Test GUI application detection performance"""
        with patch('os.path.isdir') as mock_isdir, \
             patch('os.listdir') as mock_listdir:
            
            mock_isdir.return_value = True
            # Simulate large number of applications
            mock_apps = [f"App{i}.app" for i in range(200)]
            mock_listdir.return_value = mock_apps
            
            times = []
            for _ in range(10):
                start = time.time()
                apps = perf_component._list_installed_apps()
                times.append(time.time() - start)
            
            avg_time = statistics.mean(times)
            assert avg_time < 0.1  # Should detect 200 apps in under 100ms
            assert len(apps) == 200

    def test_cli_tool_detection_speed(self, perf_component):
        """Test CLI tool detection performance"""
        # Mock subprocess calls to be fast
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Test detection of all CLI tools
            start = time.time()
            results = {}
            for tool in perf_component.cli_tools_to_detect:
                results[tool] = perf_component._detect_cli_tool(tool)
            detection_time = time.time() - start
            
            # Should detect all tools quickly
            assert detection_time < 2.0  # All CLI tools in under 2 seconds
            assert len(results) >= 30  # Should test many tools

    def test_path_resolution_performance(self, perf_component):
        """Test configuration path resolution performance"""
        # Create many test paths with various patterns
        test_paths = []
        for i in range(100):
            test_paths.extend([
                f"~/config{i}",
                f"~/Library/App{i}/*",
                f"~/.config/app{i}",
                f"/usr/local/etc/app{i}"
            ])
        
        with patch('os.path.exists') as mock_exists, \
             patch('glob.glob') as mock_glob, \
             patch('os.path.expanduser') as mock_expand, \
             patch('os.path.expandvars') as mock_expandvars:
            
            mock_expand.side_effect = lambda x: x.replace('~', '/Users/testuser')
            mock_expandvars.side_effect = lambda x: x
            mock_glob.return_value = ['/Users/testuser/Library/App1/config']
            mock_exists.return_value = True
            
            start = time.time()
            resolved = perf_component._resolve_config_paths(test_paths)
            resolution_time = time.time() - start
            
            # Should resolve 400 paths quickly
            assert resolution_time < 1.0
            assert len(resolved) > 0

    def test_export_performance(self, perf_component, temp_dir):
        """Test export operation performance"""
        with patch.object(perf_component, '_list_installed_apps') as mock_gui, \
             patch.object(perf_component, '_detect_installed_cli_tools') as mock_cli, \
             patch.object(perf_component, '_detect_package_manager_tools') as mock_pkg, \
             patch.object(perf_component, '_generate_install_hints') as mock_hints:
            
            # Mock large number of detected applications
            mock_gui.return_value = [f"App{i}" for i in range(50)]
            mock_cli.return_value = {f"CLI{i}": [f"/path/to/cli{i}"] for i in range(25)}
            mock_pkg.return_value = {f"PKG{i}": [f"/path/to/pkg{i}"] for i in range(25)}
            
            start = time.time()
            result = perf_component.export(temp_dir)
            export_time = time.time() - start
            
            # Should export 100 applications quickly
            assert export_time < 5.0  # Under 5 seconds for 100 apps
            assert result is True

    def test_concurrent_detection_performance(self, perf_component):
        """Test performance when running multiple detection operations"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def detect_gui():
            with patch('os.path.isdir', return_value=True), \
                 patch('os.listdir', return_value=[f"App{i}.app" for i in range(50)]):
                start = time.time()
                apps = perf_component._list_installed_apps()
                results_queue.put(('gui', time.time() - start, len(apps)))
        
        def detect_cli():
            with patch('subprocess.run', return_value=MagicMock(returncode=0)):
                start = time.time()
                detected = 0
                for tool in list(perf_component.cli_tools_to_detect)[:20]:  # Test subset
                    if perf_component._detect_cli_tool(tool):
                        detected += 1
                results_queue.put(('cli', time.time() - start, detected))
        
        # Run detections concurrently
        gui_thread = threading.Thread(target=detect_gui)
        cli_thread = threading.Thread(target=detect_cli)
        
        start_time = time.time()
        gui_thread.start()
        cli_thread.start()
        
        gui_thread.join()
        cli_thread.join()
        total_time = time.time() - start_time
        
        # Collect results
        gui_result = None
        cli_result = None
        while not results_queue.empty():
            result_type, duration, count = results_queue.get()
            if result_type == 'gui':
                gui_result = (duration, count)
            elif result_type == 'cli':
                cli_result = (duration, count)
        
        # Both operations should complete quickly
        assert total_time < 3.0
        assert gui_result is not None
        assert cli_result is not None
        assert gui_result[1] == 50  # 50 GUI apps detected
        assert cli_result[1] > 0    # Some CLI tools detected


class TestPerformanceComparisons:
    """Compare performance between different implementation approaches"""

    def test_old_vs_new_config_loading(self, temp_dir):
        """Compare old (simple) vs new (enhanced) configuration loading"""
        # Simulate old simple config (10 apps)
        old_config = """
interactive = true
enable_applications = true

[applications.default]
"Git" = ["~/.gitconfig"]
"Vim" = ["~/.vimrc"]
"Node.js" = ["~/.npmrc"]
"Docker" = ["~/Library/Group Containers/group.com.docker"]
"Visual Studio Code" = ["~/Library/Application Support/Code/User"]
"iTerm" = ["~/Library/Preferences/com.googlecode.iterm2.plist"]
"Homebrew" = ["/opt/homebrew/etc"]
"Zsh" = ["~/.zshrc"]
"Python" = ["~/.pypirc"]
"Slack" = ["~/Library/Application Support/Slack"]
"""
        
        # New enhanced config (89 apps)
        new_config = self._generate_enhanced_config()
        
        # Test old config performance
        old_config_path = os.path.join(temp_dir, "old_config.toml")
        with open(old_config_path, "w") as f:
            f.write(old_config)
        
        old_manager = ConfigManager(old_config_path)
        old_times = []
        for _ in range(10):
            start = time.time()
            old_config_obj = old_manager.load()
            old_times.append(time.time() - start)
        
        # Test new config performance
        new_config_path = os.path.join(temp_dir, "new_config.toml")
        with open(new_config_path, "w") as f:
            f.write(new_config)
        
        new_manager = ConfigManager(new_config_path)
        new_times = []
        for _ in range(10):
            start = time.time()
            new_config_obj = new_manager.load()
            new_times.append(time.time() - start)
        
        old_avg = statistics.mean(old_times)
        new_avg = statistics.mean(new_times)
        
        # Performance comparison
        assert len(old_config_obj.applications_default) == 10
        assert len(new_config_obj.applications_default) >= 80  # Should have many more apps
        
        # New config should still be reasonably fast despite 8x more data
        performance_degradation = new_avg / old_avg
        assert performance_degradation < 5  # Less than 5x slower for 8x more data

    def test_detection_scalability(self):
        """Test how detection performance scales with number of applications"""
        mock_executor = MagicMock()
        mock_executor.confirm = MagicMock(return_value=True)
        
        # Test with different config sizes
        sizes = [10, 25, 50, 89]
        times = []
        
        for size in sizes:
            # Create config with specified size
            config_dict = {}
            for i in range(size):
                config_dict[f"App{i}"] = [f"~/config{i}"]
            
            mock_executor.config = AppConfig(
                enable_applications=True,
                applications_default=config_dict
            )
            
            component = ApplicationsComponent(mock_executor)
            
            # Measure initialization time
            start = time.time()
            # Simulate some operations
            component.is_enabled()
            len(component.known_app_config_map)
            init_time = time.time() - start
            
            times.append((size, init_time))
        
        # Performance should scale reasonably
        for i in range(1, len(times)):
            size_ratio = times[i][0] / times[i-1][0]
            time_ratio = times[i][1] / times[i-1][1] if times[i-1][1] > 0 else 1
            
            # Time increase should be less than size increase
            assert time_ratio < size_ratio * 2

    def _generate_enhanced_config(self):
        """Generate enhanced configuration with 89 applications"""
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
"Emacs" = ["~/.emacs.d"]
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
"Node.js" = ["~/.npmrc", "~/.yarnrc"]
"Python" = ["~/.python_history", "~/.pypirc"]
"Rust" = ["~/.cargo/config.toml"]
"Go" = ["~/go/pkg/mod/cache"]
"Java" = ["~/.gradle", "~/.m2"]
"Git" = ["~/.gitconfig", "~/.gitignore_global"]
"Zsh" = ["~/.zshrc", "~/.zsh_history"]
"Fish" = ["~/.config/fish"]
"Bash" = ["~/.bashrc", "~/.bash_profile"]
"Tmux" = ["~/.tmux.conf"]
"SSH" = ["~/.ssh/config"]
"Docker" = ["~/Library/Group Containers/group.com.docker"]
"Kubernetes" = ["~/.kube/config"]
"AWS CLI" = ["~/.aws"]
"Google Cloud SDK" = ["~/.config/gcloud"]
"Homebrew" = ["/opt/homebrew/etc"]
"Google Chrome" = ["~/Library/Application Support/Google/Chrome"]
"Firefox" = ["~/Library/Application Support/Firefox"]
"Safari" = ["~/Library/Safari"]
"Slack" = ["~/Library/Application Support/Slack"]
"Discord" = ["~/Library/Application Support/discord"]
"Spotify" = ["~/Library/Application Support/Spotify"]
"Rectangle" = ["~/Library/Preferences/com.knollsoft.Rectangle.plist"]
"Raycast" = ["~/Library/Application Support/com.raycast.macos"]
"Alfred" = ["~/Library/Application Support/Alfred"]
""" + "\n".join([f'"TestApp{i}" = ["~/Library/Application Support/TestApp{i}"]' for i in range(40, 89)])


class TestMemoryEfficiency:
    """Test memory usage and efficiency"""

    def test_config_memory_footprint(self, temp_dir):
        """Test memory footprint of loaded configurations"""
        import sys
        
        # Test small config memory usage
        small_config = AppConfig()
        small_size = sys.getsizeof(small_config)
        
        # Test large config memory usage
        large_app_dict = {f"App{i}": [f"path{i}"] for i in range(89)}
        large_config = AppConfig(applications_default=large_app_dict)
        large_size = sys.getsizeof(large_config)
        
        # Memory usage should be reasonable
        memory_increase = large_size - small_size
        assert memory_increase < 50000  # Less than 50KB increase for 89 apps

    def test_component_memory_efficiency(self):
        """Test ApplicationsComponent memory efficiency"""
        import sys
        
        # Create component with large configuration
        mock_executor = MagicMock()
        large_config = {f"App{i}": [f"path{i}"] for i in range(89)}
        mock_executor.config = AppConfig(applications_default=large_config)
        
        component = ApplicationsComponent(mock_executor)
        
        # Check memory usage of component
        component_size = sys.getsizeof(component)
        config_map_size = sys.getsizeof(component.known_app_config_map)
        cli_tools_size = sys.getsizeof(component.cli_tools_to_detect)
        
        # Should be reasonably sized
        assert component_size < 10000  # Component itself should be small
        assert config_map_size < 50000  # Config map should be reasonable
        assert cli_tools_size < 5000   # CLI tools set should be small
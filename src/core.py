"""
Core classes for MyConfig - Configuration management, command execution and component abstractions
"""
from __future__ import annotations
import os, sys, subprocess, shlex, logging, pathlib
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, replace
from .logger import log_section, log_separator, log_success, confirm_action

# Handle TOML library imports
try:
    import tomllib  # py311+
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError("需要安装 tomli 库: pip install tomli")


@dataclass(frozen=True)
class AppConfig:
    """Application configuration with immutable settings"""
    interactive: bool = True
    dry_run: bool = False
    verbose: bool = False
    quiet: bool = False
    enable_npm: bool = False
    enable_pip_user: bool = False
    enable_pipx: bool = False
    enable_defaults: bool = True
    enable_vscode: bool = True
    enable_launchagents: bool = True
    enable_mas: bool = True
    enable_incremental: bool = False
    base_backup_dir: str = ""
    defaults_domains_file: str = "config/defaults/domains.txt"
    defaults_exclude_file: str = "config/defaults/exclude.txt"
    
    def update(self, **kwargs) -> AppConfig:
        """Create a new config with updated values"""
        return replace(self, **kwargs)


class ConfigManager:
    """Manages configuration loading, validation and updates"""
    
    def __init__(self, config_path: str = "./config/config.toml"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
    
    def load(self) -> AppConfig:
        """Load configuration from TOML file"""
        data = self._parse_toml(self.config_path)
        
        def get_bool(key: str, default: bool) -> bool:
            return str(data.get(key, default)).lower() == "true"
        
        def get_str(key: str, default: str) -> str:
            return str(data.get(key, default))
        
        return AppConfig(
            interactive=get_bool("interactive", True),
            enable_npm=get_bool("enable_npm", False),
            enable_pip_user=get_bool("enable_pip_user", False),
            enable_pipx=get_bool("enable_pipx", False),
            enable_defaults=get_bool("enable_defaults", True),
            enable_vscode=get_bool("enable_vscode", True),
            enable_launchagents=get_bool("enable_launchagents", True),
            enable_mas=get_bool("enable_mas", True),
            enable_incremental=get_bool("enable_incremental", False),
            base_backup_dir=get_str("base_backup_dir", ""),
            defaults_domains_file=get_str("defaults_domains_file", "config/defaults/domains.txt"),
            defaults_exclude_file=get_str("defaults_exclude_file", "config/defaults/exclude.txt"),
        )
    
    def _parse_toml(self, path: str) -> Dict[str, Any]:
        """Parse TOML configuration file"""
        if not os.path.exists(path):
            self.logger.warning(f"Config file not found: {path}, using defaults")
            return {}
        
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to parse TOML config: {e}, using fallback")
            return self._fallback_parse(path)
    
    def _fallback_parse(self, path: str) -> Dict[str, Any]:
        """Fallback parser for simple key=value format"""
        data = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    data[key.strip()] = value.strip().strip('"\'')
        except Exception as e:
            self.logger.error(f"Failed to parse config file: {e}")
        return data


class CommandExecutor:
    """Handles command execution with logging and dry-run support"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def run(self, cmd: str, check: bool = True, description: str = "") -> int:
        """Execute a shell command with proper logging"""
        if self.config.dry_run:
            desc_text = f" ({description})" if description else ""
            self.logger.info(f"[dry-run]{desc_text} {cmd}")
            return 0
        
        if self.config.verbose:
            self.logger.debug(f"$ {cmd}")
        
        try:
            rc = subprocess.call(cmd, shell=True)
            if check and rc != 0:
                desc_text = f" ({description})" if description else ""
                self.logger.error(f"Command failed{desc_text} (exit code: {rc}): {cmd}")
                raise SystemExit(rc)
            return rc
        except KeyboardInterrupt:
            self.logger.warning("Operation interrupted by user")
            raise SystemExit(130)
        except Exception as e:
            self.logger.error(f"Exception occurred while executing command: {e}")
            if check:
                raise SystemExit(1)
            return 1
    
    def run_output(self, cmd: str) -> tuple[int, str]:
        """Execute command and return exit code and output"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, encoding="utf-8"
            )
            return result.returncode, result.stdout
        except Exception as e:
            self.logger.debug(f"Command failed: {cmd}, error: {e}")
            return 1, ""
    
    def which(self, cmd: str) -> bool:
        """Check if command exists"""
        return self.run_output(f"command -v {cmd} >/dev/null 2>&1")[0] == 0
    
    def confirm(self, prompt: str) -> bool:
        """Ask for user confirmation"""
        return confirm_action(self.logger, prompt, self.config.interactive)


class BackupComponent:
    """Base class for backup components (Homebrew, VS Code, etc.)"""
    
    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.config = executor.config
        self.logger = logging.getLogger(__name__)
    
    @property
    def name(self) -> str:
        """Component name for logging"""
        return self.__class__.__name__
    
    def is_available(self) -> bool:
        """Check if this component is available on the system"""
        raise NotImplementedError
    
    def is_enabled(self) -> bool:
        """Check if this component is enabled in config"""
        raise NotImplementedError
    
    def export(self, output_dir: str) -> bool:
        """Export component data to output directory"""
        raise NotImplementedError
    
    def restore(self, backup_dir: str) -> bool:
        """Restore component data from backup directory"""
        raise NotImplementedError
    
    def preview_export(self, output_dir: str) -> List[str]:
        """Preview what would be exported"""
        raise NotImplementedError
    
    def preview_restore(self, backup_dir: str) -> List[str]:
        """Preview what would be restored"""
        raise NotImplementedError


class HomebrewComponent(BackupComponent):
    """Handles Homebrew package management backup/restore"""
    
    def is_available(self) -> bool:
        return self.executor.which("brew")
    
    def is_enabled(self) -> bool:
        return True  # Homebrew is always enabled if available
    
    def export(self, output_dir: str) -> bool:
        if not self.is_available():
            self.logger.warning("Homebrew not available, skipping")
            return False
        
        brewfile = os.path.join(output_dir, "Brewfile")
        version_file = os.path.join(output_dir, "HOMEBREW_VERSION.txt")
        
        self.executor.run(f'brew bundle dump --file="{brewfile}" --force', 
                         description="Export Brewfile")
        self.executor.run(f'brew --version > "{version_file}"', 
                         description="Save Homebrew version")
        return True
    
    def restore(self, backup_dir: str) -> bool:
        brewfile = os.path.join(backup_dir, "Brewfile")
        
        if not os.path.exists(brewfile):
            self.logger.warning("No Brewfile found in backup")
            return False
        
        if not self.is_available():
            if self.executor.confirm("Install Homebrew?"):
                install_cmd = 'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                self.executor.run(install_cmd, check=False)
        
        if self.executor.confirm("Execute brew bundle install?"):
            self.executor.run(f'brew bundle --file="{brewfile}"', check=False)
            return True
        return False
    
    def preview_export(self, output_dir: str) -> List[str]:
        if not self.is_available():
            return ["✗ Homebrew not installed, skipping"]
        return ["✓ Homebrew config (Brewfile)"]
    
    def preview_restore(self, backup_dir: str) -> List[str]:
        brewfile = os.path.join(backup_dir, "Brewfile")
        if not os.path.exists(brewfile):
            return ["✗ No Homebrew config"]
        
        try:
            with open(brewfile, 'r') as f:
                lines = f.readlines()
            brew_count = len([l for l in lines if l.strip().startswith('brew ')])
            cask_count = len([l for l in lines if l.strip().startswith('cask ')])
            return [f"✓ Homebrew: {brew_count} packages, {cask_count} apps"]
        except:
            return ["✓ Homebrew config file"]


class MASComponent(BackupComponent):
    """Handles Mac App Store applications backup/restore"""
    
    def is_available(self) -> bool:
        return self.executor.which("mas")
    
    def is_enabled(self) -> bool:
        return self.config.enable_mas
    
    def export(self, output_dir: str) -> bool:
        if not self.is_enabled() or not self.is_available():
            self.logger.warning("MAS export disabled or not available")
            return False
        
        mas_file = os.path.join(output_dir, "mas.list")
        self.executor.run(f'mas list > "{mas_file}"', 
                         description="Export MAS app list")
        return True
    
    def restore(self, backup_dir: str) -> bool:
        mas_file = os.path.join(backup_dir, "mas.list")
        
        if not os.path.exists(mas_file):
            self.logger.warning("No MAS list found in backup")
            return False
        
        if not self.is_available():
            self.executor.run("brew install mas", check=False)
        
        self.logger.warning("Please login to App Store first")
        if self.executor.confirm("Install MAS list now?"):
            install_cmd = f'awk \'{{print $1}}\' "{mas_file}" | while read -r id; do [[ -z "$id" ]] || mas install "$id" || true; done'
            self.executor.run(install_cmd, check=False)
            return True
        return False
    
    def preview_export(self, output_dir: str) -> List[str]:
        if not self.is_enabled() or not self.is_available():
            return ["✗ MAS export disabled or not installed"]
        return ["✓ Mac App Store app list"]
    
    def preview_restore(self, backup_dir: str) -> List[str]:
        mas_file = os.path.join(backup_dir, "mas.list")
        if not os.path.exists(mas_file):
            return ["✗ No MAS app list"]
        
        try:
            with open(mas_file, 'r') as f:
                app_count = len(f.readlines())
            return [f"✓ Mac App Store: {app_count} apps"]
        except:
            return ["✓ Mac App Store app list"]


class VSCodeComponent(BackupComponent):
    """Handles VS Code extensions backup/restore"""
    
    def is_available(self) -> bool:
        return self.executor.which("code")
    
    def is_enabled(self) -> bool:
        return self.config.enable_vscode
    
    def export(self, output_dir: str) -> bool:
        if not self.is_enabled() or not self.is_available():
            self.logger.warning("VS Code export disabled or not available")
            return False
        
        extensions_file = os.path.join(output_dir, "vscode_extensions.txt")
        self.executor.run(f'code --list-extensions > "{extensions_file}"', 
                         description="Export VS Code extensions")
        return True
    
    def restore(self, backup_dir: str) -> bool:
        extensions_file = os.path.join(backup_dir, "vscode_extensions.txt")
        
        if not os.path.exists(extensions_file):
            self.logger.warning("No VS Code extensions found in backup")
            return False
        
        if not self.is_available():
            self.logger.warning("VS Code not available")
            return False
        
        if self.executor.confirm("Start installing VS Code extensions?"):
            install_cmd = f'while read -r ext; do [[ -z "$ext" ]] || code --install-extension "$ext" || true; done < "{extensions_file}"'
            self.executor.run(install_cmd, check=False)
            return True
        return False
    
    def preview_export(self, output_dir: str) -> List[str]:
        if not self.is_enabled() or not self.is_available():
            return ["✗ VS Code export disabled or not installed"]
        return ["✓ VS Code extension list"]
    
    def preview_restore(self, backup_dir: str) -> List[str]:
        extensions_file = os.path.join(backup_dir, "vscode_extensions.txt")
        if not os.path.exists(extensions_file):
            return ["✗ No VS Code extensions"]
        return ["✓ VS Code extensions"]


class DotfilesComponent(BackupComponent):
    """Handles dotfiles and configuration files backup/restore"""
    
    DOT_LIST = [
        "~/.zshrc","~/.zprofile","~/.bashrc","~/.bash_profile","~/.profile",
        "~/.gitconfig","~/.gitignore_global","~/.vimrc","~/.ideavimrc",
        "~/.wezterm.lua","~/.tmux.conf","~/.config/tmux",
        "~/.config/wezterm","~/.config/kitty","~/.config/nvim","~/.config/alacritty",
        "~/.config/karabiner","~/.config/starship.toml","~/.config/iterm2",
        "~/.ssh/config",  # Config only, no private keys
        # JetBrains / Xcode / Services / Fonts (optional)
        "~/Library/Preferences/com.googlecode.iterm2.plist",
        "~/Library/Preferences/IdeaVim",
        "~/Library/Application Support/JetBrains",
        "~/Library/Preferences/IntelliJIdea*",
        "~/Library/Developer/Xcode/UserData",
        "~/Library/Services",
        "~/Library/Fonts",
        # VSCode user settings
        "~/Library/Application Support/Code/User/settings.json",
        "~/Library/Application Support/Code/User/keybindings.json",
        "~/Library/Application Support/Code/User/snippets",
    ]
    
    def is_available(self) -> bool:
        return True  # Always available
    
    def is_enabled(self) -> bool:
        return True  # Always enabled
    
    def export(self, output_dir: str) -> bool:
        import tempfile
        safe_dotfiles = self._get_secure_dotfile_list()
        
        if not safe_dotfiles:
            self.logger.warning("No safe dotfiles found")
            return False
        
        with tempfile.TemporaryDirectory() as tmp:
            # Copy files to temp directory
            for pattern in safe_dotfiles:
                src = os.path.expanduser(pattern)
                if os.path.exists(src):
                    # Create relative path structure in temp
                    rel_path = os.path.relpath(src, os.path.expanduser("~"))
                    dest = os.path.join(tmp, rel_path)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    
                    # Use rsync to copy excluding sensitive files
                    cmd = f'rsync -a --exclude "*.key" --exclude "known_hosts" --exclude "authorized_keys" "{src}" "{dest}" 2>/dev/null || true'
                    self.executor.run(cmd, check=False, description=f"Copy {pattern}")
            
            # Create tar archive
            dotfiles_archive = os.path.join(output_dir, "dotfiles.tar.gz")
            cmd = f'tar -czf "{dotfiles_archive}" -C "{tmp}" . || true'
            self.executor.run(cmd, check=False, description="Compress dotfiles")
            
        return True
    
    def restore(self, backup_dir: str) -> bool:
        dotfiles_archive = os.path.join(backup_dir, "dotfiles.tar.gz")
        
        if not os.path.exists(dotfiles_archive):
            self.logger.warning("No dotfiles archive found in backup")
            return False
        
        if self.executor.confirm("Overwrite existing files (auto backup)?"):
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                # Extract archive
                self.executor.run(f'tar -xzf "{dotfiles_archive}" -C "{tmp}"', check=False)
                
                # Backup existing files and restore
                home = os.path.expanduser("~")
                restore_cmd = f'''
                cd "{tmp}"
                find . -type f -print0 | while IFS= read -r -d "" item; do
                    dst="{home}/${{item#./}}"
                    [[ -e "$dst" ]] && cp -a "$dst" "${{dst}}.bak.$(date +%Y%m%d%H%M%S)"
                done
                rsync -av "{tmp}/" "{home}/"
                '''
                self.executor.run(restore_cmd, check=False)
                return True
        return False
    
    def preview_export(self, output_dir: str) -> List[str]:
        safe_dotfiles = self._get_secure_dotfile_list()
        if safe_dotfiles:
            return [
                f"✓ Dotfiles and config files:",
                *[f"    - {dot}" for dot in safe_dotfiles[:5]],
                f"    ... total {len(safe_dotfiles)} config files" if len(safe_dotfiles) > 5 else ""
            ]
        return ["✗ No dotfiles found"]
    
    def preview_restore(self, backup_dir: str) -> List[str]:
        dotfiles_archive = os.path.join(backup_dir, "dotfiles.tar.gz")
        if os.path.exists(dotfiles_archive):
            size = os.path.getsize(dotfiles_archive)
            return [f"✓ Dotfiles archive ({size} bytes)"]
        return ["✗ No dotfiles backup"]
    
    def _get_secure_dotfile_list(self) -> List[str]:
        """Get security-filtered dotfiles list"""
        safe_dotfiles = []
        skipped_files = []
        
        for pattern in self.DOT_LIST:
            expanded = os.path.expanduser(pattern)
            if os.path.exists(expanded):
                if not self._is_sensitive_file(expanded):
                    safe_dotfiles.append(pattern)
                else:
                    skipped_files.append(pattern)
        
        if skipped_files:
            self.logger.info(f"Skipped {len(skipped_files)} sensitive files for security")
            for skip in skipped_files:
                self.logger.debug(f"  Skipped: {skip}")
        
        return safe_dotfiles
    
    def _is_sensitive_file(self, file_path: str) -> bool:
        """Check if file contains sensitive information"""
        sensitive_patterns = [
            "private_key", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
            ".pem", ".key", ".p12", ".pfx",
            "password", "secret", "token", "auth",
            "known_hosts", "authorized_keys",
            "keychain", ".keychain",
        ]
        return any(pattern in file_path for pattern in sensitive_patterns)


class DefaultsComponent(BackupComponent):
    """Handles macOS system defaults backup/restore"""
    
    def is_available(self) -> bool:
        return self.executor.which("defaults")
    
    def is_enabled(self) -> bool:
        return self.config.enable_defaults
    
    def export(self, output_dir: str) -> bool:
        if not self.is_enabled() or not self.is_available():
            return False
        
        domains_file = "./" + self.config.defaults_domains_file
        if not os.path.exists(domains_file):
            self.logger.warning(f"Domains file not found: {domains_file}")
            return False
        
        # Load domains list
        domains = []
        with open(domains_file, "r", encoding="utf-8") as f:
            for line in f:
                domain = line.strip()
                if domain and not domain.startswith("#"):
                    domains.append(domain)
        
        if not domains:
            self.logger.warning("No domains found in domains file")
            return False
        
        # Create defaults directory
        defaults_dir = os.path.join(output_dir, "defaults")
        os.makedirs(defaults_dir, exist_ok=True)
        
        # Export each domain
        exported_count = 0
        for domain in domains:
            rc, _ = self.executor.run_output(f'defaults domains | grep -q "{domain}"')
            if rc == 0:
                plist_file = os.path.join(defaults_dir, f"{domain}.plist")
                self.executor.run(f'defaults export "{domain}" "{plist_file}" || true',
                                check=False, description=f"Export {domain}")
                exported_count += 1
        
        self.logger.info(f"Exported {exported_count} defaults domains")
        return exported_count > 0
    
    def restore(self, backup_dir: str) -> bool:
        defaults_dir = os.path.join(backup_dir, "defaults")
        
        if not os.path.isdir(defaults_dir):
            self.logger.warning("No defaults directory found in backup")
            return False
        
        if self.executor.confirm("Import and refresh Dock/Finder?"):
            # Import all plist files
            import_cmd = f'''
            for p in "{defaults_dir}"/*.plist; do
                [[ -e "$p" ]] || continue
                d="$(basename "$p" .plist)"
                defaults domains | grep -q "$d" && defaults export "$d" "$HOME/defaults_backup_${{d}}_$(date +%Y%m%d%H%M%S).plist" || true
                defaults import "$d" "$p" || true
            done
            killall Dock 2>/dev/null || true
            killall Finder 2>/dev/null || true
            '''
            self.executor.run(import_cmd, check=False)
            return True
        return False
    
    def preview_export(self, output_dir: str) -> List[str]:
        if not self.is_enabled() or not self.is_available():
            return ["✗ Defaults export disabled"]
        
        domains_file = "./" + self.config.defaults_domains_file
        if os.path.exists(domains_file):
            with open(domains_file, "r", encoding="utf-8") as f:
                domains = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            return [
                f"✓ System preferences (defaults):",
                *[f"    - {domain}" for domain in domains[:5]],
                f"    ... total {len(domains)} domains" if len(domains) > 5 else ""
            ]
        return ["✗ No defaults domains file"]
    
    def preview_restore(self, backup_dir: str) -> List[str]:
        defaults_dir = os.path.join(backup_dir, "defaults")
        if os.path.isdir(defaults_dir):
            plist_files = [f for f in os.listdir(defaults_dir) if f.endswith('.plist')]
            return [f"✓ System preferences: {len(plist_files)} domains"]
        return ["✗ No system preferences"]


class LaunchAgentsComponent(BackupComponent):
    """Handles LaunchAgents backup/restore"""
    
    def is_available(self) -> bool:
        return True  # Always available on macOS
    
    def is_enabled(self) -> bool:
        return self.config.enable_launchagents
    
    def export(self, output_dir: str) -> bool:
        if not self.is_enabled():
            return False
        
        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        if not os.path.isdir(launch_agents_dir):
            self.logger.warning("No LaunchAgents directory found")
            return False
        
        # Create LaunchAgents backup directory
        backup_la_dir = os.path.join(output_dir, "LaunchAgents")
        os.makedirs(backup_la_dir, exist_ok=True)
        
        # Copy plist files
        self.executor.run(f'cp -a "{launch_agents_dir}"/*.plist "{backup_la_dir}/" 2>/dev/null || true',
                         check=False, description="Backup LaunchAgents")
        return True
    
    def restore(self, backup_dir: str) -> bool:
        backup_la_dir = os.path.join(backup_dir, "LaunchAgents")
        
        if not os.path.isdir(backup_la_dir):
            self.logger.warning("No LaunchAgents found in backup")
            return False
        
        # Create LaunchAgents directory
        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        self.executor.run(f'mkdir -p "{launch_agents_dir}"', check=False)
        
        # Copy plist files
        self.executor.run(f'cp -a "{backup_la_dir}"/*.plist "{launch_agents_dir}/" 2>/dev/null || true',
                         check=False)
        
        if self.executor.confirm("Load LaunchAgents?"):
            load_cmd = f'find "{launch_agents_dir}" -name "*.plist" -print0 | while IFS= read -r -d "" f; do launchctl load -w "$f" 2>/dev/null || true; done'
            self.executor.run(load_cmd, check=False)
            return True
        return False
    
    def preview_export(self, output_dir: str) -> List[str]:
        if not self.is_enabled():
            return ["✗ LaunchAgents export disabled"]
        
        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        if os.path.isdir(launch_agents_dir):
            plist_files = [f for f in os.listdir(launch_agents_dir) if f.endswith('.plist')]
            return [f"✓ LaunchAgents ({len(plist_files)} files)"]
        return ["✗ No LaunchAgents"]
    
    def preview_restore(self, backup_dir: str) -> List[str]:
        backup_la_dir = os.path.join(backup_dir, "LaunchAgents")
        if os.path.isdir(backup_la_dir):
            agent_files = [f for f in os.listdir(backup_la_dir) if f.endswith('.plist')]
            return [f"✓ LaunchAgents: {len(agent_files)} services"]
        return ["✗ No LaunchAgents"]


class BackupManager:
    """Manages the overall backup and restore process"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.executor = CommandExecutor(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.components = [
            HomebrewComponent(self.executor),
            MASComponent(self.executor),
            VSCodeComponent(self.executor),
            DotfilesComponent(self.executor),
            DefaultsComponent(self.executor),
            LaunchAgentsComponent(self.executor),
        ]
    
    def export(self, output_dir: str) -> bool:
        """Export all enabled components"""
        os.makedirs(output_dir, exist_ok=True)
        
        log_section(self.logger, f"Exporting to: {output_dir}")
        log_separator(self.logger)
        
        success_count = 0
        total_count = 0
        
        # Export environment info
        self._export_environment(output_dir)
        success_count += 1
        
        # Export each component
        for component in self.components:
            if component.is_enabled() and component.is_available():
                total_count += 1
                if component.export(output_dir):
                    success_count += 1
                    self.logger.info(f"✓ {component.name} exported")
                else:
                    self.logger.warning(f"✗ {component.name} export failed")
        
        log_separator(self.logger)
        log_success(self.logger, f"Export completed: {success_count} components exported")
        return success_count > 0
    
    def restore(self, backup_dir: str) -> bool:
        """Restore all available components from backup"""
        if not os.path.isdir(backup_dir):
            self.logger.error(f"Backup directory does not exist: {backup_dir}")
            return False
        
        log_section(self.logger, f"Restoring from backup: {backup_dir}")
        log_separator(self.logger)
        
        success_count = 0
        
        # Restore each component
        for component in self.components:
            if component.restore(backup_dir):
                success_count += 1
                self.logger.info(f"✓ {component.name} restored")
        
        log_separator(self.logger)
        log_success(self.logger, f"Restore completed: {success_count} components restored")
        return success_count > 0
    
    def preview_export(self, output_dir: str) -> None:
        """Preview what would be exported"""
        log_section(self.logger, f"Preview export operation → {output_dir}")
        log_separator(self.logger)
        
        self.logger.info("Content to be exported:")
        self.logger.info("  ✓ Environment info (ENVIRONMENT.txt)")
        
        for component in self.components:
            if component.is_enabled():
                for line in component.preview_export(output_dir):
                    self.logger.info(f"  {line}")
        
        log_separator(self.logger)
        log_success(self.logger, "Preview completed. Use 'myconfig export' to perform actual export")
    
    def preview_restore(self, backup_dir: str) -> None:
        """Preview what would be restored"""
        if not os.path.isdir(backup_dir):
            self.logger.error(f"Backup directory does not exist: {backup_dir}")
            return
        
        log_section(self.logger, f"Preview restore operation ← {backup_dir}")
        log_separator(self.logger)
        
        self.logger.info("Backup content analysis:")
        
        for component in self.components:
            for line in component.preview_restore(backup_dir):
                self.logger.info(f"  {line}")
        
        log_separator(self.logger)
        log_success(self.logger, "Preview completed. Use 'myconfig restore' to perform actual restore")
    
    def _export_environment(self, output_dir: str) -> None:
        """Export environment information"""
        from .utils import ts, host
        
        env_file = os.path.join(output_dir, "ENVIRONMENT.txt")
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"export_time: {ts()}\nhost: {host()}\n\n")
            
            rc, sw = self.executor.run_output("sw_vers || true")
            f.write("sw_vers:\n" + sw + "\n")
            
            rc, xcp = self.executor.run_output("xcode-select -p || true")
            f.write("xcode-select -p:\n" + xcp + "\n")

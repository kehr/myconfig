"""
Backup management and orchestration
"""

from __future__ import annotations
import os
import logging
from .config import AppConfig
from .executor import CommandExecutor
from .components import (
    HomebrewComponent,
    MASComponent,
    VSCodeComponent,
    DotfilesComponent,
    DefaultsComponent,
    LaunchAgentsComponent,
)
from ..logger import log_section, log_separator, log_success
from ..utils import create_backup_manifest, ts, host


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

    def export(self, output_dir: str, compress: bool = False) -> bool:
        """Export all enabled components"""
        temp_dir = output_dir
        if compress:
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="myconfig_export_")
        
        os.makedirs(temp_dir, exist_ok=True)

        log_section(self.logger, f"Exporting to: {output_dir}")
        log_separator(self.logger)

        success_count = 0
        total_count = 0

        # Export environment info
        self._export_environment(temp_dir)
        success_count += 1

        # Export each component
        for component in self.components:
            if component.is_enabled() and component.is_available():
                total_count += 1
                if component.export(temp_dir):
                    success_count += 1
                    self.logger.info(f"✓ {component.name} exported")
                else:
                    self.logger.warning(f"✗ {component.name} export failed")

        # Create backup manifest and README
        component_names = [comp.name for comp in self.components if comp.is_enabled()]
        create_backup_manifest(temp_dir, component_names)
        self._create_export_readme(temp_dir)
        
        # Handle compression if requested
        if compress:
            self._create_compressed_backup(temp_dir, output_dir)
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir)
        
        log_separator(self.logger)
        log_success(
            self.logger, f"Export completed: {success_count} components exported"
        )
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
        log_success(
            self.logger, f"Restore completed: {success_count} components restored"
        )
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
        log_success(
            self.logger,
            "Preview completed. Use 'myconfig export' to perform actual export",
        )

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
        log_success(
            self.logger,
            "Preview completed. Use 'myconfig restore' to perform actual restore",
        )

    def _export_environment(self, output_dir: str) -> None:
        """Export environment information"""
        from ..utils import ts, host

        env_file = os.path.join(output_dir, "ENVIRONMENT.txt")
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"export_time: {ts()}\nhost: {host()}\n\n")

            rc, sw = self.executor.run_output("sw_vers || true")
            f.write("sw_vers:\n" + sw + "\n")

            rc, xcp = self.executor.run_output("xcode-select -p || true")
            f.write("xcode-select -p:\n" + xcp + "\n")

    def _create_export_readme(self, output_dir: str) -> None:
        """Create detailed export README with file manifest"""
        import os
        from ..utils import ts, host
        
        readme_file = os.path.join(output_dir, "README.md")
        
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write("# MyConfig Export Manifest\n\n")
            f.write(f"**Export Time**: {ts()}\n")
            f.write(f"**Hostname**: {host()}\n")
            f.write(f"**Export Tool**: MyConfig v2.0\n\n")
            
            f.write("## 📋 Export Summary\n\n")
            f.write("This backup contains the following macOS configuration components:\n\n")
            
            # Analyze and document each file/directory
            self._document_export_files(f, output_dir)
            
            f.write("\n## 🔄 Restore Instructions\n\n")
            f.write("To restore this configuration on a new system:\n\n")
            f.write("1. Install MyConfig tool\n")
            f.write("2. Run: `myconfig restore <this-directory>`\n")
            f.write("3. Or run: `myconfig unpack <backup-archive>` (if compressed)\n\n")
            
            f.write("## ⚠️ Important Notes\n\n")
            f.write("- Sensitive files (SSH keys, passwords) are automatically excluded\n")
            f.write("- System defaults may require logout/restart to take effect\n")
            f.write("- Homebrew installation will be prompted if not present\n")
            f.write("- VS Code extensions will be installed automatically\n\n")

    def _document_export_files(self, f, output_dir: str) -> None:
        """Document all exported files in detail"""
        
        # System Environment
        env_file = os.path.join(output_dir, "ENVIRONMENT.txt")
        if os.path.exists(env_file):
            f.write("### 🖥️ System Environment\n")
            f.write(f"- **File**: `ENVIRONMENT.txt`\n")
            f.write(f"- **Size**: {os.path.getsize(env_file)} bytes\n")
            f.write(f"- **Content**: macOS version, hostname, Xcode tools info\n\n")
        
        # Homebrew
        brewfile = os.path.join(output_dir, "Brewfile")
        if os.path.exists(brewfile):
            f.write("### 🍺 Homebrew Configuration\n")
            with open(brewfile, "r") as bf:
                lines = bf.readlines()
                brew_count = len([l for l in lines if l.strip().startswith('brew ')])
                cask_count = len([l for l in lines if l.strip().startswith('cask ')])
                tap_count = len([l for l in lines if l.strip().startswith('tap ')])
            
            f.write(f"- **File**: `Brewfile`\n")
            f.write(f"- **Size**: {os.path.getsize(brewfile)} bytes\n")
            f.write(f"- **Packages**: {brew_count} formulas, {cask_count} casks, {tap_count} taps\n")
            if os.path.exists(os.path.join(output_dir, "HOMEBREW_VERSION.txt")):
                f.write(f"- **Version Info**: `HOMEBREW_VERSION.txt`\n")
            f.write("\n")
        
        # VS Code
        vscode_file = os.path.join(output_dir, "vscode_extensions.txt")
        if os.path.exists(vscode_file):
            f.write("### 💻 VS Code Configuration\n")
            with open(vscode_file, "r") as vf:
                ext_count = len([l for l in vf.readlines() if l.strip()])
            f.write(f"- **File**: `vscode_extensions.txt`\n")
            f.write(f"- **Size**: {os.path.getsize(vscode_file)} bytes\n")
            f.write(f"- **Extensions**: {ext_count} installed extensions\n\n")
        
        # Dotfiles
        dotfiles_archive = os.path.join(output_dir, "dotfiles.tar.gz")
        if os.path.exists(dotfiles_archive):
            f.write("### 📁 Configuration Files (Dotfiles)\n")
            f.write(f"- **Archive**: `dotfiles.tar.gz`\n")
            f.write(f"- **Size**: {os.path.getsize(dotfiles_archive):,} bytes\n")
            f.write(f"- **Content**: Shell configs, Git settings, application preferences\n")
            f.write(f"- **Security**: Sensitive files automatically excluded\n\n")
        
        # System Defaults
        defaults_dir = os.path.join(output_dir, "defaults")
        if os.path.isdir(defaults_dir):
            f.write("### ⚙️ System Preferences (Defaults)\n")
            plist_files = [f for f in os.listdir(defaults_dir) if f.endswith('.plist')]
            total_size = sum(os.path.getsize(os.path.join(defaults_dir, pf)) for pf in plist_files)
            
            f.write(f"- **Directory**: `defaults/`\n")
            f.write(f"- **Files**: {len(plist_files)} preference domains\n")
            f.write(f"- **Total Size**: {total_size:,} bytes\n")
            f.write(f"- **Domains**: Dock, Finder, Safari, etc.\n\n")
        
        # LaunchAgents
        la_dir = os.path.join(output_dir, "LaunchAgents")
        if os.path.isdir(la_dir):
            f.write("### 🚀 Launch Agents\n")
            plist_files = [f for f in os.listdir(la_dir) if f.endswith('.plist')]
            f.write(f"- **Directory**: `LaunchAgents/`\n")
            f.write(f"- **Services**: {len(plist_files)} user services\n")
            f.write(f"- **Content**: Background services and scheduled tasks\n\n")
        
        # MAS
        mas_file = os.path.join(output_dir, "mas.list")
        if os.path.exists(mas_file):
            f.write("### 🏪 Mac App Store\n")
            with open(mas_file, "r") as mf:
                app_count = len([l for l in mf.readlines() if l.strip()])
            f.write(f"- **File**: `mas.list`\n")
            f.write(f"- **Apps**: {app_count} installed applications\n\n")
        
        # Metadata files
        f.write("### 📄 Metadata Files\n")
        manifest_file = os.path.join(output_dir, "MANIFEST.json")
        if os.path.exists(manifest_file):
            f.write(f"- **Manifest**: `MANIFEST.json` - Export metadata and component list\n")
        f.write(f"- **This File**: `README.md` - Detailed export documentation\n")

    def _create_compressed_backup(self, temp_dir: str, output_path: str) -> None:
        """Create compressed backup archive"""
        import tarfile
        
        # Ensure output_path has .tar.gz extension
        if not output_path.endswith('.tar.gz'):
            output_path = output_path + '.tar.gz'
        
        self.logger.info(f"Creating compressed backup: {output_path}")
        
        with tarfile.open(output_path, 'w:gz') as tar:
            # Add all files from temp directory
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                tar.add(item_path, arcname=item)
        
        # Show final archive size
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        self.logger.info(f"Compressed backup created: {size_mb:.1f} MB")

    def unpack(self, archive_path: str, output_dir: str = None) -> str:
        """Unpack a compressed backup archive"""
        import tarfile
        import tempfile
        
        if not os.path.exists(archive_path):
            self.logger.error(f"Archive not found: {archive_path}")
            return None
        
        if output_dir is None:
            # Create temp directory for extraction
            output_dir = tempfile.mkdtemp(prefix="myconfig_unpack_")
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        log_section(self.logger, f"Unpacking archive: {archive_path}")
        log_separator(self.logger)
        
        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(output_dir)
            
            # Verify extraction
            if os.path.exists(os.path.join(output_dir, "MANIFEST.json")):
                log_success(self.logger, f"Archive unpacked to: {output_dir}")
                return output_dir
            else:
                self.logger.error("Invalid backup archive - missing MANIFEST.json")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to unpack archive: {e}")
            return None

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

        # Create backup manifest
        component_names = [comp.name for comp in self.components if comp.is_enabled()]
        create_backup_manifest(output_dir, component_names)
        
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

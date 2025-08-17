"""
Backup components for different macOS tools and configurations
"""

from .base import BackupComponent
from .homebrew import HomebrewComponent
from .mas import MASComponent
from .vscode import VSCodeComponent
from .dotfiles import DotfilesComponent
from .defaults import DefaultsComponent
from .launchagents import LaunchAgentsComponent

__all__ = [
    "BackupComponent",
    "HomebrewComponent",
    "MASComponent",
    "VSCodeComponent", 
    "DotfilesComponent",
    "DefaultsComponent",
    "LaunchAgentsComponent",
]

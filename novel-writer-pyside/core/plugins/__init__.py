"""插件系统核心模块。"""

from .base import PluginBase
from .manager import PluginManager, plugin_manager

__all__ = [
    "PluginBase",
    "PluginManager",
    "plugin_manager",
]

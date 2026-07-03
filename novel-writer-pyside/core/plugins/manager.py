"""插件管理器 - 负责插件的发现、加载、启用/禁用。"""

import importlib
import logging
import pkgutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

from .base import PluginBase

logger = logging.getLogger(__name__)


class PluginManager:
    """插件管理器 - 负责插件的发现、加载、启用/禁用。"""

    # 7 个扩展点
    EXTENSION_POINTS = [
        "ui_menu",
        "ui_sidebar",
        "ai_provider",
        "writing_method",
        "export_format",
        "tracker",
        "command",
    ]

    def __init__(self, plugin_dir: Optional[str] = None):
        self._plugins: Dict[str, PluginBase] = {}
        self._plugin_dir: str = plugin_dir or ""

    def discover_plugins(self, plugin_dir: Optional[str] = None) -> int:
        """扫描插件目录并加载所有有效插件。返回加载的插件数量。"""
        target_dir = plugin_dir or self._plugin_dir or str(Path.home() / ".novel-writer" / "plugins")
        plugin_path = Path(target_dir)

        if not plugin_path.exists():
            plugin_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"插件目录不存在，已创建: {plugin_path}")
            return 0

        self._plugin_dir = str(plugin_path)

        # 将插件目录加入 sys.path 以便 importlib 发现
        plugin_str = str(plugin_path)
        if plugin_str not in sys.path:
            sys.path.insert(0, plugin_str)

        count = 0
        for finder, name, ispkg in pkgutil.iter_modules([plugin_str]):
            try:
                module = importlib.import_module(name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, PluginBase)
                        and attr is not PluginBase
                    ):
                        # 避免重复加载
                        if name in self._plugins:
                            continue
                        plugin_instance = attr()
                        self._plugins[plugin_instance.name or name] = plugin_instance
                        plugin_instance.on_load()
                        count += 1
                        logger.info(f"插件已加载: {plugin_instance.name or name}")
            except Exception as e:
                logger.error(f"加载插件 '{name}' 失败: {e}")

        return count

    def load_plugin(self, plugin_name: str) -> bool:
        """加载指定插件。"""
        if plugin_name in self._plugins:
            logger.warning(f"插件 '{plugin_name}' 已加载")
            return False

        if not self._plugin_dir:
            logger.error("尚未设置插件目录，请先调用 discover_plugins")
            return False

        try:
            module = importlib.import_module(plugin_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, PluginBase)
                    and attr is not PluginBase
                ):
                    plugin_instance = attr()
                    self._plugins[plugin_instance.name or plugin_name] = plugin_instance
                    plugin_instance.on_load()
                    logger.info(f"插件已加载: {plugin_instance.name or plugin_name}")
                    return True
            logger.warning(f"在模块 '{plugin_name}' 中未找到有效的插件类")
            return False
        except Exception as e:
            logger.error(f"加载插件 '{plugin_name}' 失败: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载指定插件。"""
        plugin = self._plugins.pop(plugin_name, None)
        if plugin is None:
            logger.warning(f"插件 '{plugin_name}' 未加载")
            return False
        try:
            plugin.on_unload()
            logger.info(f"插件已卸载: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"卸载插件 '{plugin_name}' 失败: {e}")
            return False

    def enable_plugin(self, plugin_name: str) -> bool:
        """启用指定插件。"""
        plugin = self._plugins.get(plugin_name)
        if plugin is None:
            logger.warning(f"插件 '{plugin_name}' 未加载")
            return False
        try:
            plugin.on_enable()
            logger.info(f"插件已启用: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"启用插件 '{plugin_name}' 失败: {e}")
            return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """禁用指定插件。"""
        plugin = self._plugins.get(plugin_name)
        if plugin is None:
            logger.warning(f"插件 '{plugin_name}' 未加载")
            return False
        try:
            plugin.on_disable()
            logger.info(f"插件已禁用: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"禁用插件 '{plugin_name}' 失败: {e}")
            return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """获取指定插件实例。"""
        return self._plugins.get(plugin_name)

    def list_plugins(self) -> List[Dict]:
        """列出所有已发现的插件信息。"""
        return [
            {
                "name": p.name or name,
                "version": p.version,
                "description": p.description,
                "author": p.author,
                "extension_points": list(p.extension_points),
            }
            for name, p in self._plugins.items()
        ]

    def get_plugins_for_point(self, extension_point: str) -> List[PluginBase]:
        """获取支持指定扩展点的所有插件。"""
        if extension_point not in self.EXTENSION_POINTS:
            logger.warning(f"未知的扩展点: '{extension_point}'")
            return []
        return [
            p for p in self._plugins.values()
            if extension_point in p.extension_points
        ]


# 全局插件管理器单例
plugin_manager = PluginManager()

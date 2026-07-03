"""插件服务 - PluginManager 的 Qt 包装层。"""
from typing import Optional, List, Dict
from PySide6.QtCore import QObject, Signal
from core.plugins.manager import plugin_manager


class PluginService(QObject):
    """插件服务 - 连接 UI 和插件系统。"""

    plugin_installed = Signal(str)       # 插件安装 (plugin_name)
    plugin_uninstalled = Signal(str)     # 插件卸载 (plugin_name)
    plugin_enabled = Signal(str)         # 插件启用 (plugin_name)
    plugin_disabled = Signal(str)        # 插件禁用 (plugin_name)

    def __init__(self, manager=None):
        super().__init__()
        self._manager = manager or plugin_manager

    def list_plugins(self) -> List[Dict]:
        """列出所有插件。"""
        return self._manager.list_plugins()

    def install_plugin(self, plugin_name: str, source: str = None) -> bool:
        """安装插件。"""
        success = self._manager.load_plugin(plugin_name)
        if success:
            self.plugin_installed.emit(plugin_name)
        return success

    def uninstall_plugin(self, plugin_name: str) -> bool:
        """卸载插件。"""
        success = self._manager.unload_plugin(plugin_name)
        if success:
            self.plugin_uninstalled.emit(plugin_name)
        return success

    def enable_plugin(self, plugin_name: str) -> None:
        """启用插件。"""
        self._manager.enable_plugin(plugin_name)
        self.plugin_enabled.emit(plugin_name)

    def disable_plugin(self, plugin_name: str) -> None:
        """禁用插件。"""
        self._manager.disable_plugin(plugin_name)
        self.plugin_disabled.emit(plugin_name)

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """获取插件信息。"""
        plugin = self._manager.get_plugin(plugin_name)
        if plugin is None:
            return None
        return {
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "author": plugin.author,
            "extension_points": plugin.extension_points,
        }

    def execute_command(self, plugin_name: str, command: str, **kwargs) -> str:
        """执行插件命令。"""
        plugin = self._manager.get_plugin(plugin_name)
        if plugin is None:
            return ""
        # 委托给插件执行（如果插件有 execute 方法）
        if hasattr(plugin, 'execute'):
            return plugin.execute(command, **kwargs)
        return ""


# 全局实例
plugin_service = PluginService()

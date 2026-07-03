"""插件抽象基类。"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class PluginBase(ABC):
    """所有插件的抽象基类。"""

    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""

    # 支持的扩展点列表
    extension_points: List[str] = []

    def on_load(self):
        """插件加载时调用。"""
        pass

    def on_unload(self):
        """插件卸载时调用。"""
        pass

    def on_enable(self):
        """启用时调用。"""
        pass

    def on_disable(self):
        """禁用时调用。"""
        pass

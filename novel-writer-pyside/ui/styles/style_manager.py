"""主题样式管理器。"""
import os
from pathlib import Path

class StyleManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._styles_dir = Path(__file__).parent
        self._current_theme = "dark"
    
    @property
    def current_theme(self) -> str:
        return self._current_theme
    
    def load_theme(self, theme_name: str = "dark") -> str:
        """加载主题 QSS 文件。"""
        qss_file = self._styles_dir / f"{theme_name}.qss"
        if qss_file.exists():
            self._current_theme = theme_name
            return qss_file.read_text(encoding="utf-8")
        return ""
    
    def apply_theme(self, app, theme_name: str = "dark"):
        """应用主题 QSS。"""
        theme_map = {
            "dark": "ui/styles/dark.qss",
            "light": "ui/styles/light.qss",
            "sepia": "ui/styles/sepia.qss",
        }
        qss_path = theme_map.get(theme_name)
        if qss_path and os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        self._current_theme = theme_name


style_manager = StyleManager()

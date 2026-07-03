"""应用配置管理 — 仅用于启动引导配置（data_dir 等 DB 初始化前需要的值）。

职责边界：
- config.json / AppConfig → 仅存储 bootstrap 配置（DB 路径、应用版本等）
- app_config 表 (app_config_service) → 存储运行时业务配置（主题、语言等）
- QSettings → 仅存储 UI 状态（几何、最近项目、撤销栈深度）
"""
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


class AppConfig:
    """应用配置单例。仅管理 bootstrap 配置。"""

    # 安装级默认值
    app_name: str = "Novel Writer"
    app_version: str = "1.0.0"
    data_dir: str = "~/NovelWriter"

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
        load_dotenv()
        self._config: dict = {}
        self._load_defaults()
        self._load_from_file()

    def _load_defaults(self):
        """默认值（环境变量优先）。"""
        self._config["data_dir"] = os.getenv(
            "NOVEL_DATA_DIR",
            str(Path.home() / ".novel-writer"),
        )
        self._config["app_name"] = os.getenv("APP_NAME", self.app_name)
        self._config["app_version"] = os.getenv("APP_VERSION", self.app_version)

    def _load_from_file(self):
        """从 config.json 补充覆盖。"""
        cfg_path = self._get_config_path()
        if cfg_path.exists():
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # 只读取已知的 bootstrap 键
                for key in ("data_dir", "app_name", "app_version"):
                    if key in data:
                        self._config[key] = data[key]
            except (json.JSONDecodeError, OSError):
                pass

    # ---- 接口 ----

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def set(self, key: str, value):
        self._config[key] = value

    def all(self) -> dict:
        return dict(self._config)

    def save(self) -> None:
        """持久化 bootstrap 配置到 config.json。"""
        cfg_path = self._get_config_path()
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        # 只保存 bootstrap 键
        to_save = {k: self._config[k] for k in ("data_dir", "app_name", "app_version") if k in self._config}
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2, ensure_ascii=False)

    def update(self, **kwargs) -> None:
        """批量更新 bootstrap 配置并自动保存。"""
        changed = False
        for key in ("data_dir", "app_name", "app_version"):
            if key in kwargs:
                self._config[key] = kwargs[key]
                changed = True
        if changed:
            self.save()

    # ---- 路径 ----

    @classmethod
    def _get_config_path(cls) -> Path:
        if sys.platform == "win32":
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path.home() / ".config"
        return base / "NovelWriter" / "config.json"


config = AppConfig()

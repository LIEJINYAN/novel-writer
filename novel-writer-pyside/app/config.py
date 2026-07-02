"""应用配置管理。"""
import os
from pathlib import Path
from dotenv import load_dotenv

class AppConfig:
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
        self._config = {}
        self._load_defaults()
    
    def _load_defaults(self):
        self._config["data_dir"] = os.getenv(
            "NOVEL_DATA_DIR",
            str(Path.home() / ".novel-writer"),
        )
        self._config["language"] = os.getenv("NOVEL_LANGUAGE", "zh-CN")
        self._config["theme"] = os.getenv("NOVEL_THEME", "dark")
        self._config["log_level"] = os.getenv("LOG_LEVEL", "INFO")
        
        # AI 配置
        self._config["default_ai_provider"] = os.getenv("DEFAULT_AI_PROVIDER", "openai")
        self._config["default_ai_model"] = os.getenv("DEFAULT_AI_MODEL", "gpt-4o")
    
    def get(self, key: str, default=None):
        return self._config.get(key, default)
    
    def set(self, key: str, value):
        self._config[key] = value
    
    def all(self) -> dict:
        return dict(self._config)


config = AppConfig()

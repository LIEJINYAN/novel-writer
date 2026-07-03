"""应用配置服务 — 读写 app_config 表。"""
from __future__ import annotations
from typing import Optional
from models import AppConfig
from models.database import db_manager


class AppConfigService:
    """应用级配置的键值对存储。"""

    def get(self, key: str, default: str = "") -> str:
        """读取配置。"""
        session = db_manager.get_app_session()
        try:
            cfg = session.query(AppConfig).filter_by(key=key).first()
            return cfg.value if cfg else default
        finally:
            session.close()

    def set(self, key: str, value: str) -> None:
        """写入配置（upsert）。"""
        session = db_manager.get_app_session()
        try:
            cfg = session.query(AppConfig).filter_by(key=key).first()
            if cfg:
                cfg.value = value
            else:
                cfg = AppConfig(key=key, value=value)
                session.add(cfg)
            session.commit()
        finally:
            session.close()

    def get_int(self, key: str, default: int = 0) -> int:
        val = self.get(key)
        try:
            return int(val) if val else default
        except ValueError:
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        val = self.get(key)
        if val.lower() in ("1", "true", "yes"):
            return True
        if val.lower() in ("0", "false", "no"):
            return False
        return default


app_config_service = AppConfigService()

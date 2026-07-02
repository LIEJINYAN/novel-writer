"""数据库连接管理器。"""
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    pass

class DatabaseManager:
    def __init__(self):
        self._engine = None
        self._session_factory = None
    
    @property
    def data_dir(self) -> Path:
        """应用数据目录。"""
        from app.config import AppConfig
        config = AppConfig()
        return Path(config.get("data_dir", Path.home() / ".novel-writer"))
    
    def init_db(self, db_path: str = None) -> None:
        """初始化数据库连接。"""
        if db_path is None:
            data_dir = self.data_dir
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "novel_writer.db")
        
        self._engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False,
        )
        
        # 启用 WAL 模式和 busy timeout
        with self._engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA busy_timeout=5000"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
        
        self._session_factory = sessionmaker(bind=self._engine)
        
        # 创建所有表
        Base.metadata.create_all(self._engine)
    
    def get_session(self):
        """获取数据库会话。"""
        if self._session_factory is None:
            raise RuntimeError("数据库未初始化，请先调用 init_db()")
        return self._session_factory()
    
    def close(self) -> None:
        """关闭数据库连接。"""
        if self._engine:
            self._engine.dispose()

# 全局单例
db_manager = DatabaseManager()

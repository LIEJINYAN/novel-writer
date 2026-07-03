"""数据库连接管理器 — 双层架构（应用级 DB + 项目级 DB）。"""
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class AppBase(DeclarativeBase):
    """应用级数据表的 Base（全局 DB）。"""
    pass


Base = AppBase  # 兼容旧代码


class ProjectBase(DeclarativeBase):
    """项目级数据表的 Base（每个项目独立 DB）。"""
    pass


class DatabaseManager:
    def __init__(self):
        self._app_engine = None
        self._app_session_factory = None
        self._project_engine = None
        self._project_session_factory = None

    @property
    def data_dir(self) -> Path:
        from app.config import AppConfig
        config = AppConfig()
        return Path(config.get("data_dir", Path.home() / ".novel-writer"))

    # ---- 应用级 DB ----

    def _get_app_db_path(self) -> str:
        return str(self.data_dir / "novel_writer.db")

    def init_db(self, db_path: str = None) -> None:
        """初始化应用级数据库（兼容旧入口）。"""
        return self.init_app_db(db_path)

    def init_app_db(self, db_path: str = None) -> None:
        """初始化应用级数据库。"""
        if db_path is None:
            db_path = self._get_app_db_path()
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._app_engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False,
        )
        with self._app_engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA busy_timeout=5000"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.execute(text("PRAGMA cache_size=-20000"))
            conn.execute(text("PRAGMA temp_store=MEMORY"))

        self._app_session_factory = sessionmaker(bind=self._app_engine)
        AppBase.metadata.create_all(self._app_engine)

        # 兼容迁移
        self._migrate_schema()

    def get_app_session(self):
        """获取应用级数据库会话。"""
        if self._app_session_factory is None:
            raise RuntimeError("应用数据库未初始化，请先调用 init_app_db()")
        return self._app_session_factory()

    def get_session(self):
        """兼容旧接口 — 返回应用级 session。"""
        return self.get_app_session()

    # ---- 项目级 DB ----

    @property
    def is_project_open(self) -> bool:
        return self._project_engine is not None

    def init_project_db(self, db_path: str) -> None:
        """初始化/打开项目级数据库。"""
        db_path_obj = Path(db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)

        self._project_engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False,
        )
        with self._project_engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA busy_timeout=5000"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.execute(text("PRAGMA cache_size=-20000"))
            conn.execute(text("PRAGMA temp_store=MEMORY"))

        self._project_session_factory = sessionmaker(bind=self._project_engine)
        ProjectBase.metadata.create_all(self._project_engine)

    def open_project(self, project_dir: str) -> None:
        """打开项目：初始化项目级 DB。"""
        self.close_project()
        db_path = Path(project_dir) / ".novel" / "project.db"
        self.init_project_db(str(db_path))

    def close_project(self) -> None:
        """关闭当前项目。"""
        if self._project_engine:
            self._project_engine.dispose()
            self._project_engine = None
            self._project_session_factory = None

    def get_project_session(self):
        """获取项目级数据库会话。"""
        if self._project_session_factory is None:
            raise RuntimeError("未打开项目，请先调用 open_project()")
        return self._project_session_factory()

    # ---- Schema 迁移（兼容旧单库） ----

    def _migrate_schema(self):
        """应用级 DB 的兼容迁移。"""
        import sqlite3
        db_path = self._app_engine.url.database if self._app_engine else None
        if not db_path:
            return
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("PRAGMA table_info(volumes)")
            cols = {row[1] for row in cursor.fetchall()}
            if "is_deleted" not in cols:
                conn.execute("ALTER TABLE volumes ADD COLUMN is_deleted INTEGER DEFAULT 0")
            if "deleted_at" not in cols:
                conn.execute("ALTER TABLE volumes ADD COLUMN deleted_at DATETIME")
            cursor = conn.execute("PRAGMA table_info(chapters)")
            cols = {row[1] for row in cursor.fetchall()}
            if "deleted_at" not in cols:
                conn.execute("ALTER TABLE chapters ADD COLUMN deleted_at DATETIME")
            conn.close()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"数据库字段迁移跳过: {e}")

        self._migrate_fk_cascade()
        self._migrate_ai_providers_schema()
        self._migrate_projects_schema()
        self._migrate_volumes_schema()

    def _migrate_fk_cascade(self):
        """为已有数据库的 FK 补上 ON DELETE CASCADE。"""
        import sqlite3, re
        db_path = self._app_engine.url.database if self._app_engine else None
        if not db_path:
            return

        conn = sqlite3.connect(db_path)
        try:
            tables = conn.execute(
                "SELECT name, sql FROM sqlite_master "
                "WHERE type='table' AND sql IS NOT NULL"
            ).fetchall()

            expected = self._get_expected_fk_strategy()
            migrated = False

            for name, old_sql in tables:
                if 'FOREIGN KEY' not in old_sql.upper():
                    continue
                if name not in expected:
                    continue

                fks = conn.execute(f"PRAGMA foreign_key_list({name})").fetchall()
                needs_fix = any(
                    fk[6] not in ('cascade', 'set null', 'no action')
                    and fk[3] in expected[name]
                    for fk in fks
                )
                if not needs_fix:
                    continue

                def add_on_delete(m):
                    clause = m.group(0)
                    fk_col = m.group(1)
                    strategy = expected[name].get(fk_col, 'CASCADE')
                    if 'ON DELETE' not in clause.upper():
                        clause += f" ON DELETE {strategy}"
                    return clause

                new_sql = re.sub(
                    r'FOREIGN KEY\s*\(\s*(\w+)\s*\)\s*REFERENCES\s+\w+\s*\([^)]+\)',
                    add_on_delete,
                    old_sql,
                    flags=re.IGNORECASE,
                )
                if new_sql == old_sql:
                    continue

                conn.execute("PRAGMA foreign_keys=OFF")
                conn.execute(f"ALTER TABLE {name} RENAME TO {name}_bak")
                conn.execute(new_sql)
                conn.execute(f"INSERT INTO {name} SELECT * FROM {name}_bak")
                conn.execute(f"DROP TABLE {name}_bak")
                migrated = True

            if migrated:
                conn.execute("PRAGMA foreign_keys=ON")
                conn.commit()
                import logging
                logging.getLogger(__name__).info("FK 级联删除迁移完成")
        except Exception as e:
            conn.rollback()
            import logging
            logging.getLogger(__name__).warning(f"FK 迁移跳过: {e}")
        finally:
            conn.close()

    def _get_expected_fk_strategy(self) -> dict:
        return {
            'characters': {'project_id': 'CASCADE'},
            'chapter_appearances': {'character_id': 'CASCADE', 'chapter_id': 'CASCADE'},
            'plot_arcs': {'project_id': 'CASCADE'},
            'plot_nodes': {
                'project_id': 'CASCADE',
                'arc_id': 'CASCADE',
                'chapter_id': 'SET NULL',
            },
            'plot_foreshadows': {
                'project_id': 'CASCADE',
                'node_id': 'CASCADE',
                'target_node_id': 'SET NULL',
            },
        }

    def close(self) -> None:
        """关闭所有连接。"""
        self.close_project()
        if self._app_engine:
            self._app_engine.dispose()


    def _migrate_ai_providers_schema(self):
        """迁移 ai_providers 表到新 schema。"""
        import sqlite3
        db_path = self._app_engine.url.database if self._app_engine else None
        if not db_path:
            return
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("PRAGMA table_info(ai_providers)")
            cols = {row[1] for row in cursor.fetchall()}
            # 旧 schema 有 name 列 → 需要重建
            if "name" in cols and "provider_name" not in cols:
                conn.execute("PRAGMA foreign_keys=OFF")
                conn.execute("ALTER TABLE ai_providers RENAME TO ai_providers_old")
                conn.execute("""
                    INSERT INTO ai_providers (provider_name, display_name, api_key, api_base, default_model, is_enabled, is_default, config)
                    SELECT name, display_name, api_key_encrypted, api_base, default_model, is_enabled, 0, NULL
                    FROM ai_providers_old
                """)
                conn.execute("DROP TABLE ai_providers_old")
                conn.execute("PRAGMA foreign_keys=ON")
                conn.commit()
            # 检查并加密明文 api_key 值（加密值以 gAAAAA 开头）
            has_api_key_col = "api_key" in cols
            if has_api_key_col:
                rows = conn.execute("SELECT id, api_key FROM ai_providers WHERE api_key IS NOT NULL AND api_key != ''").fetchall()
                for row_id, api_key_val in rows:
                    if not api_key_val.startswith("gAAAAA"):
                        try:
                            from utils.crypto import encrypt_api_key
                            encrypted = encrypt_api_key(api_key_val)
                            conn.execute("UPDATE ai_providers SET api_key = ? WHERE id = ?",
                                         (encrypted, row_id))
                        except Exception:
                            pass
                conn.commit()
            # 补上 temperature / max_tokens（新模型新增字段）
            for col_name, col_def in [("temperature", "FLOAT DEFAULT 0.8"),
                                       ("max_tokens", "INTEGER DEFAULT 4096")]:
                if col_name not in cols:
                    try:
                        conn.execute(f"ALTER TABLE ai_providers ADD COLUMN {col_name} {col_def}")
                    except Exception:
                        pass
            conn.commit()
            conn.close()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"ai_providers 迁移跳过: {e}")

    def _migrate_projects_schema(self):
        """为已有 projects 表补上新列。"""
        import sqlite3
        db_path = self._app_engine.url.database if self._app_engine else None
        if not db_path:
            return
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("PRAGMA table_info(projects)")
            cols = {row[1] for row in cursor.fetchall()}
            new_cols = {
                "total_words": "INTEGER DEFAULT 0",
                "chapter_count": "INTEGER DEFAULT 0",
                "last_opened_at": "DATETIME",
            }
            for col_name, col_def in new_cols.items():
                if col_name not in cols:
                    conn.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_def}")
            conn.close()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"projects 迁移跳过: {e}")

    def _migrate_volumes_schema(self):
        """迁移旧 volumes 表：补上 volume_number, name→title。"""
        import sqlite3
        db_path = self._app_engine.url.database if self._app_engine else None
        if not db_path:
            return
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("PRAGMA table_info(volumes)")
            cols = {row[1] for row in cursor.fetchall()}
            if "name" in cols and "title" not in cols:
                conn.execute("PRAGMA foreign_keys=OFF")
                conn.execute("ALTER TABLE volumes ADD COLUMN title VARCHAR(200) DEFAULT ''")
                conn.execute("UPDATE volumes SET title = name")
                conn.execute("PRAGMA foreign_keys=ON")
                conn.commit()
            if "volume_number" not in cols:
                conn.execute("ALTER TABLE volumes ADD COLUMN volume_number INTEGER DEFAULT 1")
                cursor2 = conn.execute("SELECT id, sort_order FROM volumes ORDER BY sort_order")
                for row_id, sort_order in cursor2.fetchall():
                    conn.execute("UPDATE volumes SET volume_number = ? WHERE id = ?",
                                 (sort_order or 1, row_id))
                conn.commit()
            conn.close()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"volumes 迁移跳过: {e}")


# 全局单例
db_manager = DatabaseManager()

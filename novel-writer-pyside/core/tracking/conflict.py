"""冲突追踪器 - 管理小说冲突的 CRUD 操作。"""
from __future__ import annotations
from typing import Optional
from models import Conflict
from models.database import DatabaseManager


class ConflictTracker:
    """冲突追踪器 - 管理冲突数据的增删改查。"""

    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager

    def create(self, project_id: int, **data) -> Conflict:
        """创建冲突。"""
        session = self._db.get_project_session()
        try:
            conflict = Conflict(**data)
            session.add(conflict)
            session.commit()
            session.refresh(conflict)
            return conflict
        finally:
            session.close()

    def get(self, conflict_id: int) -> Optional[Conflict]:
        """获取单个冲突。"""
        session = self._db.get_project_session()
        try:
            return session.query(Conflict).filter_by(id=conflict_id).first()
        finally:
            session.close()

    def update(self, conflict_id: int, **data) -> Optional[Conflict]:
        """更新冲突。"""
        session = self._db.get_project_session()
        try:
            conflict = session.query(Conflict).filter_by(id=conflict_id).first()
            if not conflict:
                return None
            for key, value in data.items():
                if hasattr(conflict, key):
                    setattr(conflict, key, value)
            session.commit()
            session.refresh(conflict)
            return conflict
        finally:
            session.close()

    def delete(self, conflict_id: int) -> bool:
        """删除冲突。"""
        session = self._db.get_project_session()
        try:
            conflict = session.query(Conflict).filter_by(id=conflict_id).first()
            if not conflict:
                return False
            session.delete(conflict)
            session.commit()
            return True
        finally:
            session.close()

    def list_all(self, project_id: int) -> list[Conflict]:
        """列出所有冲突，按 sort_order 排序。"""
        session = self._db.get_project_session()
        try:
            return session.query(Conflict).order_by(Conflict.sort_order).all()
        finally:
            session.close()

"""项目仓储 - 项目数据访问层。"""
from __future__ import annotations
from typing import List, Optional

from models.project import Project
from .base import BaseRepository


class ProjectRepository(BaseRepository):
    """项目仓储 - 封装项目数据访问。"""

    def __init__(self):
        super().__init__(Project)

    def get_by_name(self, name: str) -> Optional[Project]:
        """根据名称获取项目。"""
        session = self._get_session()
        try:
            return session.query(Project).filter_by(name=name, is_deleted=False).first()
        finally:
            session.close()

    def list_recent(self, limit: int = 10) -> List[Project]:
        """获取最近打开的项目列表。"""
        session = self._get_session()
        try:
            return session.query(Project)\
                .filter_by(is_deleted=False)\
                .order_by(Project.last_opened_at.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()

    def search(self, keyword: str) -> List[Project]:
        """按关键词搜索项目。"""
        session = self._get_session()
        try:
            like = f"%{keyword}%"
            return session.query(Project)\
                .filter_by(is_deleted=False)\
                .filter(Project.name.like(like) | Project.description.like(like))\
                .all()
        finally:
            session.close()

    def _get_session(self):
        from models.database import db_manager
        return db_manager.get_session()

"""章节仓储 - 章节数据访问层。"""
from __future__ import annotations
from typing import List, Optional

from models import Volume, Chapter
from .base import BaseRepository


class ChapterRepository(BaseRepository):
    """章节仓储 - 封装章节数据访问。"""

    def __init__(self):
        super().__init__(Chapter)

    def list_by_project(self, project_id: int) -> List[Chapter]:
        """获取项目所有章节。"""
        session = self._get_session()
        try:
            return session.query(Chapter)\
                .filter_by(project_id=project_id, is_deleted=False)\
                .order_by(Chapter.chapter_number.asc())\
                .all()
        finally:
            session.close()

    def list_by_volume(self, volume_id: int) -> List[Chapter]:
        """获取分卷下所有章节。"""
        session = self._get_session()
        try:
            return session.query(Chapter)\
                .filter_by(volume_id=volume_id, is_deleted=False)\
                .order_by(Chapter.chapter_number.asc())\
                .all()
        finally:
            session.close()

    def _get_session(self):
        from models.database import db_manager
        return db_manager.get_session()


class VolumeRepository(BaseRepository):
    """分卷仓储 - 封装分卷数据访问。"""

    def __init__(self):
        super().__init__(Volume)

    def list_by_project(self, project_id: int) -> List[Volume]:
        """获取项目所有分卷。"""
        session = self._get_session()
        try:
            return session.query(Volume)\
                .filter_by(project_id=project_id)\
                .order_by(Volume.sort_order.asc())\
                .all()
        finally:
            session.close()

    def _get_session(self):
        from models.database import db_manager
        return db_manager.get_session()

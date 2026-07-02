"""角色仓储 - 角色数据访问层。"""
from __future__ import annotations
from typing import List

from models.character import Character, ChapterAppearance
from .base import BaseRepository


class CharacterRepository(BaseRepository):
    """角色仓储 - 封装角色数据访问。"""

    def __init__(self):
        super().__init__(Character)

    def list_by_project(self, project_id: int) -> List[Character]:
        """获取项目所有角色。"""
        session = self._get_session()
        try:
            return session.query(Character)\
                .filter_by(project_id=project_id, is_deleted=False)\
                .order_by(Character.name.asc())\
                .all()
        finally:
            session.close()

    def search(self, project_id: int, keyword: str) -> List[Character]:
        """搜索角色。"""
        session = self._get_session()
        try:
            like = f"%{keyword}%"
            return session.query(Character)\
                .filter_by(project_id=project_id, is_deleted=False)\
                .filter(Character.name.like(like) | Character.aliases.like(like))\
                .all()
        finally:
            session.close()

    def _get_session(self):
        from models.database import db_manager
        return db_manager.get_session()


class ChapterAppearanceRepository(BaseRepository):
    """出场记录仓储 - 封装出场记录数据访问。"""

    def __init__(self):
        super().__init__(ChapterAppearance)

    def list_by_character(self, character_id: int) -> List[ChapterAppearance]:
        """获取角色的所有出场记录。"""
        session = self._get_session()
        try:
            return session.query(ChapterAppearance)\
                .filter_by(character_id=character_id)\
                .order_by(ChapterAppearance.chapter_id.asc())\
                .all()
        finally:
            session.close()

    def list_by_chapter(self, chapter_id: int) -> List[ChapterAppearance]:
        """获取章节中的所有角色出场记录。"""
        session = self._get_session()
        try:
            return session.query(ChapterAppearance)\
                .filter_by(chapter_id=chapter_id)\
                .all()
        finally:
            session.close()

    def _get_session(self):
        from models.database import db_manager
        return db_manager.get_session()

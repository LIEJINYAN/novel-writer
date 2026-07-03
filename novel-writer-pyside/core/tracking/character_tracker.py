"""角色追踪器 - 管理角色数据和出场记录。

提供核心数据库逻辑，供 services/character_service.py 委托调用。
"""

from __future__ import annotations
from typing import Optional
from models import Character, ChapterAppearance
from models.database import DatabaseManager


class CharacterTracker:
    """角色追踪器 - 管理角色、出场记录和角色弧。"""

    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager

    # ===== 角色 CRUD =====

    def add_character(self, project_id: int, **data) -> Character:
        """添加角色。"""
        session = self._db.get_project_session()
        try:
            if "role_type" in data:
                data["role"] = data.pop("role_type")
            char = Character(**data)
            session.add(char)
            session.commit()
            session.refresh(char)
            return char
        finally:
            session.close()

    def get_character(self, character_id: int) -> Optional[Character]:
        """获取角色。"""
        session = self._db.get_project_session()
        try:
            return session.query(Character).filter(
                Character.id == character_id,
                Character.is_deleted == 0
            ).first()
        finally:
            session.close()

    def update_character(self, character_id: int, **data) -> Optional[Character]:
        """更新角色。"""
        session = self._db.get_project_session()
        try:
            char = session.query(Character).filter_by(id=character_id).first()
            if not char:
                return None
            if "role_type" in data:
                data["role"] = data.pop("role_type")
            for key, value in data.items():
                if hasattr(char, key):
                    setattr(char, key, value)
            session.commit()
            session.refresh(char)
            return char
        finally:
            session.close()

    def delete_character(self, character_id: int) -> bool:
        """软删除角色。"""
        session = self._db.get_project_session()
        try:
            char = session.query(Character).filter_by(id=character_id).first()
            if not char:
                return False
            char.is_deleted = 1
            session.commit()
            return True
        finally:
            session.close()

    def list_characters(self, project_id: int, search: str = "",
                        role_type: str = "", status: str = "") -> list[Character]:
        """列出角色，支持搜索和筛选。"""
        session = self._db.get_project_session()
        try:
            query = session.query(Character).filter(
                Character.is_deleted == 0
            )
            if search:
                like = f"%{search}%"
                query = query.filter(
                    Character.name.like(like) | Character.aliases.like(like)
                )
            if role_type:
                query = query.filter(Character.role == role_type)
            return query.order_by(Character.name).all()
        finally:
            session.close()

    def count_characters(self, project_id: int) -> int:
        """统计角色数。"""
        session = self._db.get_project_session()
        try:
            return session.query(Character).filter(
                Character.is_deleted == 0
            ).count()
        finally:
            session.close()

    # ===== 出场记录 =====

    def remove_appearance(self, character_id: int, chapter_id: int) -> bool:
        """删除指定角色在指定章节的出场记录。"""
        session = self._db.get_project_session()
        try:
            app = session.query(ChapterAppearance).filter(
                ChapterAppearance.character_id == character_id,
                ChapterAppearance.chapter_id == chapter_id,
            ).first()
            if not app:
                return False
            session.delete(app)
            session.commit()
            return True
        finally:
            session.close()

    def record_appearance(self, character_id: int, chapter_id: int,
                          role: str = "次要", context: str = "") -> ChapterAppearance:
        """记录角色出场。"""
        session = self._db.get_project_session()
        try:
            app = ChapterAppearance(
                character_id=character_id,
                chapter_id=chapter_id,
                role=role,
                context=context,
            )
            session.add(app)
            session.commit()
            session.refresh(app)
            return app
        finally:
            session.close()

    def get_appearances(self, character_id: int) -> list[dict]:
        """获取出场记录（含章节标题）。"""
        session = self._db.get_project_session()
        try:
            results = session.query(ChapterAppearance).filter(
                ChapterAppearance.character_id == character_id
            ).order_by(ChapterAppearance.id).all()
            return [
                {
                    "id": a.id,
                    "chapter_id": a.chapter_id,
                    "chapter_title": a.chapter.title if a.chapter else "",
                    "role": a.role,
                    "context": a.context,
                }
                for a in results
            ]
        finally:
            session.close()

    # ===== 角色弧 =====

    def get_character_arc(self, character_id: int) -> str:
        """获取角色弧描述。"""
        session = self._db.get_project_session()
        try:
            char = session.query(Character).filter_by(id=character_id).first()
            if char and char.character_arc:
                return char.character_arc
            return ""
        finally:
            session.close()

    def update_character_status(self, character_id: int, status: str) -> Optional[Character]:
        """更新角色状态（通过 role 字段或自定义状态）。"""
        session = self._db.get_project_session()
        try:
            char = session.query(Character).filter_by(id=character_id).first()
            if not char:
                return None
            char.role = status
            session.commit()
            session.refresh(char)
            return char
        finally:
            session.close()

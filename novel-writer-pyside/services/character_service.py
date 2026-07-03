"""角色服务 - CRUD 和出场记录管理。"""
from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import joinedload
from models import Character, ChapterAppearance
from models.database import db_manager


class CharacterService:

    def create(self, project_id: int, **data) -> Character:
        """创建角色。"""
        session = db_manager.get_project_session()
        try:
            # 兼容旧字段名映射
            if "role_type" in data:
                data["role"] = data.pop("role_type")
            char = Character(**data)
            session.add(char)
            session.commit()
            session.refresh(char)
            return char
        finally:
            session.close()

    def get(self, character_id: int) -> Optional[Character]:
        """获取角色。"""
        session = db_manager.get_project_session()
        try:
            return session.query(Character).filter(
                Character.id == character_id,
                Character.is_deleted == 0
            ).first()
        finally:
            session.close()

    def update(self, character_id: int, **data) -> Optional[Character]:
        """更新角色。"""
        session = db_manager.get_project_session()
        try:
            char = session.query(Character).filter_by(id=character_id).first()
            if not char:
                return None
            # 兼容旧字段名
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

    def delete(self, character_id: int) -> bool:
        """软删除角色。"""
        session = db_manager.get_project_session()
        try:
            char = session.query(Character).filter_by(id=character_id).first()
            if not char:
                return False
            char.is_deleted = 1
            session.commit()
            return True
        finally:
            session.close()

    def list(self, project_id: int, search: str = "",
             role_type: str = "", status: str = "") -> list[Character]:
        """列出角色，支持搜索和筛选。"""
        session = db_manager.get_project_session()
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
                query = query.filter(Character.role_type == role_type)
            if status:
                query = query.filter(Character.status == status)
            return query.order_by(Character.name).all()
        finally:
            session.close()

    def add_appearance(self, character_id: int, chapter_id: int,
                       role: str = "次要", context: str = "") -> ChapterAppearance:
        """添加出场记录。"""
        session = db_manager.get_project_session()
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
        session = db_manager.get_project_session()
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

    def count(self, project_id: int) -> int:
        """统计角色数。"""
        session = db_manager.get_project_session()
        try:
            return session.query(Character).filter(
                Character.is_deleted == 0
            ).count()
        finally:
            session.close()


character_service = CharacterService()

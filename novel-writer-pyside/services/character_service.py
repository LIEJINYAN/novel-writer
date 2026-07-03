"""角色服务 - CRUD 和出场记录管理（委托至 CharacterTracker）。"""
from __future__ import annotations
from typing import Optional
from models import Character, ChapterAppearance
from models.database import db_manager
from core.tracking.character_tracker import CharacterTracker


class CharacterService:

    def __init__(self, repo: Optional["CharacterRepository"] = None):
        """可选的仓储依赖注入。

        Args:
            repo: 角色仓储实例（不传时使用 db_manager 直连）
        """
        self._repo = repo
        self._tracker = CharacterTracker(db_manager)

    def create(self, project_id: int, **data) -> Character:
        """创建角色。"""
        return self._tracker.add_character(project_id, **data)

    def get(self, character_id: int) -> Optional[Character]:
        """获取角色。"""
        return self._tracker.get_character(character_id)

    def update(self, character_id: int, **data) -> Optional[Character]:
        """更新角色。"""
        return self._tracker.update_character(character_id, **data)

    def delete(self, character_id: int) -> bool:
        """软删除角色。"""
        return self._tracker.delete_character(character_id)

    def list(self, project_id: int, search: str = "",
             role_type: str = "", status: str = "") -> list[Character]:
        """列出角色，支持搜索和筛选。"""
        return self._tracker.list_characters(project_id, search, role_type, status)

    def add_appearance(self, character_id: int, chapter_id: int,
                       role: str = "次要", context: str = "") -> ChapterAppearance:
        """添加出场记录。"""
        return self._tracker.record_appearance(character_id, chapter_id, role, context)

    def remove_appearance(self, character_id: int, chapter_id: int) -> bool:
        """删除出场记录。"""
        return self._tracker.remove_appearance(character_id, chapter_id)

    def get_appearances(self, character_id: int) -> list[dict]:
        """获取出场记录（含章节标题）。"""
        return self._tracker.get_appearances(character_id)

    def count(self, project_id: int) -> int:
        """统计角色数。"""
        return self._tracker.count_characters(project_id)


character_service = CharacterService()

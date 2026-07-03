"""关系/派系服务 - CRUD 和变化历史自动记录（委托至 RelationshipTracker）。"""
from __future__ import annotations
from typing import Optional
from models import Relationship, RelationshipChange, Faction, FactionMember
from models.database import db_manager
from core.tracking.relationship_tracker import RelationshipTracker


class RelationshipService:

    def __init__(self):
        self._tracker = RelationshipTracker(db_manager)

    # ---- 关系 CRUD ----

    def create(self, project_id: int, character_a_id: int, character_b_id: int,
               **data) -> Relationship:
        """创建关系，自动记录变化历史。"""
        return self._tracker.add_relationship(
            project_id, character_a_id, character_b_id, **data
        )

    def get(self, relationship_id: int) -> Optional[Relationship]:
        """获取关系（含角色信息、变化历史）。"""
        return self._tracker.get_relationship(relationship_id)

    def update(self, relationship_id: int, **data) -> Optional[Relationship]:
        """更新关系，自动记录变化。"""
        return self._tracker.update_relationship(relationship_id, **data)

    def delete(self, relationship_id: int) -> bool:
        """删除关系。"""
        return self._tracker.delete_relationship(relationship_id)

    def list(self, project_id: int, search: str = "") -> list[dict]:
        """列出关系，支持按角色名搜索。"""
        return self._tracker.list_relationships(project_id, search)

    # ---- 派系 CRUD ----

    def create_faction(self, project_id: int, name: str, **data) -> Faction:
        """创建派系。"""
        return self._tracker.add_faction(project_id, name, **data)

    def get_faction(self, faction_id: int) -> Optional[Faction]:
        """获取派系（含领导者和成员信息）。"""
        return self._tracker.get_faction(faction_id)

    def update_faction(self, faction_id: int, **data) -> Optional[Faction]:
        """更新派系。"""
        return self._tracker.update_faction(faction_id, **data)

    def delete_faction(self, faction_id: int) -> bool:
        """删除派系（级联删除成员）。"""
        return self._tracker.delete_faction(faction_id)

    def list_factions(self, project_id: int) -> list[dict]:
        """列出派系（含领导者名和成员数）。"""
        return self._tracker.list_factions(project_id)

    # ---- 派系成员 ----

    def add_member(self, faction_id: int, character_id: int,
                   role: str = "", core: bool = False) -> Optional[FactionMember]:
        """添加派系成员。"""
        return self._tracker.add_faction_member(
            faction_id, character_id, role, core
        )

    def remove_member(self, faction_id: int, character_id: int) -> bool:
        """移除派系成员。"""
        return self._tracker.remove_faction_member(faction_id, character_id)

    def list_faction_members(self, faction_id: int) -> list[FactionMember]:
        """列出派系成员。"""
        return self._tracker.list_faction_members(faction_id)


relationship_service = RelationshipService()

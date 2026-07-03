"""关系/派系服务 - CRUD 和变化历史自动记录。"""
from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import joinedload
from models import Relationship, RelationshipChange, Faction, FactionMember
from models.database import db_manager


class RelationshipService:

    # ---- 关系 CRUD ----

    def create(self, project_id: int, character_a_id: int, character_b_id: int,
               **data) -> Relationship:
        """创建关系，自动记录变化历史。"""
        session = db_manager.get_project_session()
        try:
            rel = Relationship(
                character_a_id=character_a_id,
                character_b_id=character_b_id,
                **data
            )
            session.add(rel)
            session.flush()

            # 自动记录"新建"
            change = RelationshipChange(
                relationship_id=rel.id,
                change_type="新建",
                old_relation="",
                new_relation=data.get("current_relation", ""),
                description="关系建立",
            )
            session.add(change)
            session.commit()
            session.refresh(rel)
            return rel
        finally:
            session.close()

    def get(self, relationship_id: int) -> Optional[Relationship]:
        """获取关系（含角色信息、变化历史）。"""
        session = db_manager.get_project_session()
        try:
            return session.query(Relationship).filter(Relationship.id == relationship_id).first()
        finally:
            session.close()

    def update(self, relationship_id: int, **data) -> Optional[Relationship]:
        """更新关系，自动记录变化。"""
        session = db_manager.get_project_session()
        try:
            rel = session.query(Relationship).filter_by(id=relationship_id).first()
            if not rel:
                return None

            old_val = rel.current_relation
            for key, value in data.items():
                if hasattr(rel, key):
                    setattr(rel, key, value)

            session.flush()

            # 如果关系标签有变化，自动记录
            new_val = data.get("current_relation", old_val)
            if new_val != old_val:
                change = RelationshipChange(
                    relationship_id=rel.id,
                    change_type="变化",
                    old_relation=old_val,
                    new_relation=new_val,
                    description=f"关系状态变化: {old_val} → {new_val}",
                )
                session.add(change)

            session.commit()
            session.refresh(rel)
            return rel
        finally:
            session.close()

    def delete(self, relationship_id: int) -> bool:
        """删除关系。"""
        session = db_manager.get_project_session()
        try:
            rel = session.query(Relationship).filter_by(id=relationship_id).first()
            if not rel:
                return False
            session.delete(rel)
            session.commit()
            return True
        finally:
            session.close()

    def list(self, project_id: int, search: str = "") -> list[dict]:
        """列出关系，支持按角色名搜索。"""
        session = db_manager.get_project_session()
        try:
            query = session.query(Relationship)

            if search:
                like = f"%{search}%"
                query = query.join(Relationship.character_a).join(
                    Relationship.character_b, aliased=True
                )

            results = query.order_by(Relationship.id).all()
            return [
                {
                    "id": r.id,
                    "character_a_id": r.character_a_id,
                    "character_a_name": r.character_a.name if r.character_a else "",
                    "character_b_id": r.character_b_id,
                    "character_b_name": r.character_b.name if r.character_b else "",
                    "relationship_type": r.relationship_type,
                    "current_relation": r.current_relation,
                    "intensity": r.intensity,
                    "notes": r.notes,
                }
                for r in results
            ]
        finally:
            session.close()

    # ---- 派系 CRUD ----

    def create_faction(self, project_id: int, name: str, **data) -> Faction:
        """创建派系。"""
        session = db_manager.get_project_session()
        try:
            fac = Faction(name=name, **data)
            session.add(fac)
            session.commit()
            session.refresh(fac)
            return fac
        finally:
            session.close()

    def get_faction(self, faction_id: int) -> Optional[Faction]:
        """获取派系（含领导者和成员信息）。"""
        session = db_manager.get_project_session()
        try:
            return session.query(Faction).filter(Faction.id == faction_id).first()
        finally:
            session.close()

    def update_faction(self, faction_id: int, **data) -> Optional[Faction]:
        """更新派系。"""
        session = db_manager.get_project_session()
        try:
            fac = session.query(Faction).filter_by(id=faction_id).first()
            if not fac:
                return None
            for key, value in data.items():
                if hasattr(fac, key):
                    setattr(fac, key, value)
            session.commit()
            session.refresh(fac)
            return fac
        finally:
            session.close()

    def delete_faction(self, faction_id: int) -> bool:
        """删除派系（级联删除成员）。"""
        session = db_manager.get_project_session()
        try:
            fac = session.query(Faction).filter_by(id=faction_id).first()
            if not fac:
                return False
            session.delete(fac)
            session.commit()
            return True
        finally:
            session.close()

    def list_factions(self, project_id: int) -> list[dict]:
        """列出派系（含领导者名和成员数）。"""
        session = db_manager.get_project_session()
        try:
            results = session.query(Faction).order_by(Faction.name).all()
            return [
                {
                    "id": f.id,
                    "name": f.name,
                    "description": f.description,
                    "leader_name": f.leader.name if f.leader else "",
                    "member_count": len(f.members),
                    "status": f.status,
                }
                for f in results
            ]
        finally:
            session.close()

    # ---- 派系成员 ----

    def add_member(self, faction_id: int, character_id: int,
                   role: str = "", core: bool = False) -> Optional[FactionMember]:
        """添加派系成员。"""
        session = db_manager.get_project_session()
        try:
            existing = session.query(FactionMember).filter_by(
                faction_id=faction_id, character_id=character_id
            ).first()
            if existing:
                return existing

            members = session.query(FactionMember).filter_by(faction_id=faction_id).count()
            member = FactionMember(
                faction_id=faction_id,
                character_id=character_id,
                role_in_faction=role,
                is_core_member=1 if core else 0,
                sort_order=members,
            )
            session.add(member)
            session.commit()
            session.refresh(member)
            return member
        finally:
            session.close()

    def remove_member(self, faction_id: int, character_id: int) -> bool:
        """移除派系成员。"""
        session = db_manager.get_project_session()
        try:
            member = session.query(FactionMember).filter_by(
                faction_id=faction_id, character_id=character_id
            ).first()
            if not member:
                return False
            session.delete(member)
            session.commit()
            return True
        finally:
            session.close()

    def list_faction_members(self, faction_id: int) -> list[FactionMember]:
        """列出派系成员。"""
        session = db_manager.get_project_session()
        try:
            return session.query(FactionMember).filter(
                FactionMember.faction_id == faction_id
            ).order_by(FactionMember.sort_order).all()
        finally:
            session.close()


relationship_service = RelationshipService()

"""世界观服务 - CRUD 和树形查询。"""
from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import joinedload
from models import WorldSetting
from models.database import db_manager


class WorldService:

    def create(self, project_id: int, name: str, **data) -> WorldSetting:
        """创建世界观条目。"""
        session = db_manager.get_project_session()
        try:
            ws = WorldSetting(name=name, **data)
            session.add(ws)
            session.commit()
            session.refresh(ws)
            return ws
        finally:
            session.close()

    def get(self, setting_id: int) -> Optional[WorldSetting]:
        """获取条目（含子条目）。"""
        session = db_manager.get_project_session()
        try:
            return session.query(WorldSetting).filter(WorldSetting.id == setting_id).first()
        finally:
            session.close()

    def update(self, setting_id: int, **data) -> Optional[WorldSetting]:
        """更新条目。"""
        session = db_manager.get_project_session()
        try:
            ws = session.query(WorldSetting).filter_by(id=setting_id).first()
            if not ws:
                return None
            for key, value in data.items():
                if hasattr(ws, key):
                    setattr(ws, key, value)
            session.commit()
            session.refresh(ws)
            return ws
        finally:
            session.close()

    def delete(self, setting_id: int) -> bool:
        """删除条目（子节点 parent_id 置 NULL）。"""
        session = db_manager.get_project_session()
        try:
            ws = session.query(WorldSetting).filter_by(id=setting_id).first()
            if not ws:
                return False
            # 子节点 parent_id 置 NULL
            session.query(WorldSetting).filter_by(parent_id=setting_id).update(
                {"parent_id": None}, synchronize_session=False
            )
            session.delete(ws)
            session.commit()
            return True
        finally:
            session.close()

    def list(self, project_id: int, type_filter: str = "",
             search: str = "") -> list[WorldSetting]:
        """列出条目，支持类型筛选和搜索。"""
        session = db_manager.get_project_session()
        try:
            query = session.query(WorldSetting)
            if type_filter:
                query = query.filter(WorldSetting.setting_type == type_filter)
            if search:
                like = f"%{search}%"
                query = query.filter(WorldSetting.name.like(like) | WorldSetting.tags.like(like))
            return query.order_by(WorldSetting.sort_order, WorldSetting.name).all()
        finally:
            session.close()

    def get_tree(self, project_id: int) -> list[dict]:
        """返回树形结构（仅顶层节点带 children）。"""
        all_items = self.list(project_id)

        # 构建 id → item dict
        item_map: dict[int, dict] = {}
        for item in all_items:
            item_map[item.id] = {
                "id": item.id,
                "name": item.name,
                "setting_type": item.setting_type,
                "importance": item.importance,
                "parent_id": item.parent_id,
                "tags": item.tags or "",
                "children": [],
            }

        # 构建树
        roots: list[dict] = []
        for node in item_map.values():
            if node["parent_id"] and node["parent_id"] in item_map:
                item_map[node["parent_id"]]["children"].append(node)
            else:
                roots.append(node)

        return roots


world_service = WorldService()

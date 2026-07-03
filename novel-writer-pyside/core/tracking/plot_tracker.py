"""情节追踪器 - 管理情节节点、弧线、伏笔和冲突。

提供核心数据库逻辑，供 services/plot_service.py 委托调用。
"""

from __future__ import annotations
from typing import Optional
from models import PlotNode, Foreshadowing, Conflict
from models.database import DatabaseManager


class PlotTracker:
    """情节追踪器 - 管理情节节点、伏笔和冲突。"""

    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager

    # ===== 弧线 CRUD =====

    def create_arc(self, project_id: int, name: str,
                   description: str = "", sort_order: int = 0) -> PlotNode:
        """创建情节弧线（本质为 plot_type 标记的 PlotNode）。"""
        session = self._db.get_project_session()
        try:
            arc = PlotNode(name=name, description=description,
                           sort_order=sort_order, plot_type="arc")
            session.add(arc)
            session.commit()
            session.refresh(arc)
            return arc
        finally:
            session.close()

    def get_arc(self, arc_id: int) -> Optional[PlotNode]:
        """获取弧线。"""
        session = self._db.get_project_session()
        try:
            return session.query(PlotNode).filter_by(id=arc_id).first()
        finally:
            session.close()

    def update_arc(self, arc_id: int, **data) -> Optional[PlotNode]:
        """更新弧线。"""
        session = self._db.get_project_session()
        try:
            arc = session.query(PlotNode).filter_by(id=arc_id).first()
            if not arc:
                return None
            for key, value in data.items():
                if hasattr(arc, key):
                    setattr(arc, key, value)
            session.commit()
            session.refresh(arc)
            return arc
        finally:
            session.close()

    def delete_arc(self, arc_id: int) -> bool:
        """删除弧线。"""
        session = self._db.get_project_session()
        try:
            arc = session.query(PlotNode).filter_by(id=arc_id).first()
            if not arc:
                return False
            session.delete(arc)
            session.commit()
            return True
        finally:
            session.close()

    def list_arcs(self, project_id: int) -> list[PlotNode]:
        """列出弧线。"""
        session = self._db.get_project_session()
        try:
            return session.query(PlotNode)\
                .order_by(PlotNode.sort_order).all()
        finally:
            session.close()

    # ===== 节点 CRUD =====

    def add_plot_node(self, project_id: int, **data) -> PlotNode:
        """添加情节节点。"""
        session = self._db.get_project_session()
        try:
            title = data.pop("name", "")
            arc_id = data.pop("parent_id", None)
            node = PlotNode(name=title, parent_id=arc_id, **data)
            session.add(node)
            session.commit()
            session.refresh(node)
            return node
        finally:
            session.close()

    def get_node(self, node_id: int) -> Optional[PlotNode]:
        """获取节点。"""
        session = self._db.get_project_session()
        try:
            return session.query(PlotNode).filter_by(id=node_id).first()
        finally:
            session.close()

    def update_node(self, node_id: int, **data) -> Optional[PlotNode]:
        """更新节点。"""
        session = self._db.get_project_session()
        try:
            node = session.query(PlotNode).filter_by(id=node_id).first()
            if not node:
                return None
            if "title" in data:
                data["name"] = data.pop("title")
            for key, value in data.items():
                if hasattr(node, key):
                    setattr(node, key, value)
            session.commit()
            session.refresh(node)
            return node
        finally:
            session.close()

    def update_node_status(self, node_id: int, status: str) -> Optional[PlotNode]:
        """更新节点状态。"""
        session = self._db.get_project_session()
        try:
            node = session.query(PlotNode).filter_by(id=node_id).first()
            if not node:
                return None
            node.status = status
            session.commit()
            session.refresh(node)
            return node
        finally:
            session.close()

    def delete_node(self, node_id: int) -> bool:
        """删除节点。"""
        session = self._db.get_project_session()
        try:
            node = session.query(PlotNode).filter_by(id=node_id).first()
            if not node:
                return False
            session.delete(node)
            session.commit()
            return True
        finally:
            session.close()

    def list_nodes(self, project_id: int, arc_id: Optional[int] = None,
                   status: Optional[str] = None) -> list[PlotNode]:
        """列出节点，可选按弧线或状态筛选。"""
        session = self._db.get_project_session()
        try:
            query = session.query(PlotNode)
            if arc_id is not None:
                query = query.filter(PlotNode.parent_id == arc_id)
            if status:
                query = query.filter(PlotNode.status == status)
            return query.order_by(PlotNode.sort_order).all()
        finally:
            session.close()

    # ===== 伏笔 CRUD =====

    def add_foreshadowing(self, project_id: int, **data) -> Foreshadowing:
        """添加伏笔。"""
        session = self._db.get_project_session()
        try:
            fs = Foreshadowing(**data)
            session.add(fs)
            session.commit()
            session.refresh(fs)
            return fs
        finally:
            session.close()

    def get_foreshadowing(self, foreshadow_id: int) -> Optional[Foreshadowing]:
        """获取伏笔。"""
        session = self._db.get_project_session()
        try:
            return session.query(Foreshadowing).filter_by(id=foreshadow_id).first()
        finally:
            session.close()

    def update_foreshadowing(self, foreshadow_id: int, **data) -> Optional[Foreshadowing]:
        """更新伏笔。"""
        session = self._db.get_project_session()
        try:
            fs = session.query(Foreshadowing).filter_by(id=foreshadow_id).first()
            if not fs:
                return None
            for key, value in data.items():
                if hasattr(fs, key):
                    setattr(fs, key, value)
            session.commit()
            session.refresh(fs)
            return fs
        finally:
            session.close()

    def delete_foreshadowing(self, foreshadow_id: int) -> bool:
        """删除伏笔。"""
        session = self._db.get_project_session()
        try:
            fs = session.query(Foreshadowing).filter_by(id=foreshadow_id).first()
            if not fs:
                return False
            session.delete(fs)
            session.commit()
            return True
        finally:
            session.close()

    def list_foreshadowings(self, node_id: Optional[int] = None) -> list[Foreshadowing]:
        """列出伏笔，可选按节点筛选。"""
        session = self._db.get_project_session()
        try:
            query = session.query(Foreshadowing)
            if node_id is not None:
                query = query.filter(Foreshadowing.id == node_id)
            return query.all()
        finally:
            session.close()

    # ===== 冲突管理 =====

    def add_conflict(self, project_id: int, **data) -> Conflict:
        """添加冲突。"""
        session = self._db.get_project_session()
        try:
            conflict = Conflict(**data)
            session.add(conflict)
            session.commit()
            session.refresh(conflict)
            return conflict
        finally:
            session.close()

    def get_conflict(self, conflict_id: int) -> Optional[Conflict]:
        """获取冲突。"""
        session = self._db.get_project_session()
        try:
            return session.query(Conflict).filter_by(id=conflict_id).first()
        finally:
            session.close()

    def update_conflict(self, conflict_id: int, **data) -> Optional[Conflict]:
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

    def delete_conflict(self, conflict_id: int) -> bool:
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

    def list_conflicts(self, project_id: int) -> list[Conflict]:
        """列出冲突。"""
        session = self._db.get_project_session()
        try:
            return session.query(Conflict).order_by(Conflict.sort_order).all()
        finally:
            session.close()

    # ===== 情节阶段 =====

    def get_current_stage(self, project_id: int) -> str:
        """获取当前情节阶段。

        查找状态为 in_progress 的第一个节点，返回其 stage_key。
        """
        session = self._db.get_project_session()
        try:
            node = session.query(PlotNode).filter(
                PlotNode.status == "in_progress"
            ).order_by(PlotNode.sort_order).first()
            if node and node.stage_key:
                return node.stage_key
            return "unknown"
        finally:
            session.close()

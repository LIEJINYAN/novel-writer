"""情节服务 - 弧线、节点、伏笔管理。"""
from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import joinedload
from models import PlotArc, PlotNode, PlotForeshadow
from models.database import db_manager


class PlotService:

    # ===== 弧线 CRUD =====

    def create_arc(self, project_id: int, name: str,
                   description: str = "", sort_order: int = 0) -> PlotArc:
        session = db_manager.get_project_session()
        try:
            arc = PlotArc(name=name,
                          description=description, sort_order=sort_order)
            session.add(arc)
            session.commit()
            session.refresh(arc)
            return arc
        finally:
            session.close()

    def get_arc(self, arc_id: int) -> Optional[PlotArc]:
        session = db_manager.get_project_session()
        try:
            return session.query(PlotArc).filter_by(id=arc_id).first()
        finally:
            session.close()

    def update_arc(self, arc_id: int, **data) -> Optional[PlotArc]:
        session = db_manager.get_project_session()
        try:
            arc = session.query(PlotArc).filter_by(id=arc_id).first()
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
        session = db_manager.get_project_session()
        try:
            arc = session.query(PlotArc).filter_by(id=arc_id).first()
            if not arc:
                return False
            session.delete(arc)
            session.commit()
            return True
        finally:
            session.close()

    def list_arcs(self, project_id: int) -> list[PlotArc]:
        session = db_manager.get_project_session()
        try:
            return session.query(PlotArc)\
                .order_by(PlotArc.sort_order).all()
        finally:
            session.close()

    # ===== 节点 CRUD =====

    def create_node(self, project_id: int, title: str,
                    arc_id: Optional[int] = None, **data) -> PlotNode:
        session = db_manager.get_project_session()
        try:
            node = PlotNode(name=title,
                            parent_id=arc_id, **data)
            session.add(node)
            session.commit()
            session.refresh(node)
            return node
        finally:
            session.close()

    def get_node(self, node_id: int) -> Optional[PlotNode]:
        session = db_manager.get_project_session()
        try:
            return session.query(PlotNode).filter_by(id=node_id).first()
        finally:
            session.close()

    def update_node(self, node_id: int, **data) -> Optional[PlotNode]:
        session = db_manager.get_project_session()
        try:
            node = session.query(PlotNode).filter_by(id=node_id).first()
            if not node:
                return None
            # 兼容旧字段名
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

    def delete_node(self, node_id: int) -> bool:
        session = db_manager.get_project_session()
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
        session = db_manager.get_project_session()
        try:
            query = session.query(PlotNode)
            if arc_id is not None:
                query = query.filter(PlotNode.parent_id == arc_id)
            if status:
                query = query.filter(PlotNode.status == status)
            return query.order_by(PlotNode.sort_order).all()
        finally:
            session.close()

    def get_nodes_by_arc(self, arc_id: int) -> list[PlotNode]:
        return self.list_nodes(project_id=0, arc_id=arc_id)
        # Arc ID 本身是唯一的，不需要 project_id 筛选

    def get_nodes_by_status(self, project_id: int, status: str) -> list[PlotNode]:
        return self.list_nodes(project_id=project_id, status=status)

    # ===== 伏笔 CRUD =====

    def create_foreshadow(self, project_id: int, node_id: int,
                          description: str = "",
                          target_node_id: Optional[int] = None) -> PlotForeshadow:
        session = db_manager.get_project_session()
        try:
            fs = PlotForeshadow(
                node_id=node_id,
                description=description, target_node_id=target_node_id,
            )
            session.add(fs)
            session.commit()
            session.refresh(fs)
            return fs
        finally:
            session.close()

    def get_foreshadow(self, foreshadow_id: int) -> Optional[PlotForeshadow]:
        session = db_manager.get_project_session()
        try:
            return session.query(PlotForeshadow).filter_by(id=foreshadow_id).first()
        finally:
            session.close()

    def update_foreshadow(self, foreshadow_id: int, **data) -> Optional[PlotForeshadow]:
        session = db_manager.get_project_session()
        try:
            fs = session.query(PlotForeshadow).filter_by(id=foreshadow_id).first()
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

    def delete_foreshadow(self, foreshadow_id: int) -> bool:
        session = db_manager.get_project_session()
        try:
            fs = session.query(PlotForeshadow).filter_by(id=foreshadow_id).first()
            if not fs:
                return False
            session.delete(fs)
            session.commit()
            return True
        finally:
            session.close()

    def list_foreshadows(self, node_id: int) -> list[PlotForeshadow]:
        session = db_manager.get_project_session()
        try:
            return session.query(PlotForeshadow).filter_by(node_id=node_id)\
                .all()
        finally:
            session.close()


plot_service = PlotService()

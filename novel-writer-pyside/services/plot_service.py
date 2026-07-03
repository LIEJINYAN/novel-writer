"""情节服务 - 弧线、节点、伏笔管理（委托至 PlotTracker）。"""
from __future__ import annotations
from typing import Optional
from models import PlotArc, PlotNode, PlotForeshadow
from models.database import db_manager
from core.tracking.plot_tracker import PlotTracker


class PlotService:

    def __init__(self, node_repo: Optional["PlotNodeRepository"] = None):
        """可选的仓储依赖注入。

        Args:
            node_repo: 情节节点仓储实例（不传时使用 db_manager 直连）
        """
        self._node_repo = node_repo
        self._tracker = PlotTracker(db_manager)

    # ===== 弧线 CRUD =====

    def create_arc(self, project_id: int, name: str,
                   description: str = "", sort_order: int = 0) -> PlotArc:
        return self._tracker.create_arc(project_id, name, description, sort_order)

    def get_arc(self, arc_id: int) -> Optional[PlotArc]:
        return self._tracker.get_arc(arc_id)

    def update_arc(self, arc_id: int, **data) -> Optional[PlotArc]:
        return self._tracker.update_arc(arc_id, **data)

    def delete_arc(self, arc_id: int) -> bool:
        return self._tracker.delete_arc(arc_id)

    def list_arcs(self, project_id: int) -> list[PlotArc]:
        return self._tracker.list_arcs(project_id)

    # ===== 节点 CRUD =====

    def create_node(self, project_id: int, **data) -> PlotNode:
        return self._tracker.add_plot_node(project_id, **data)

    def get_node(self, node_id: int) -> Optional[PlotNode]:
        return self._tracker.get_node(node_id)

    def update_node(self, node_id: int, **data) -> Optional[PlotNode]:
        return self._tracker.update_node(node_id, **data)

    def delete_node(self, node_id: int) -> bool:
        return self._tracker.delete_node(node_id)

    def list_nodes(self, project_id: int, arc_id: Optional[int] = None,
                   status: Optional[str] = None) -> list[PlotNode]:
        return self._tracker.list_nodes(project_id, arc_id, status)

    def get_nodes_by_arc(self, arc_id: int) -> list[PlotNode]:
        return self._tracker.list_nodes(project_id=0, arc_id=arc_id)

    def get_nodes_by_status(self, project_id: int, status: str) -> list[PlotNode]:
        return self._tracker.list_nodes(project_id=project_id, status=status)

    # ===== 伏笔 CRUD =====

    def create_foreshadow(self, project_id: int, node_id: int,
                          description: str = "",
                          target_node_id: Optional[int] = None) -> PlotForeshadow:
        # 映射业务字段名到数据模型字段名：description -> content, node_id -> planted_chapter_id, target_node_id -> reveal_chapter_id
        data = dict(content=description,
                    planted_chapter_id=node_id,
                    reveal_chapter_id=target_node_id)
        return self._tracker.add_foreshadowing(project_id, **data)

    def get_foreshadow(self, foreshadow_id: int) -> Optional[PlotForeshadow]:
        return self._tracker.get_foreshadowing(foreshadow_id)

    def update_foreshadow(self, foreshadow_id: int, **data) -> Optional[PlotForeshadow]:
        # 映射业务字段名到数据模型字段名
        mapped_data = {}
        field_mapping = {
            "description": "content",
            "node_id": "planted_chapter_id",
            "target_node_id": "reveal_chapter_id",
        }
        for key, value in data.items():
            mapped_key = field_mapping.get(key, key)
            mapped_data[mapped_key] = value
        return self._tracker.update_foreshadowing(foreshadow_id, **mapped_data)

    def delete_foreshadow(self, foreshadow_id: int) -> bool:
        return self._tracker.delete_foreshadowing(foreshadow_id)

    def list_foreshadows(self, node_id: int) -> list[PlotForeshadow]:
        return self._tracker.list_foreshadowings(node_id)


plot_service = PlotService()

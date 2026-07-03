"""情节仓储 - 情节数据访问层。"""
from __future__ import annotations
from typing import List, Optional

from models import PlotArc, PlotNode, PlotForeshadow
from .base import BaseRepository


class PlotArcRepository(BaseRepository):
    """情节弧线仓储 - 封装情节弧线数据访问。"""

    def __init__(self):
        super().__init__(PlotArc)

    def list_by_project(self, project_id: int) -> List[PlotArc]:
        """获取项目所有情节弧线。"""
        session = self._get_session()
        try:
            return session.query(PlotArc)\
                .filter_by(project_id=project_id)\
                .order_by(PlotArc.sort_order.asc())\
                .all()
        finally:
            session.close()

    def _get_session(self):
        from models.database import db_manager
        return db_manager.get_session()


class PlotNodeRepository(BaseRepository):
    """情节节点仓储 - 封装情节节点数据访问。"""

    def __init__(self):
        super().__init__(PlotNode)

    def list_by_project(self, project_id: int) -> List[PlotNode]:
        """获取项目所有情节节点。"""
        session = self._get_session()
        try:
            return session.query(PlotNode)\
                .filter_by(project_id=project_id)\
                .order_by(PlotNode.sort_order.asc())\
                .all()
        finally:
            session.close()

    def list_by_arc(self, arc_id: int) -> List[PlotNode]:
        """获取弧线的所有节点。"""
        session = self._get_session()
        try:
            return session.query(PlotNode)\
                .filter_by(arc_id=arc_id)\
                .order_by(PlotNode.sort_order.asc())\
                .all()
        finally:
            session.close()

    def _get_session(self):
        from models.database import db_manager
        return db_manager.get_session()


class PlotForeshadowRepository(BaseRepository):
    """伏笔仓储 - 封装伏笔数据访问。"""

    def __init__(self):
        super().__init__(PlotForeshadow)

    def list_by_node(self, node_id: int) -> List[PlotForeshadow]:
        """获取节点的所有伏笔。"""
        session = self._get_session()
        try:
            return session.query(PlotForeshadow)\
                .filter_by(node_id=node_id)\
                .all()
        finally:
            session.close()

    def _get_session(self):
        from models.database import db_manager
        return db_manager.get_session()

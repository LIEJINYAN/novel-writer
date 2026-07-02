"""AI Provider 仓储 - AI提供商数据访问层。"""
from __future__ import annotations
from typing import List, Optional

from models.ai_provider import AIProvider
from .base import BaseRepository


class AIProviderRepository(BaseRepository):
    """AI Provider 仓储 - 封装 AI 提供商数据访问。"""

    def __init__(self):
        super().__init__(AIProvider)

    def list_enabled(self) -> List[AIProvider]:
        """获取所有启用的 AI 提供商。"""
        session = self._get_session()
        try:
            return session.query(AIProvider)\
                .filter_by(is_enabled=True)\
                .order_by(AIProvider.sort_order.asc())\
                .all()
        finally:
            session.close()

    def get_by_name(self, name: str) -> Optional[AIProvider]:
        """根据名称获取 AI 提供商。"""
        session = self._get_session()
        try:
            return session.query(AIProvider).filter_by(name=name).first()
        finally:
            session.close()

    def _get_session(self):
        from models.database import db_manager
        return db_manager.get_session()

"""时间线服务 - 事件 CRUD（委托至 TimelineManager）。"""
from __future__ import annotations
from typing import Optional
from models import TimelineEvent
from models.database import db_manager
from core.tracking.timeline_manager import TimelineManager


class TimelineService:

    def __init__(self):
        self._manager = TimelineManager(db_manager)

    def create(self, project_id: int, event_name: str, **data) -> TimelineEvent:
        """创建时间线事件。"""
        return self._manager.add_event(project_id, event_name, **data)

    def get(self, event_id: int) -> Optional[TimelineEvent]:
        """获取事件（含章节信息）。"""
        return self._manager.get_event(event_id)

    def update(self, event_id: int, **data) -> Optional[TimelineEvent]:
        """更新事件。"""
        return self._manager.update_event(event_id, **data)

    def delete(self, event_id: int) -> bool:
        """删除事件。"""
        return self._manager.delete_event(event_id)

    def batch_delete(self, event_ids: list[int]) -> int:
        """批量删除事件，返回删除数。"""
        return self._manager.batch_delete_events(event_ids)

    def list(self, project_id: int, search: str = "") -> list[dict]:
        """列出事件，按 sort_order 排序。"""
        return self._manager.list_events(project_id, search)


timeline_service = TimelineService()

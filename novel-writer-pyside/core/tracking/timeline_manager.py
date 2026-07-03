"""时间线管理器 - 管理时间线事件和排序验证。

提供核心数据库逻辑，供 services/timeline_service.py 委托调用。
"""

from __future__ import annotations
from typing import Optional
from models import TimelineEvent
from models.database import DatabaseManager


class TimelineManager:
    """时间线管理器 - 管理事件、区间查询和验证。"""

    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager

    # ===== 事件 CRUD =====

    def add_event(self, project_id: int, event_name: str, **data) -> TimelineEvent:
        """添加时间线事件。"""
        session = self._db.get_project_session()
        try:
            ev = TimelineEvent(event_name=event_name, **data)
            session.add(ev)
            session.commit()
            session.refresh(ev)
            return ev
        finally:
            session.close()

    def get_event(self, event_id: int) -> Optional[TimelineEvent]:
        """获取事件（含章节信息）。"""
        session = self._db.get_project_session()
        try:
            return session.query(TimelineEvent).filter(
                TimelineEvent.id == event_id
            ).first()
        finally:
            session.close()

    def update_event(self, event_id: int, **data) -> Optional[TimelineEvent]:
        """更新事件。"""
        session = self._db.get_project_session()
        try:
            ev = session.query(TimelineEvent).filter_by(id=event_id).first()
            if not ev:
                return None
            for key, value in data.items():
                if hasattr(ev, key):
                    setattr(ev, key, value)
            session.commit()
            session.refresh(ev)
            return ev
        finally:
            session.close()

    def delete_event(self, event_id: int) -> bool:
        """删除事件。"""
        session = self._db.get_project_session()
        try:
            ev = session.query(TimelineEvent).filter_by(id=event_id).first()
            if not ev:
                return False
            session.delete(ev)
            session.commit()
            return True
        finally:
            session.close()

    def batch_delete_events(self, event_ids: list[int]) -> int:
        """批量删除事件，返回删除数。"""
        session = self._db.get_project_session()
        try:
            count = session.query(TimelineEvent).filter(
                TimelineEvent.id.in_(event_ids)
            ).delete(synchronize_session=False)
            session.commit()
            return count
        finally:
            session.close()

    def list_events(self, project_id: int, search: str = "") -> list[dict]:
        """列出事件，按 sort_order 排序。"""
        session = self._db.get_project_session()
        try:
            query = session.query(TimelineEvent)

            if search:
                like = f"%{search}%"
                query = query.filter(TimelineEvent.event_name.like(like))

            results = query.order_by(TimelineEvent.sort_order).all()
            return [
                {
                    "id": e.id,
                    "event_name": e.event_name,
                    "description": e.description,
                    "story_date": e.story_date,
                    "chapter_id": e.chapter_id,
                    "chapter_title": e.chapter.title if e.chapter else "",
                    "location": e.location,
                    "importance": e.importance,
                    "sort_order": e.sort_order,
                }
                for e in results
            ]
        finally:
            session.close()

    # ===== 区间查询 =====

    def get_events_between(self, project_id: int, start_date: str,
                           end_date: str) -> list[TimelineEvent]:
        """获取日期区间内的事件。"""
        session = self._db.get_project_session()
        try:
            return session.query(TimelineEvent).filter(
                TimelineEvent.story_date >= start_date,
                TimelineEvent.story_date <= end_date,
            ).order_by(TimelineEvent.sort_order).all()
        finally:
            session.close()

    # ===== 时间线验证 =====

    def validate_timeline(self, project_id: int) -> list[dict]:
        """验证时间线一致性，返回异常事件列表。

        检测 sort_order 与 story_date 数值序的矛盾。
        """
        session = self._db.get_project_session()
        try:
            events = session.query(TimelineEvent).order_by(
                TimelineEvent.sort_order
            ).all()

            issues = []
            for i in range(1, len(events)):
                prev = events[i - 1]
                curr = events[i]

                prev_num = self._extract_number(prev.story_date)
                curr_num = self._extract_number(curr.story_date)

                if prev_num is not None and curr_num is not None:
                    if curr_num < prev_num:
                        issues.append({
                            "event_id": curr.id,
                            "event_name": curr.event_name,
                            "message": f"日期序号({curr_num})小于前一个事件「{prev.event_name}」({prev_num})",
                            "severity": "warning",
                        })
            return issues
        finally:
            session.close()

    @staticmethod
    def _extract_number(text: str) -> Optional[int]:
        """从文本中提取数字序号。"""
        import re
        if not text:
            return None
        match = re.search(r"(\d+)", text)
        if match:
            return int(match.group(1))
        return None

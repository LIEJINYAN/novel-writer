"""时间线服务 - 事件 CRUD。"""
from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import joinedload
from models import TimelineEvent
from models.database import db_manager


class TimelineService:

    def create(self, project_id: int, event_name: str, **data) -> TimelineEvent:
        """创建时间线事件。"""
        session = db_manager.get_project_session()
        try:
            ev = TimelineEvent(event_name=event_name, **data)
            session.add(ev)
            session.commit()
            session.refresh(ev)
            return ev
        finally:
            session.close()

    def get(self, event_id: int) -> Optional[TimelineEvent]:
        """获取事件（含章节信息）。"""
        session = db_manager.get_project_session()
        try:
            return session.query(TimelineEvent).filter(TimelineEvent.id == event_id).first()
        finally:
            session.close()

    def update(self, event_id: int, **data) -> Optional[TimelineEvent]:
        """更新事件。"""
        session = db_manager.get_project_session()
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

    def delete(self, event_id: int) -> bool:
        """删除事件。"""
        session = db_manager.get_project_session()
        try:
            ev = session.query(TimelineEvent).filter_by(id=event_id).first()
            if not ev:
                return False
            session.delete(ev)
            session.commit()
            return True
        finally:
            session.close()

    def batch_delete(self, event_ids: list[int]) -> int:
        """批量删除事件，返回删除数。"""
        session = db_manager.get_project_session()
        try:
            count = session.query(TimelineEvent).filter(
                TimelineEvent.id.in_(event_ids)
            ).delete(synchronize_session=False)
            session.commit()
            return count
        finally:
            session.close()

    def list(self, project_id: int, search: str = "") -> list[dict]:
        """列出事件，按 sort_order 排序。"""
        session = db_manager.get_project_session()
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


timeline_service = TimelineService()

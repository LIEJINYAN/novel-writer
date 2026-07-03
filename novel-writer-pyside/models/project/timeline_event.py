"""时间线事件数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from models.database import ProjectBase


class TimelineEvent(ProjectBase):
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_name = Column(String(200), nullable=False)
    description = Column(Text)
    story_date = Column(String(200))
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))
    location = Column(String(200))
    duration = Column(String(100))
    participants = Column(Text)
    related_plot_node_id = Column(Integer, ForeignKey("plot_nodes.id", ondelete="SET NULL"))
    importance = Column(String(20), default="medium")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    __table_args__ = (
        Index("idx_timeline_events_chapter_id", "chapter_id"),
        Index("idx_timeline_events_sort_order", "sort_order"),
    )

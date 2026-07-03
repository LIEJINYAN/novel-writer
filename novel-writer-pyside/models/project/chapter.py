"""章节数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship as rel, backref
from models.database import ProjectBase


class Chapter(ProjectBase):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    volume_id = Column(Integer, ForeignKey("volumes.id", ondelete="CASCADE"), nullable=True)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    subtitle = Column(String(200))
    content = Column(Text)
    content_plain = Column(Text)
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    paragraph_count = Column(Integer, default=0)
    summary = Column(Text)
    status = Column(String(20), default="draft")
    plot_stage = Column(String(50))
    sort_order = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    volume = rel("Volume", backref=backref("chapters", passive_deletes=True))

    __table_args__ = (
        Index("idx_chapters_volume_id", "volume_id"),
        Index("idx_chapters_sort_order", "sort_order"),
        Index("idx_chapters_status", "status"),
        Index("idx_chapters_is_deleted", "is_deleted"),
    )

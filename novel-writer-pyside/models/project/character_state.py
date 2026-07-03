"""角色状态数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from models.database import ProjectBase


class CharacterState(ProjectBase):
    __tablename__ = "character_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))
    is_alive = Column(Integer, default=1)
    health_status = Column(String(50), default="良好")
    mental_state = Column(String(50), default="正常")
    location = Column(String(200))
    position = Column(String(100))
    current_phase = Column(String(50), default="起点")
    next_goal = Column(Text)
    status_snapshot = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

"""势力成员数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from models.database import ProjectBase


class FactionMember(ProjectBase):
    __tablename__ = "faction_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    faction_id = Column(Integer, ForeignKey("factions.id", ondelete="CASCADE"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    role_in_faction = Column(String(100))
    join_reason = Column(Text)
    joined_chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))
    is_core_member = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("faction_id", "character_id"),
    )

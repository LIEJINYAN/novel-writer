"""情节节点数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship as rel, backref
from models.database import ProjectBase


class PlotNode(ProjectBase):
    __tablename__ = "plot_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("plot_nodes.id", ondelete="SET NULL"))
    plot_type = Column(String(20), default="main")
    name = Column(String(200), nullable=False)
    description = Column(Text)
    stage_key = Column(String(100))
    status = Column(String(20), default="pending")
    start_chapter = Column(Integer)
    end_chapter = Column(Integer)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    parent = rel("PlotNode", remote_side=[id], backref=backref("children", passive_deletes=True))

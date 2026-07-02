"""情节数据模型。"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base


class PlotArc(Base):
    __tablename__ = "plot_arcs"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", backref="plot_arcs")
    nodes = relationship("PlotNode", back_populates="arc",
                         cascade="all, delete-orphan", order_by="PlotNode.sort_order")


class PlotNode(Base):
    __tablename__ = "plot_nodes"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    arc_id = Column(Integer, ForeignKey("plot_arcs.id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    status = Column(String(50), default="计划中")  # 计划中/进行中/已完成/已放弃
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    importance = Column(String(50), default="重要")  # 核心/重要/次要
    sort_order = Column(Integer, default=0)
    notes = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", backref="plot_nodes")
    arc = relationship("PlotArc", back_populates="nodes")
    chapter = relationship("Chapter")
    foreshadows = relationship("PlotForeshadow",
                               foreign_keys="PlotForeshadow.node_id",
                               back_populates="node",
                               cascade="all, delete-orphan")


class PlotForeshadow(Base):
    __tablename__ = "plot_foreshadows"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("plot_nodes.id"), nullable=False)
    description = Column(Text, default="")
    target_node_id = Column(Integer, ForeignKey("plot_nodes.id"), nullable=True)
    status = Column(String(50), default="已埋设")  # 已埋设/已揭示/已废弃

    project = relationship("Project", backref="plot_foreshadows")
    node = relationship("PlotNode", foreign_keys=[node_id], back_populates="foreshadows")
    target_node = relationship("PlotNode", foreign_keys=[target_node_id])

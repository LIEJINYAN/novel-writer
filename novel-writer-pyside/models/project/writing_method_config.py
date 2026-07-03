"""写作方法配置数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from models.database import ProjectBase


class WritingMethodConfig(ProjectBase):
    __tablename__ = "writing_method_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    method_name = Column(String(50), nullable=False)
    stage_config = Column(Text)
    scene_templates = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

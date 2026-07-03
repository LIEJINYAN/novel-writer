"""校验规则数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from models.database import ProjectBase


class ValidationRule(ProjectBase):
    __tablename__ = "validation_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), default="character")
    is_enabled = Column(Boolean, default=True)
    checks = Column(Text)
    config = Column(Text)
    severity = Column(String(20), default="warning")
    auto_fix_enabled = Column(Boolean, default=False)
    confidence_threshold = Column(Float, default=0.9)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

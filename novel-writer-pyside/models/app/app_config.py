from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from models.database import AppBase


class AppConfig(AppBase):
    __tablename__ = "app_config"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

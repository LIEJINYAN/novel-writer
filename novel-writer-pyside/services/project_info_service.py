"""项目信息服务 - 读写 project_info 表（项目级 DB）。"""
from __future__ import annotations
from typing import Optional
from models import ProjectInfo
from models.database import db_manager


class ProjectInfoService:

    def get(self) -> Optional[ProjectInfo]:
        """获取当前项目的信息。"""
        session = db_manager.get_project_session()
        try:
            return session.query(ProjectInfo).first()
        finally:
            session.close()

    def update(self, **data) -> Optional[ProjectInfo]:
        """更新项目信息。"""
        session = db_manager.get_project_session()
        try:
            info = session.query(ProjectInfo).first()
            if not info:
                return None
            for key, value in data.items():
                if hasattr(info, key):
                    setattr(info, key, value)
            session.commit()
            session.refresh(info)
            return info
        finally:
            session.close()

    def create(self, name: str, **data) -> ProjectInfo:
        """创建项目信息（首次初始化时调用）。"""
        session = db_manager.get_project_session()
        try:
            info = ProjectInfo(name=name, **data)
            session.add(info)
            session.commit()
            session.refresh(info)
            return info
        finally:
            session.close()


project_info_service = ProjectInfoService()

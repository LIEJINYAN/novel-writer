"""项目管理服务。"""
import os
from pathlib import Path
from datetime import datetime
from models import db_manager, Project, Volume, Chapter
from utils.signal_bus import signal_bus
from utils.logger import logger


class ProjectService:
    """项目服务 - 管理项目的 CRUD 操作。"""

    def __init__(self):
        self._current_project = None

    @property
    def current_project(self) -> Project:
        return self._current_project

    def create_project(self, info: dict) -> Project:
        """创建新项目。"""
        session = db_manager.get_session()
        try:
            project = Project(
                name=info["name"],
                genre=info.get("genre", ""),
                writing_method=info.get("writing_method", "three-act"),
                target_words=info.get("target_words", 0),
                description=info.get("description", ""),
            )

            # 设置项目路径
            projects_dir = Path(db_manager.data_dir) / "projects" / info["name"]
            projects_dir.mkdir(parents=True, exist_ok=True)
            project.path = str(projects_dir)
            project.status = "active"

            session.add(project)
            session.flush()

            # 创建默认分卷
            volume = Volume(
                project_id=project.id,
                name="第一卷",
                sort_order=1,
                description="默认分卷",
            )
            session.add(volume)
            session.commit()

            self._current_project = project
            logger.success(f"项目创建成功: {project.name}")
            return project

        except Exception as e:
            session.rollback()
            logger.error(f"创建项目失败: {e}")
            raise
        finally:
            session.close()

    def open_project(self, project_id: int) -> Project:
        """打开项目。"""
        session = db_manager.get_session()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if project:
                self._current_project = project
                signal_bus.project_opened.emit(project.id)
                logger.info(f"打开项目: {project.name}")
            return project
        finally:
            session.close()

    def list_projects(self) -> list:
        """获取项目列表。"""
        session = db_manager.get_session()
        try:
            return session.query(Project)\
                .filter_by(status="active")\
                .order_by(Project.updated_at.desc())\
                .all()
        finally:
            session.close()

    def delete_project(self, project_id: int) -> bool:
        """删除项目。"""
        session = db_manager.get_session()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if project:
                project.status = "archived"
                session.commit()
                logger.info(f"项目已归档: {project.name}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"删除项目失败: {e}")
            raise
        finally:
            session.close()

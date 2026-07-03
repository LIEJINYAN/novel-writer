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
                title="第一卷",
                volume_number=1,
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

    # ========== 回收站操作 ==========

    def list_archived_projects(self) -> list[Project]:
        """列出所有已归档的项目。"""
        session = db_manager.get_session()
        try:
            return session.query(Project)\
                .filter_by(status="archived")\
                .order_by(Project.updated_at.desc())\
                .all()
        finally:
            session.close()

    def restore_project(self, project_id: int) -> bool:
        """恢复已归档的项目。"""
        session = db_manager.get_session()
        try:
            project = session.query(Project).filter_by(id=project_id, status="archived").first()
            if project:
                project.status = "active"
                session.commit()
                logger.info(f"项目已恢复: {project.name}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"恢复项目失败: {e}")
            raise
        finally:
            session.close()

    def hard_delete_project(self, project_id: int) -> bool:
        """彻底删除项目（从数据库移除 + 删除磁盘目录）。

        依赖数据库的 ``ON DELETE CASCADE`` 自动级联删除所有关联数据。
        新增关联 ``projects.id`` 的表时，只需在 FK 上声明
        ``ondelete="CASCADE"``，不需要改此处代码。
        """
        session = db_manager.get_session()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return False

            # 删除磁盘目录
            if project.path and Path(project.path).exists():
                import shutil
                shutil.rmtree(project.path, ignore_errors=True)

            project_name = project.name

            # ORM 自动级联删除所有关联数据（volumes/chapters/characters/plots/…）
            session.delete(project)
            session.commit()
            logger.info(f"项目已永久删除: {project_name}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"永久删除项目失败: {e}")
            raise
        finally:
            session.close()

    def hard_delete_all_projects(self) -> int:
        """永久删除所有已归档的项目。返回删除数量。"""
        session = db_manager.get_session()
        try:
            projects = session.query(Project).filter_by(status="archived").all()
            count = len(projects)
            session.close()
            for project in projects:
                self.hard_delete_project(project.id)
            logger.info(f"清空回收站: 删除 {count} 个项目")
            return count
        except Exception as e:
            logger.error(f"清空回收站失败: {e}")
            raise

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

"""项目管理器 - 核心业务逻辑。"""
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from models import db_manager, Project, Volume, Chapter
from utils.logger import logger


class ProjectManager:
    """项目管理器 - 处理项目相关的核心业务逻辑。"""

    # ========== 项目统计 & 归档（已有） ==========

    def get_project_stats(self, project_id: int) -> dict:
        """获取项目统计信息。"""
        session = db_manager.get_session()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return {}

            total_chapters = session.query(Chapter)\
                .filter_by(project_id=project_id, is_deleted=False)\
                .count()
            total_words = session.query(Chapter.content)\
                .filter_by(project_id=project_id, is_deleted=False)\
                .all()

            word_count = sum(len(c.content) for c in total_words) if total_words else 0

            volumes = session.query(Volume)\
                .filter_by(project_id=project_id)\
                .order_by(Volume.sort_order)\
                .all()

            return {
                "project": project,
                "total_chapters": total_chapters,
                "total_words": word_count,
                "volumes_count": len(volumes),
                "progress": round(word_count / project.target_words * 100, 1)
                    if project.target_words > 0 else 0,
            }
        finally:
            session.close()

    def archive_project(self, project_id: int) -> bool:
        """归档项目。"""
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
            logger.error(f"归档失败: {e}")
            raise
        finally:
            session.close()

    # ========== 项目 CRUD ==========

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

            logger.success(f"项目创建成功: {project.name}")
            return project

        except Exception as e:
            session.rollback()
            logger.error(f"创建项目失败: {e}")
            raise
        finally:
            session.close()

    def open_project(self, project_id: int) -> Optional[Project]:
        """打开项目（更新 last_opened_at）。"""
        session = db_manager.get_session()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if project:
                project.last_opened_at = datetime.now()
                session.commit()
                logger.info(f"打开项目: {project.name}")
            return project
        finally:
            session.close()

    def delete_project(self, project_id: int) -> bool:
        """删除/归档项目。"""
        return self.archive_project(project_id)

    def get_project(self, project_id: int) -> Optional[Project]:
        """获取项目对象。"""
        session = db_manager.get_session()
        try:
            return session.query(Project).filter_by(id=project_id).first()
        finally:
            session.close()

    def get_project_by_path(self, path: str) -> Optional[Project]:
        """通过路径查找项目。"""
        session = db_manager.get_session()
        try:
            return session.query(Project).filter_by(path=path).first()
        finally:
            session.close()

    def list_projects(self) -> List[Project]:
        """获取所有活跃项目列表。"""
        session = db_manager.get_session()
        try:
            return session.query(Project)\
                .filter_by(status="active")\
                .order_by(Project.updated_at.desc())\
                .all()
        finally:
            session.close()

    def list_archived_projects(self) -> List[Project]:
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

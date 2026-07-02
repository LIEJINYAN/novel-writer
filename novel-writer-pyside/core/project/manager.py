"""项目管理器 - 核心业务逻辑。"""
from pathlib import Path
from typing import Optional, List
from models import db_manager, Project, Volume, Chapter
from utils.logger import logger


class ProjectManager:
    """项目管理器 - 处理项目相关的核心业务逻辑。"""

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

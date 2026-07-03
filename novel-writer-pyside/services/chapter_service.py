"""章节管理服务 - 薄包装层，委托给 WritingEngine。"""
from __future__ import annotations
from typing import Optional
from datetime import datetime
from models import db_manager, Volume, Chapter
from utils.signal_bus import signal_bus
from utils.logger import logger
from core.writing import WritingEngine


class ChapterService:
    """章节服务 - 管理分卷和章节的 CRUD 操作。"""

    def __init__(self, repo: Optional["ChapterRepository"] = None,
                 volume_repo: Optional["VolumeRepository"] = None,
                 engine: Optional[WritingEngine] = None):
        """可选的仓储或引擎依赖注入。

        Args:
            repo: 章节仓储实例（保留向后兼容，不再使用）
            volume_repo: 分卷仓储实例（保留向后兼容，不再使用）
            engine: 写作引擎实例（不传时创建默认实例）
        """
        self._repo = repo
        self._volume_repo = volume_repo
        self._engine = engine or WritingEngine()

    # ========== 分卷操作（委托） ==========

    def create_volume(self, project_id: int, name: str, description: str = "") -> Volume:
        return self._engine.create_volume(project_id, name, description)

    def get_volume(self, volume_id: int) -> Volume | None:
        return self._engine.get_volume(volume_id)

    def rename_volume(self, volume_id: int, new_name: str) -> bool:
        return self._engine.rename_volume(volume_id, new_name)

    def delete_volume(self, volume_id: int) -> bool:
        return self._engine.delete_volume(volume_id)

    def list_volumes(self, project_id: int = None) -> list[Volume]:
        return self._engine.list_volumes(project_id)

    def reorder_volume(self, volume_id: int, target_position: int) -> bool:
        return self._engine.reorder_volume(volume_id, target_position)

    # ========== 章节操作（委托） ==========

    def create_chapter(self, volume_id: int, title: str, content: str = "") -> Chapter:
        return self._engine.create_chapter(volume_id, title, content)

    def get_chapter(self, chapter_id: int) -> Chapter | None:
        return self._engine.get_chapter(chapter_id)

    def rename_chapter(self, chapter_id: int, new_title: str) -> bool:
        return self._engine.rename_chapter(chapter_id, new_title)

    def delete_chapter(self, chapter_id: int) -> bool:
        return self._engine.delete_chapter(chapter_id)

    def list_chapters(self, project_id: int) -> list:
        return self._engine.list_chapters(project_id)

    def update_chapter_content(self, chapter_id: int, content: str) -> bool:
        return self._engine.update_chapter_content(chapter_id, content)

    def reorder_chapter(self, chapter_id: int, target_volume_id: int, target_position: int) -> bool:
        return self._engine.reorder_chapter(chapter_id, target_volume_id, target_position)

    # ========== 回收站操作 ==========

    def list_deleted_chapters(self, project_id: int = None) -> list[Chapter]:
        """列出所有软删除的章节。可指定项目 ID 过滤。

        注：不包含已删除分卷下的章节（它们随分卷一起操作）。
        """
        session = db_manager.get_project_session()
        try:
            q = session.query(Chapter).filter(Chapter.is_deleted == True)
            # 排除已删除分卷下的章节
            q = q.outerjoin(Volume, Chapter.volume_id == Volume.id)\
                 .filter((Volume.is_deleted == False) | (Volume.is_deleted == None))
            return q.order_by(Chapter.deleted_at.desc()).all()
        finally:
            session.close()

    def restore_chapter(self, chapter_id: int) -> bool:
        """恢复软删除的章节。"""
        session = db_manager.get_project_session()
        try:
            chapter = session.query(Chapter).filter_by(id=chapter_id, is_deleted=True).first()
            if chapter:
                chapter.is_deleted = False
                session.commit()
                signal_bus.chapter_created.emit(chapter.id)
                logger.info(f"章节已恢复: {chapter.title}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"恢复章节失败: {e}")
            raise
        finally:
            session.close()

    def hard_delete_chapter(self, chapter_id: int) -> bool:
        """彻底删除章节（从数据库移除）。"""
        session = db_manager.get_project_session()
        try:
            chapter = session.query(Chapter).filter_by(id=chapter_id).first()
            if chapter:
                session.delete(chapter)
                session.commit()
                logger.info(f"章节已永久删除: {chapter.title}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"永久删除章节失败: {e}")
            raise
        finally:
            session.close()

    def hard_delete_all_chapters(self, project_id: int = None) -> int:
        """永久删除所有软删除的章节。返回删除数量。"""
        session = db_manager.get_project_session()
        try:
            q = session.query(Chapter).filter(Chapter.is_deleted == True)
            count = q.count()
            q.delete(synchronize_session=False)
            session.commit()
            logger.info(f"清空回收站: 删除 {count} 个章节")
            return count
        except Exception as e:
            session.rollback()
            logger.error(f"清空回收站失败: {e}")
            raise
        finally:
            session.close()

    def list_deleted_volumes(self, project_id: int = None) -> list[Volume]:
        """列出所有软删除的分卷。"""
        session = db_manager.get_project_session()
        try:
            # Volume 无 is_deleted 字段，返回空列表
            return []
        finally:
            session.close()

    def restore_volume(self, volume_id: int) -> int:
        """恢复软删除的分卷及其下所有章节。返回恢复的章节数。"""
        session = db_manager.get_project_session()
        try:
            volume = session.query(Volume).filter_by(id=volume_id, is_deleted=True).first()
            if not volume:
                return 0

            volume.is_deleted = False
            volume.deleted_at = None

            chapters = session.query(Chapter)\
                .filter_by(volume_id=volume_id, is_deleted=True)\
                .all()
            for chapter in chapters:
                chapter.is_deleted = False
                chapter.deleted_at = None

            session.commit()
            logger.info(f"分卷已恢复: {volume.name}, 含 {len(chapters)} 个章节")
            return len(chapters)
        except Exception as e:
            session.rollback()
            logger.error(f"恢复分卷失败: {e}")
            raise
        finally:
            session.close()

    def hard_delete_volume(self, volume_id: int) -> bool:
        """彻底删除分卷及其下所有章节。"""
        session = db_manager.get_project_session()
        try:
            volume = session.query(Volume).filter_by(id=volume_id).first()
            if not volume:
                return False

            # CASCADE 会自动删除关联的章节
            session.delete(volume)
            session.commit()
            logger.info(f"分卷已永久删除: {volume.name}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"永久删除分卷失败: {e}")
            raise
        finally:
            session.close()

    def hard_delete_all_volumes(self, project_id: int = None) -> int:
        """永久删除所有软删除的分卷。返回删除数量。"""
        # Volume 无 is_deleted 字段，无法软删除，返回 0
        logger.info("清空回收站: Volume 无 is_deleted 字段，跳过")
        return 0

    # ========== 搜索 ==========

    def search_in_project(self, project_id: int, keyword: str) -> list:
        """在项目所有未删除章节的 title 和 content 中搜索关键词。"""
        if not keyword or not keyword.strip():
            return []

        session = db_manager.get_project_session()
        try:
            chapters = session.query(Chapter)\
                .filter_by(is_deleted=False)\
                .order_by(Chapter.chapter_number.asc())\
                .all()

            results = []
            keyword_lower = keyword.lower()

            for chapter in chapters:
                title = chapter.title or ""
                content = chapter.content or ""

                title_count = title.lower().count(keyword_lower)
                content_count = content.lower().count(keyword_lower)
                match_count = title_count + content_count

                if match_count == 0:
                    continue

                snippet = ""
                idx = content.lower().find(keyword_lower)
                if idx >= 0:
                    start = max(0, idx - 20)
                    end = min(len(content), idx + len(keyword) + 20)
                    snippet = content[start:end]
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(content):
                        snippet = snippet + "..."
                else:
                    snippet = title[:40]
                    if len(title) > 40:
                        snippet += "..."

                volume_name = chapter.volume.name if chapter.volume else ""

                results.append({
                    "chapter_id": chapter.id,
                    "chapter_title": chapter.title,
                    "chapter_number": chapter.chapter_number,
                    "volume_name": volume_name,
                    "match_count": match_count,
                    "snippet": snippet,
                })

            return results
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise
        finally:
            session.close()

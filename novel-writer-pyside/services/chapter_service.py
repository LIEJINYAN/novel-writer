"""章节管理服务。"""
from datetime import datetime
from models import db_manager, Volume, Chapter
from utils.signal_bus import signal_bus
from utils.logger import logger


class ChapterService:
    """章节服务 - 管理分卷和章节的 CRUD 操作。"""

    def __init__(self):
        pass

    def create_volume(self, project_id: int, name: str, description: str = "") -> Volume:
        """创建新分卷，sort_order 自动为当前项目最大+1。"""
        session = db_manager.get_project_session()
        try:
            max_sort = session.query(Volume)\
                .order_by(Volume.sort_order.desc())\
                .first()
            sort_order = (max_sort.sort_order + 1) if max_sort else 1

            volume = Volume(
                title=name,
                volume_number=sort_order,
                sort_order=sort_order,
                description=description,
            )
            session.add(volume)
            session.commit()
            logger.success(f"分卷创建成功: {volume.title}")
            return volume
        except Exception as e:
            session.rollback()
            logger.error(f"创建分卷失败: {e}")
            raise
        finally:
            session.close()

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
            q = session.query(Volume).filter(Volume.is_deleted == True)
            return q.order_by(Volume.deleted_at.desc()).all()
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
        session = db_manager.get_project_session()
        try:
            q = session.query(Volume).filter(Volume.is_deleted == True)
            count = q.count()
            q.delete(synchronize_session=False)
            session.commit()
            logger.info(f"清空回收站: 删除 {count} 个分卷")
            return count
        except Exception as e:
            session.rollback()
            logger.error(f"清空分卷回收站失败: {e}")
            raise
        finally:
            session.close()

    def get_volume(self, volume_id: int) -> Volume | None:
        """获取分卷。"""
        session = db_manager.get_project_session()
        try:
            return session.query(Volume).filter_by(id=volume_id).first()
        finally:
            session.close()

    def rename_volume(self, volume_id: int, new_name: str) -> bool:
        """重命名分卷。"""
        session = db_manager.get_project_session()
        try:
            volume = session.query(Volume).filter_by(id=volume_id).first()
            if volume:
                volume.name = new_name
                session.commit()
                logger.info(f"分卷重命名成功: {new_name}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"重命名分卷失败: {e}")
            raise
        finally:
            session.close()

    def delete_volume(self, volume_id: int) -> bool:
        """软删除分卷及其下所有章节。"""
        session = db_manager.get_project_session()
        try:
            volume = session.query(Volume).filter_by(id=volume_id).first()
            if not volume:
                return False

            now = datetime.now()
            volume.is_deleted = True
            volume.deleted_at = now

            chapters = session.query(Chapter)\
                .filter_by(volume_id=volume_id, is_deleted=False)\
                .all()
            for chapter in chapters:
                chapter.is_deleted = True
                chapter.deleted_at = now
                signal_bus.chapter_deleted.emit(chapter.id)

            session.commit()
            logger.info(f"分卷已软删除: {volume.name}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"删除分卷失败: {e}")
            raise
        finally:
            session.close()

    def create_chapter(self, volume_id: int, title: str, content: str = "") -> Chapter:
        """创建新章节，章节号自动为当前分卷最大章节号+1。"""
        session = db_manager.get_project_session()
        try:
            volume = session.query(Volume).filter_by(id=volume_id).first()
            if not volume:
                raise ValueError(f"分卷不存在: {volume_id}")

            max_chapter = session.query(Chapter)\
                .filter_by(volume_id=volume_id, is_deleted=False)\
                .order_by(Chapter.chapter_number.desc())\
                .first()
            chapter_number = (max_chapter.chapter_number + 1) if max_chapter else 1

            word_count = sum(1 for c in content if not c.isspace())

            chapter = Chapter(
                volume_id=volume_id,
                chapter_number=chapter_number,
                title=title,
                content=content,
                word_count=word_count,
            )
            session.add(chapter)
            session.commit()
            signal_bus.chapter_created.emit(chapter.id)
            logger.success(f"章节创建成功: {chapter.title}")
            return chapter
        except Exception as e:
            session.rollback()
            logger.error(f"创建章节失败: {e}")
            raise
        finally:
            session.close()

    def get_chapter(self, chapter_id: int) -> Chapter | None:
        """获取章节。"""
        session = db_manager.get_project_session()
        try:
            return session.query(Chapter).filter_by(id=chapter_id, is_deleted=False).first()
        finally:
            session.close()

    def list_chapters(self, project_id: int) -> list:
        """获取项目所有未删除章节列表。"""
        session = db_manager.get_project_session()
        try:
            return session.query(Chapter)\
                .filter_by(is_deleted=False)\
                .order_by(Chapter.chapter_number.asc())\
                .all()
        finally:
            session.close()

    def update_chapter_content(self, chapter_id: int, content: str) -> bool:
        """更新章节内容和字数。"""
        session = db_manager.get_project_session()
        try:
            chapter = session.query(Chapter)\
                .filter_by(id=chapter_id, is_deleted=False)\
                .first()
            if chapter:
                chapter.content = content
                chapter.word_count = sum(1 for c in content if not c.isspace())
                session.commit()
                signal_bus.chapter_saved.emit(chapter.id)
                signal_bus.content_changed.emit(chapter.id)
                logger.info(f"章节内容已更新: {chapter.title}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新章节内容失败: {e}")
            raise
        finally:
            session.close()

    def rename_chapter(self, chapter_id: int, new_title: str) -> bool:
        """重命名章节。"""
        session = db_manager.get_project_session()
        try:
            chapter = session.query(Chapter)\
                .filter_by(id=chapter_id, is_deleted=False)\
                .first()
            if chapter:
                chapter.title = new_title
                session.commit()
                signal_bus.chapter_saved.emit(chapter.id)
                logger.info(f"章节重命名成功: {new_title}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"重命名章节失败: {e}")
            raise
        finally:
            session.close()

    def delete_chapter(self, chapter_id: int) -> bool:
        """软删除章节（is_deleted=True）。"""
        session = db_manager.get_project_session()
        try:
            chapter = session.query(Chapter)\
                .filter_by(id=chapter_id, is_deleted=False)\
                .first()
            if chapter:
                chapter.is_deleted = True
                chapter.deleted_at = datetime.now()
                session.commit()
                signal_bus.chapter_deleted.emit(chapter.id)
                logger.info(f"章节已软删除: {chapter.title}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"删除章节失败: {e}")
            raise
        finally:
            session.close()

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

    def reorder_chapter(self, chapter_id: int, target_volume_id: int, target_position: int) -> bool:
        """将章节移动到目标分卷的目标位置。"""
        session = db_manager.get_project_session()
        try:
            chapter = session.query(Chapter)\
                .filter_by(id=chapter_id, is_deleted=False)\
                .first()
            if not chapter:
                return False

            source_volume_id = chapter.volume_id

            source_chapters = session.query(Chapter)\
                .filter_by(volume_id=source_volume_id, is_deleted=False)\
                .order_by(Chapter.chapter_number.asc())\
                .all()

            if source_volume_id == target_volume_id:
                source_chapters = [c for c in source_chapters if c.id != chapter_id]
                target_position = max(1, min(target_position, len(source_chapters) + 1))
                source_chapters.insert(target_position - 1, chapter)

                for idx, ch in enumerate(source_chapters, start=1):
                    ch.chapter_number = idx
            else:
                target_volume = session.query(Volume).filter_by(id=target_volume_id).first()
                if not target_volume:
                    return False

                source_chapters = [c for c in source_chapters if c.id != chapter_id]
                for idx, ch in enumerate(source_chapters, start=1):
                    ch.chapter_number = idx

                chapter.volume_id = target_volume_id

                target_chapters = session.query(Chapter)\
                    .filter_by(volume_id=target_volume_id, is_deleted=False)\
                    .order_by(Chapter.chapter_number.asc())\
                    .all()

                target_position = max(1, min(target_position, len(target_chapters) + 1))
                target_chapters.insert(target_position - 1, chapter)

                for idx, ch in enumerate(target_chapters, start=1):
                    ch.chapter_number = idx

            session.commit()
            signal_bus.chapter_updated.emit(chapter_id)
            logger.info(f"章节重排序成功: {chapter.title} -> 分卷{target_volume_id} 位置{target_position}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"章节重排序失败: {e}")
            raise
        finally:
            session.close()

    def reorder_volume(self, volume_id: int, target_position: int) -> bool:
        """将分卷移动到项目中的目标位置。"""
        session = db_manager.get_project_session()
        try:
            volume = session.query(Volume).filter_by(id=volume_id).first()
            if not volume:
                return False

            project_id = volume.project_id

            volumes = session.query(Volume)\
                .order_by(Volume.sort_order.asc())\
                .all()

            volumes = [v for v in volumes if v.id != volume_id]
            target_position = max(1, min(target_position, len(volumes) + 1))
            volumes.insert(target_position - 1, volume)

            for idx, v in enumerate(volumes, start=1):
                v.sort_order = idx

            session.commit()
            signal_bus.volume_updated.emit(volume_id)
            logger.info(f"分卷重排序成功: {volume.name} -> 位置{target_position}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"分卷重排序失败: {e}")
            raise
        finally:
            session.close()

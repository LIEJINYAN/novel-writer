"""TXT/MD 文件导入服务。"""
import re
from pathlib import Path

from models import db_manager, Volume, Chapter
from utils.logger import logger
from services.import_utils import split_full_book, natural_sort_key, _build_segments


class TxtImportService:
    """导入服务 - 从 .txt / .md 文件导入章节内容。"""

    # ------------------------------------------------------------------
    # 文件导入方法
    # ------------------------------------------------------------------

    @staticmethod
    def import_chapter_from_file(file_path: str, chapter_id: int) -> Chapter:
        """读取 .txt 或 .md 文件，更新指定章节的内容。"""
        path = Path(file_path)
        if not path.is_file():
            raise ValueError(f"文件不存在: {path}")
        if path.suffix.lower() not in (".txt", ".md"):
            raise ValueError(f"不支持的文件格式: {path.suffix}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        session = db_manager.get_session()
        try:
            chapter = session.query(Chapter)\
                .filter_by(id=chapter_id, is_deleted=False)\
                .first()
            if not chapter:
                raise ValueError(f"章节不存在: {chapter_id}")

            chapter.content = content
            chapter.word_count = sum(1 for c in content if not c.isspace())
            session.commit()
            logger.success(f"从文件导入章节完成: {chapter.title}")
            return chapter
        except Exception as e:
            session.rollback()
            logger.error(f"从文件导入章节失败: {e}")
            raise
        finally:
            session.close()

    @staticmethod
    def import_volume_from_dir(dir_path: str, volume_id: int) -> dict:
        """递归扫描目录中所有 .txt / .md 文件，为每个文件创建章节。"""
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise ValueError(f"目录不存在: {dir_path}")

        # 收集所有 .txt 和 .md 文件
        files = []
        for ext in ("*.txt", "*.md"):
            files.extend(dir_path.rglob(ext))

        if not files:
            return {"success": 0, "skipped": 0, "chapters": []}

        # 按文件名自然排序（1, 2, 10 而不是 1, 10, 2）
        files.sort(key=lambda p: natural_sort_key(p.stem))

        session = db_manager.get_session()
        try:
            volume = session.query(Volume).filter_by(id=volume_id).first()
            if not volume:
                raise ValueError(f"分卷不存在: {volume_id}")

            # 从现有最大章节号之后开始编号
            max_chapter = session.query(Chapter)\
                .filter_by(volume_id=volume_id, is_deleted=False)\
                .order_by(Chapter.chapter_number.desc())\
                .first()
            chapter_number = (max_chapter.chapter_number + 1) if max_chapter else 1

            chapters = []
            skipped = 0

            for file_path in files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    logger.warn(f"读取文件失败: {file_path} - {e}")
                    skipped += 1
                    continue

                title = file_path.stem
                chapter = Chapter(
                    volume_id=volume_id,
                    project_id=volume.project_id,
                    chapter_number=chapter_number,
                    title=title,
                    content=content,
                    word_count=sum(1 for c in content if not c.isspace()),
                )
                session.add(chapter)
                chapters.append(chapter)
                chapter_number += 1

            session.commit()
            logger.success(
                f"从目录导入完成: {len(chapters)} 章节, {skipped} 跳过"
            )
            return {"success": len(chapters), "skipped": skipped, "chapters": chapters}
        except Exception as e:
            session.rollback()
            logger.error(f"从目录导入失败: {e}")
            raise
        finally:
            session.close()

    # ------------------------------------------------------------------
    # 全书拆分与导入
    # ------------------------------------------------------------------

    @staticmethod
    def split_full_book(file_path: str) -> list[dict]:
        """委托给 import_utils.split_full_book。"""
        return split_full_book(file_path)

    @staticmethod
    def import_full_book(
        file_path: str,
        project_id: int,
        volume_id: int = None,
        target_name: str = None,
    ) -> dict:
        """拆分全书并导入为独立章节。

        若未提供 *volume_id*，自动创建一个新分卷（名称为 *target_name* 或
        "导入章节"）。
        """
        segments = split_full_book(file_path)
        if not segments:
            return {"success": 0, "volume_id": None, "chapters": []}

        session = db_manager.get_session()
        try:
            if volume_id is None:
                volume = Volume(
                    title=target_name or "导入章节",
                    volume_number=1,
                    sort_order=0,
                    description="",
                )
                session.add(volume)
                session.flush()
                volume_id = volume.id

            chapters = []
            for i, seg in enumerate(segments, start=1):
                chapter = Chapter(
                    volume_id=volume_id,
                    project_id=project_id,
                    chapter_number=i,
                    title=seg["title"],
                    content=seg["content"],
                    word_count=seg["word_count"],
                )
                session.add(chapter)
                chapters.append(chapter)

            session.commit()
            logger.success(f"导入全书完成: {len(chapters)} 章节")
            return {"success": len(chapters), "volume_id": volume_id, "chapters": chapters}
        except Exception as e:
            session.rollback()
            logger.error(f"导入全书失败: {e}")
            raise
        finally:
            session.close()

    # ------------------------------------------------------------------
    # 工具方法（已移至 import_utils，此处保留引用保证兼容）
    # ------------------------------------------------------------------

    @staticmethod
    def natural_sort_key(s: str) -> list:
        """委托给 import_utils.natural_sort_key。"""
        return natural_sort_key(s)

"""PDF 全本导入服务。"""

from pathlib import Path

from models import db_manager, Volume, Chapter
from utils.logger import logger
from services.import_utils import split_text


class PdfImportService:
    """导入服务 - 从 .pdf 文件导入全书。"""

    @staticmethod
    def import_pdf_full_book(
        file_path: str,
        project_id: int,
        volume_id: int = None,
        target_name: str = None,
    ) -> dict:
        """导入 PDF 文件并拆分为多个章节。

        参数同 TxtImportService.import_full_book。返回::

            {"success": N, "volume_id": ID, "chapters": [Chapter, ...]}
        """
        sections = PdfImportService._parse_pdf(file_path)
        if not sections:
            return {"success": 0, "volume_id": None, "chapters": []}

        return PdfImportService._import_sections(
            sections, project_id, volume_id, target_name
        )

    # ------------------------------------------------------------------
    # PDF 解析
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_pdf(file_path: str) -> list[dict]:
        """解析 PDF 文件，提取文本并按章节分割。

        返回::

            [{"title": "...", "content": "...", "word_count": N}, ...]
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("需要 PyMuPDF 库：pip install PyMuPDF")

        path = Path(file_path)
        if not path.is_file():
            raise ValueError(f"文件不存在: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"不支持的文件格式: {path.suffix}")

        doc = fitz.open(str(path))
        total_pages = len(doc)

        if total_pages == 0:
            raise ValueError("PDF 文件为空")

        # 提取全部文本
        full_text = []
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text("text")
            if text:
                full_text.append(text)
                # 每页末尾插入分页标记
                if page_num < total_pages - 1:
                    full_text.append("\f")

        doc.close()

        content = "".join(full_text).strip()

        # 扫描件检测
        if len(content) < 100:
            raise ValueError(
                "该 PDF 可能为扫描件，不包含可提取的文本内容。\n\n"
                "建议使用 OCR 工具（如 Adobe Acrobat、PaddleOCR）"
                "先转换为文本后再导入。"
            )

        logger.success(f"PDF 文本提取完成: {total_pages} 页, {len(content)} 字符")

        # 按章节分割
        sections = split_text(content)

        if not sections:
            # 分割失败时，整本作为一章
            sections = [{
                "title": "全文",
                "content": content,
                "word_count": sum(1 for c in content if not c.isspace()),
            }]

        return sections

    # ------------------------------------------------------------------
    # 导入数据库
    # ------------------------------------------------------------------

    @staticmethod
    def _import_sections(
        sections: list[dict],
        project_id: int,
        volume_id: int = None,
        target_name: str = None,
    ) -> dict:
        """将章节列表导入到数据库。"""
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
            for i, seg in enumerate(sections, start=1):
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
            logger.success(f"PDF 导入完成: {len(chapters)} 章节")
            return {"success": len(chapters), "volume_id": volume_id, "chapters": chapters}
        except Exception as e:
            session.rollback()
            logger.error(f"PDF 导入失败: {e}")
            raise
        finally:
            session.close()

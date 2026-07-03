"""EPUB 全本导入服务。"""

import re
from pathlib import Path

from models import db_manager, Volume, Chapter
from utils.logger import logger


class EpubImportService:
    """导入服务 - 从 .epub 文件导入全书。"""

    @staticmethod
    def import_epub_full_book(
        file_path: str,
        project_id: int,
        volume_id: int = None,
        target_name: str = None,
    ) -> dict:
        """导入 EPUB 文件并拆分为多个章节。

        参数同 TxtImportService.import_full_book。返回::

            {"success": N, "volume_id": ID, "chapters": [Chapter, ...]}
        """
        sections = EpubImportService._parse_epub(file_path)
        if not sections:
            return {"success": 0, "volume_id": None, "chapters": []}

        return EpubImportService._import_sections(
            sections, project_id, volume_id, target_name
        )

    # ------------------------------------------------------------------
    # EPUB 解析
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_epub(file_path: str) -> list[dict]:
        """解析 EPUB 文件，返回章节列表。

        返回::

            [{"title": "...", "content": "...", "word_count": N}, ...]
        """
        try:
            import ebooklib
            from ebooklib import epub
        except ImportError:
            raise ImportError("需要 ebooklib 库：pip install ebooklib")

        path = Path(file_path)
        if not path.is_file():
            raise ValueError(f"文件不存在: {path}")
        if path.suffix.lower() != ".epub":
            raise ValueError(f"不支持的文件格式: {path.suffix}")

        book = epub.read_epub(str(path))
        sections = []

        # 构建 TOC 标题映射 {item_id: title}
        toc_titles = EpubImportService._build_toc_titles(book)

        # 按 spine 顺序提取文档项
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            # 获取原始 HTML
            raw_html = item.get_body_content().decode("utf-8", errors="replace")

            # 清洗 HTML → 纯文本
            text = EpubImportService._html_to_text(raw_html)
            if not text.strip():
                continue

            # 获取标题
            title = toc_titles.get(item.get_id(), "")
            if not title:
                # 从文件名猜测标题
                name = Path(item.get_name()).stem
                # 去掉常见数字前缀
                title = re.sub(r"^[\d_\-]+\s*", "", name).replace("_", " ").replace("-", " ").strip()
                if not title:
                    title = f"第 {len(sections) + 1} 章"

            sections.append({
                "title": title,
                "content": text.strip(),
                "word_count": sum(1 for c in text if not c.isspace()),
            })

        if not sections:
            raise ValueError("EPUB 文件中未找到任何章节内容")

        logger.success(f"EPUB 解析完成: {len(sections)} 章节")
        return sections

    @staticmethod
    def _build_toc_titles(book) -> dict[str, str]:
        """从 EPUB 的 NCX/TOC 构建 {item_id: title} 映射。"""
        titles = {}

        try:
            # 方式 1：从 nav（EPUB3 导航文档）提取
            if hasattr(book, 'toc') and book.toc:
                EpubImportService._extract_toc_entries(book.toc, book, titles)
        except Exception:
            pass

        # 方式 2：从 NCX 提取（EPUB2）
        try:
            if hasattr(book, 'get_metadata') and callable(book.get_metadata):
                ncx = book.get_metadata("http://www.daisy.org/z3986/2005/ncx/")
                # NCX 通常不会直接给出 item 映射，用 navMap 更可靠
        except Exception:
            pass

        # 方式 3：从 spine 包含的 NCX 中手动提取
        try:
            from ebooklib import epub
            ncx_items = [i for i in book.get_items_of_type(ebooklib.ITEM_NCX)]
            for ncx_item in ncx_items:
                content = ncx_item.get_content().decode("utf-8", errors="replace")
                # 解析 NCX navPoint
                import xml.etree.ElementTree as ET
                root = ET.fromstring(content)
                # NCX 命名空间
                ns = {"ncx": "http://www.daisy.org/z3986/2005/ncx/"}
                for nav_point in root.iter("{http://www.daisy.org/z3986/2005/ncx/}navPoint"):
                    text_el = nav_point.find(".//ncx:text", ns)
                    content_el = nav_point.find("ncx:content", ns)
                    if text_el is not None and content_el is not None:
                        src = content_el.get("src", "")
                        # 从 src 提取 item id（去掉 #fragment 和路径）
                        item_src = src.split("#")[0]
                        titles[item_src] = text_el.text or ""
        except Exception:
            pass

        return titles

    @staticmethod
    def _extract_toc_entries(toc_entries, book, titles: dict, depth: int = 0):
        """递归提取 TOC 条目中的标题与文件引用。"""
        if depth > 10:
            return
        for entry in toc_entries:
            if isinstance(entry, tuple) and len(entry) == 2:
                # ebooklib 的 Link 类型：(Link, [sub_entries])
                link, sub_entries = entry
                if hasattr(link, 'href') and hasattr(link, 'title'):
                    href = link.href.split("#")[0]
                    titles[href] = link.title or ""
                if sub_entries:
                    EpubImportService._extract_toc_entries(sub_entries, book, titles, depth + 1)
            elif hasattr(entry, 'href') and hasattr(entry, 'title'):
                href = entry.href.split("#")[0]
                titles[href] = entry.title or ""

    @staticmethod
    def _html_to_text(html: str) -> str:
        """清洗 HTML 为纯文本。"""
        # 移除 <script>、<style> 块
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)

        # 块级标签转换行
        html = re.sub(r"</?(?:p|div|h[1-6]|blockquote|li|tr|br|hr|section|article)[^>]*>",
                     "\n", html, flags=re.IGNORECASE)

        # 移除其余 HTML 标签
        html = re.sub(r"<[^>]+>", "", html)

        # 解码 HTML 实体
        html = html.replace("&nbsp;", " ").replace("&amp;", "&")
        html = html.replace("&lt;", "<").replace("&gt;", ">")
        html = html.replace("&quot;", '"').replace("&apos;", "'")
        html = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), html)

        # 合并多余空行
        html = re.sub(r"\n{3,}", "\n\n", html)

        return html.strip()

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
            logger.success(f"EPUB 导入完成: {len(chapters)} 章节")
            return {"success": len(chapters), "volume_id": volume_id, "chapters": chapters}
        except Exception as e:
            session.rollback()
            logger.error(f"EPUB 导入失败: {e}")
            raise
        finally:
            session.close()

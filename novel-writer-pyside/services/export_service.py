"""导出服务 - 支持多种格式导出。"""
import json
from pathlib import Path
from datetime import datetime
from models import db_manager, Project, Volume, Chapter, Character, ChapterAppearance, PlotArc, PlotNode, PlotForeshadow
from utils.logger import logger


class ExportService:
    """导出服务 - 管理项目的各种格式导出。"""

    def __init__(self):
        pass

    # ── 内部辅助方法 ──────────────────────────────────────────

    def _get_full_chapter_list(self, project_id: int) -> list:
        """获取项目所有未删除章节，按分卷排序、章节号排序。返回 (volume_name, chapter) 列表。"""
        session = db_manager.get_project_session()
        try:
            volumes = (
                session.query(Volume)
                .order_by(Volume.sort_order.asc())
                .all()
            )
            chapters = (
                session.query(Chapter)
                .filter_by(is_deleted=False)
                .order_by(Chapter.chapter_number.asc())
                .all()
            )
            # 构建带分卷信息的列表
            result = []
            volume_map = {v.id: v for v in volumes}
            for ch in chapters:
                vol = volume_map.get(ch.volume_id)
                vol_name = vol.name if vol else ""
                result.append((vol_name, ch))
            return result
        finally:
            session.close()

    def _get_volume_name_by_id(self, volume_id: int) -> str:
        """根据分卷ID获取分卷名称。"""
        session = db_manager.get_project_session()
        try:
            vol = session.query(Volume).filter_by(id=volume_id).first()
            return vol.name if vol else ""
        finally:
            session.close()

    def _get_project(self, project_id: int) -> Project:
        """获取项目对象。"""
        session = db_manager.get_project_session()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                raise ValueError(f"项目不存在: {project_id}")
            return project
        finally:
            session.close()

    def _ensure_parent_dir(self, file_path: str) -> None:
        """确保目标文件的父目录存在。"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    # ── TXT / MD 基础输出 ────────────────────────────────────

    def _build_txt_content(self, project_id: int) -> str:
        """构建完整小说的 TXT 内容。"""
        chapters = self._get_full_chapter_list(project_id)
        lines = []
        for vol_name, ch in chapters:
            if vol_name:
                lines.append(f"【{vol_name}】")
            lines.append(f"=== 第{ch.chapter_number}章 {ch.title} ===")
            lines.append("")
            lines.append(ch.content or "")
            lines.append("")
            lines.append("")
        return "\n".join(lines)

    def _build_md_content(self, project_id: int) -> str:
        """构建完整小说的 Markdown 内容。"""
        chapters = self._get_full_chapter_list(project_id)
        lines = []
        current_vol = None
        for vol_name, ch in chapters:
            if vol_name and vol_name != current_vol:
                lines.append(f"# {vol_name}")
                lines.append("")
                current_vol = vol_name
            lines.append(f"## 第{ch.chapter_number}章 {ch.title}")
            lines.append("")
            lines.append(ch.content or "")
            lines.append("")
        return "\n".join(lines)

    def _build_single_txt(self, chapter: Chapter, volume_name: str = "") -> str:
        """构建单章的 TXT 内容。"""
        lines = []
        if volume_name:
            lines.append(f"【{volume_name}】")
        lines.append(f"=== 第{chapter.chapter_number}章 {chapter.title} ===")
        lines.append("")
        lines.append(chapter.content or "")
        lines.append("")
        return "\n".join(lines)

    def _build_single_md(self, chapter: Chapter, volume_name: str = "") -> str:
        """构建单章的 Markdown 内容。"""
        lines = []
        if volume_name:
            lines.append(f"# {volume_name}")
            lines.append("")
        lines.append(f"## 第{chapter.chapter_number}章 {chapter.title}")
        lines.append("")
        lines.append(chapter.content or "")
        lines.append("")
        return "\n".join(lines)

    # ── 完整导出方法 ──────────────────────────────────────────

    def export_to_original(self, project_id: int, target_path: str) -> str:
        """导出为原始 TypeScript 格式目录结构。

        匹配原版 `novel init` 创建的项目结构：
            .specify/config.json + memory/
            stories/001.md, 002.md, ...
            spec/config.json + tracking/ + knowledge/

        Args:
            project_id: 项目 ID
            target_path: 目标目录路径

        Returns:
            导出的目录路径
        """
        project = self._get_project(project_id)
        chapters = self._get_full_chapter_list(project_id)
        root = Path(target_path)
        root.mkdir(parents=True, exist_ok=True)

        # ---- .specify/config.json ----
        specify_config = {
            "name": project.name,
            "type": project.genre or "novel",
            "ai": "claude",
            "method": project.writing_method or "three-act",
            "created": datetime.now().isoformat(),
            "version": "1.0.0",
        }
        specify_dir = root / ".specify"
        specify_dir.mkdir(parents=True, exist_ok=True)
        with open(str(specify_dir / "config.json"), "w", encoding="utf-8") as f:
            json.dump(specify_config, f, ensure_ascii=False, indent=2)

        # ---- .specify/memory/ ----
        memory_dir = specify_dir / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        self._write_template(memory_dir / "constitution.md",
            "# 创作宪法\n\n## 写作原则\n\n"
            "- 保持真实的情感表达\n"
            "- 避免陈词滥调\n"
            "- 展示而非讲述\n\n")
        self._write_template(memory_dir / "personal-voice.md",
            "# 个人风格\n\n## 语言特点\n\n"
            "- 自然的对话节奏\n- 细腻的环境描写\n\n")

        # ---- stories/ ----
        stories_dir = root / "stories"
        stories_dir.mkdir(parents=True, exist_ok=True)
        for idx, (vol_name, ch) in enumerate(chapters, start=1):
            lines = [f"# 第{ch.chapter_number}章 {ch.title}", ""]
            if vol_name:
                lines.insert(0, f"> {vol_name}")
                lines.insert(1, "")
            lines.append(ch.content or "")
            story_file = stories_dir / f"{idx:03d}.md"
            with open(str(story_file), "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

        # ---- spec/config.json ----
        spec_dir = root / "spec"
        spec_dir.mkdir(parents=True, exist_ok=True)
        spec_config = {
            "version": "1.0.0",
            "project": {
                "name": project.name,
                "type": project.genre or "novel",
                "language": "zh-CN",
            },
            "method": {
                "current": project.writing_method or "three-act",
                "available": [
                    "three-act", "hero-journey", "story-circle",
                    "seven-point", "pixar-formula", "snowflake",
                ],
                "mixMode": False,
            },
            "features": {
                "tracking": {
                    "enabled": True,
                    "autoSave": True,
                    "files": [
                        "plot-tracker.json", "character-state.json",
                        "relationships.json", "timeline.json",
                    ],
                },
                "ai": {
                    "defaultAssistant": "claude",
                    "temperature": 0.7,
                    "maxTokens": 4000,
                },
            },
            "preferences": {
                "chapterLength": {
                    "min": 3000,
                    "max": 5000,
                    "target": project.target_words or 4000,
                },
                "backupEnabled": True,
            },
        }
        with open(str(spec_dir / "config.json"), "w", encoding="utf-8") as f:
            json.dump(spec_config, f, ensure_ascii=False, indent=2)

        # ---- spec/tracking/ ----
        tracking_dir = spec_dir / "tracking"
        tracking_dir.mkdir(parents=True, exist_ok=True)
        self._export_tracking_character(session := db_manager.get_project_session(), project_id, tracking_dir)
        self._export_tracking_plot(session, project_id, tracking_dir)
        self._export_tracking_relationships(session, project_id, tracking_dir)
        self._export_tracking_timeline(session, project_id, tracking_dir)
        self._export_tracking_validation(session, project_id, tracking_dir, project)
        session.close()

        # ---- spec/knowledge/ ----
        knowledge_dir = spec_dir / "knowledge"
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        self._write_template(knowledge_dir / "world-setting.md",
            "# 世界观设定\n\n## 世界概述\n\n\n## 地理环境\n\n\n## 社会结构\n\n\n## 魔法/科技体系\n\n\n")
        self._write_template(knowledge_dir / "locations.md",
            "# 地点设定\n\n| 地点 | 描述 | 重要事件 |\n|------|------|---------|\n|      |      |         |\n\n")

        logger.success(f"导出原始格式成功: {root}")
        return str(root)

    # ---- tracking 导出辅助方法 ----

    def _write_template(self, path: Path, content: str):
        """写入模板文件，仅当文件不存在时。"""
        if not path.exists():
            path.write_text(content, encoding="utf-8")

    def _export_tracking_character(self, session, project_id: int, tracking_dir: Path):
        """导出 character-state.json。"""
        chars = session.query(Character).filter_by(is_deleted=0).all()
        data = {
            "novel": "",
            "lastUpdated": datetime.now().isoformat(),
            "protagonist": {},
            "supportingCharacters": {},
            "characterGroups": {"active": [], "inactive": [], "deceased": []},
            "appearanceTracking": [],
            "consistency": {"physicalTraits": {}, "personalityTraits": {}, "speechPatterns": {}, "warnings": []},
        }
        for c in chars:
            if c.role_type == "主角":
                data["protagonist"] = {
                    "name": c.name,
                    "currentStatus": {"alive": True, "health": c.status or "良好", "mentalState": "正常", "location": ""},
                    "development": {"arc": c.arc or "", "milestones": [], "currentPhase": ""},
                }
                data["characterGroups"]["active"].append(c.name)
            else:
                data["supportingCharacters"][c.name] = {
                    "role": c.role_type or "配角",
                    "importance": "medium",
                    "status": {"alive": True, "lastSeen": {"chapter": None, "location": ""}},
                    "arc": {"planned": c.notes or "", "current": ""},
                }
                data["characterGroups"]["active"].append(c.name)
        with open(str(tracking_dir / "character-state.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _export_tracking_plot(self, session, project_id: int, tracking_dir: Path):
        """导出 plot-tracker.json。"""
        arcs = session.query(PlotArc).all()
        data = {
            "novel": "",
            "lastUpdated": datetime.now().isoformat(),
            "currentState": {"chapter": 1, "volume": 1, "mainPlotStage": "开端"},
            "plotlines": {
                "main": {
                    "name": "", "description": "", "status": "active",
                    "currentNode": "", "completedNodes": [], "upcomingNodes": [],
                },
                "subplots": [],
            },
            "foreshadowing": [],
            "sections": [],
        }
        # 弧线→plotlines
        for arc in arcs:
            nodes = session.query(PlotNode).filter_by(arc_id=arc.id).order_by(PlotNode.sort_order).all()
            arc_entry = {
                "name": arc.name,
                "description": arc.description or "",
                "status": "active", "currentNode": "",
                "completedNodes": [], "upcomingNodes": [],
            }
            for n in nodes:
                if n.status == "已完成":
                    arc_entry["completedNodes"].append(n.title)
                else:
                    arc_entry["upcomingNodes"].append(n.title)
            data["plotlines"]["subplots"].append(arc_entry)

        # 伏笔→foreshadowing
        all_nodes = session.query(PlotNode).all()
        node_ids = [n.id for n in all_nodes]
        if node_ids:
            foreshadows = session.query(PlotForeshadow).filter(
                PlotForeshadow.node_id.in_(node_ids)
            ).all()
            for fs in foreshadows:
                data["foreshadowing"].append({
                    "id": f"foreshadow-{fs.id}",
                    "content": fs.description or "",
                    "planted": {"chapter": None, "description": ""},
                    "hints": [],
                    "plannedReveal": {"chapter": None, "description": ""},
                    "status": fs.status or "已埋设",
                })
        with open(str(tracking_dir / "plot-tracker.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _export_tracking_relationships(self, session, project_id: int, tracking_dir: Path):
        """导出 relationships.json。"""
        chars = session.query(Character).filter_by(is_deleted=0).all()
        char_map = {}
        for c in chars:
            char_map[c.name] = {
                "relationships": {
                    "allies": [], "enemies": [], "romantic": [],
                    "family": [], "mentors": [], "neutral": [], "unknown": [],
                },
                "dynamicRelations": [],
            }
        data = {"novel": "", "lastUpdated": "", "characters": char_map, "factions": {}}
        with open(str(tracking_dir / "relationships.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _export_tracking_timeline(self, session, project_id: int, tracking_dir: Path):
        """导出 timeline.json。"""
        chapters = session.query(Chapter).filter_by(
            is_deleted=0
        ).order_by(Chapter.chapter_number).all()
        events = []
        for ch in chapters:
            events.append({
                "chapter": ch.chapter_number,
                "date": "",
                "event": ch.title,
                "duration": "",
                "participants": [],
            })
        data = {
            "novel": "", "lastUpdated": "",
            "storyTime": {"start": "", "current": "", "end": ""},
            "events": events,
        }
        with open(str(tracking_dir / "timeline.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _export_tracking_validation(self, session, project_id: int, tracking_dir: Path, project: Project):
        """导出 validation-rules.json。"""
        chars = session.query(Character).filter_by(is_deleted=0).all()
        protagonist_name = ""
        supporting = {}
        for c in chars:
            if c.role_type == "主角" and not protagonist_name:
                protagonist_name = c.name
            else:
                supporting[c.name] = {
                    "aliases": [],
                    "note": c.notes or "",
                }
        data = {
            "version": "1.0",
            "description": "小说内容验证规则",
            "characters": {
                "protagonist": {
                    "name": protagonist_name or "[主角名]",
                    "aliases": [], "forbidden": [],
                    "traits": [], "note": "",
                },
                "supporting": supporting,
            },
            "world": {
                "rules": [], "consistency": {"time": True, "space": True, "cause": True},
            },
        }
        with open(str(tracking_dir / "validation-rules.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def export_txt(self, project_id: int, file_path: str) -> str:
        """导出完整小说为单个 TXT 文件。

        Args:
            project_id: 项目 ID
            file_path: 目标文件路径

        Returns:
            导出的文件路径
        """
        project = self._get_project(project_id)
        self._ensure_parent_dir(file_path)

        content = self._build_txt_content(project_id)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.success(f"导出 TXT 成功: {file_path}")
        return file_path

    def export_md(self, project_id: int, file_path: str) -> str:
        """导出完整小说为单个 Markdown 文件。

        Args:
            project_id: 项目 ID
            file_path: 目标文件路径

        Returns:
            导出的文件路径
        """
        project = self._get_project(project_id)
        self._ensure_parent_dir(file_path)

        content = self._build_md_content(project_id)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.success(f"导出 MD 成功: {file_path}")
        return file_path

    def export_epub(self, project_id: int, file_path: str, settings: dict = None) -> str:
        """导出完整小说为 EPUB 电子书。

        Args:
            project_id: 项目 ID
            file_path: 目标文件路径
            settings: 可选设置字典，支持:
                - author (str): 作者名
                - cover_image (str): 封面图片路径
                - publisher (str): 出版商

        Returns:
            导出的文件路径
        """
        try:
            from ebooklib import epub
        except ImportError:
            logger.error("ebooklib 未安装，请执行 pip install ebooklib")
            raise ImportError("ebooklib 未安装，请执行 pip install ebooklib")

        settings = settings or {}
        project = self._get_project(project_id)
        chapters = self._get_full_chapter_list(project_id)
        self._ensure_parent_dir(file_path)

        book = epub.EpubBook()

        # 元数据
        book.set_identifier(f"novel-writer-{project_id}-{datetime.now():%Y%m%d%H%M%S}")
        book.set_title(project.name)
        book.set_language("zh-CN")
        if settings.get("author"):
            book.add_author(settings["author"])
        if settings.get("publisher"):
            book.add_metadata("DC", "publisher", settings["publisher"])

        # 封面（如有提供图片）
        cover_path = settings.get("cover_image") or project.cover_image
        if cover_path and Path(cover_path).exists():
            with open(cover_path, "rb") as img_file:
                book.set_cover("cover.jpg", img_file.read())

        # CSS 样式
        style = """
        @namespace epub "http://www.idpf.org/2007/ops";
        body { font-family: "SimSun", "Songti SC", serif; line-height: 1.8; padding: 1em; }
        h1 { text-align: center; font-size: 1.6em; margin: 1.5em 0 0.5em; }
        h2 { text-align: center; font-size: 1.3em; margin: 1.2em 0 0.5em; }
        p { text-indent: 2em; margin: 0.3em 0; }
        .chapter { margin: 1em 0; }
        """
        css_item = epub.EpubItem(
            uid="style",
            file_name="style/default.css",
            media_type="text/css",
            content=style.encode("utf-8"),
        )
        book.add_item(css_item)

        # 生成各章节
        epub_chapters = []
        for vol_name, ch in chapters:
            # 构建章节 HTML
            html_parts = [
                "<!DOCTYPE html>",
                '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">',
                "<head>",
                '<meta charset="utf-8"/>',
                f"<title>第{ch.chapter_number}章 {ch.title}</title>",
                '<link rel="stylesheet" type="text/css" href="style/default.css"/>',
                "</head>",
                "<body>",
            ]
            if vol_name:
                html_parts.append(f"<h1>{vol_name}</h1>")
            html_parts.append(f"<h2>第{ch.chapter_number}章 {ch.title}</h2>")
            html_parts.append('<div class="chapter">')
            # 将换行转为段落
            paragraphs = (ch.content or "").split("\n")
            for para in paragraphs:
                stripped = para.strip()
                if stripped:
                    html_parts.append(f"<p>{stripped}</p>")
            html_parts.append("</div>")
            html_parts.append("</body>")
            html_parts.append("</html>")

            ch_item = epub.EpubHtml(
                title=f"第{ch.chapter_number}章 {ch.title}",
                file_name=f"chapter_{ch.chapter_number:03d}.xhtml",
                lang="zh-CN",
            )
            ch_item.content = "\n".join(html_parts).encode("utf-8")
            ch_item.add_item(css_item)
            book.add_item(ch_item)
            epub_chapters.append(ch_item)

        # 构建 TOC：有分卷则用嵌套结构，否则扁平
        toc_entries = []
        current_vol = None
        vol_sub_chapters = []
        for idx, (vol_name, ch) in enumerate(chapters):
            ch_item = epub_chapters[idx]
            if vol_name:
                if vol_name != current_vol:
                    if vol_sub_chapters and current_vol:
                        toc_entries.append((epub.Section(current_vol), vol_sub_chapters))
                    current_vol = vol_name
                    vol_sub_chapters = [ch_item]
                else:
                    vol_sub_chapters.append(ch_item)
            else:
                if vol_sub_chapters and current_vol:
                    toc_entries.append((epub.Section(current_vol), vol_sub_chapters))
                    current_vol = None
                    vol_sub_chapters = []
                toc_entries.append(ch_item)

        if vol_sub_chapters and current_vol:
            toc_entries.append((epub.Section(current_vol), vol_sub_chapters))
        if not toc_entries:
            toc_entries = epub_chapters[:]

        book.toc = toc_entries

        # 添加导航文件
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # 设置阅读顺序
        book.spine = ["nav"] + epub_chapters

        # 生成 EPUB 文件
        epub.write_epub(file_path, book, {})
        logger.success(f"导出 EPUB 成功: {file_path}")
        return file_path

    def export_pdf(self, project_id: int, file_path: str, settings: dict = None) -> str:
        """导出完整小说为 PDF 文件。

        Args:
            project_id: 项目 ID
            file_path: 目标文件路径
            settings: 可选设置字典，支持:
                - author (str): 作者名
                - font_size (int): 正文字号，默认 12
                - page_size (str): 页面尺寸，默认 'A4'
                - margin (int): 页边距(mm)，默认 20

        Returns:
            导出的文件路径
        """
        try:
            from fpdf import FPDF
        except ImportError:
            logger.error("fpdf2 未安装，请执行 pip install fpdf2")
            raise ImportError("fpdf2 未安装，请执行 pip install fpdf2")

        settings = settings or {}
        project = self._get_project(project_id)
        chapters = self._get_full_chapter_list(project_id)
        self._ensure_parent_dir(file_path)

        font_size = settings.get("font_size", 12)
        page_size = settings.get("page_size", "A4")
        margin = settings.get("margin", 20)
        author = settings.get("author", "")

        pdf = FPDF(orientation="P", unit="mm", format=page_size)
        pdf.set_auto_page_break(auto=True, margin=margin + 10)
        pdf.add_page()

        # ── 中文字体处理 ──
        font_family = self._setup_pdf_cjk_font(pdf)

        # ── 书名页 ──
        pdf.ln(60)
        pdf.set_font(font_family, "", 28)
        pdf.multi_cell(0, 15, project.name, align="C")
        pdf.ln(10)
        if author:
            pdf.set_font(font_family, "", 14)
            pdf.multi_cell(0, 10, author, align="C")
        pdf.ln(5)
        pdf.set_font(font_family, "", 10)
        pdf.multi_cell(0, 8, f"导出日期: {datetime.now():%Y-%m-%d}", align="C")

        # ── 章节内容 ──
        current_vol = None
        for vol_name, ch in chapters:
            # 分卷标题页
            if vol_name and vol_name != current_vol:
                pdf.add_page()
                pdf.ln(50)
                pdf.set_font(font_family, "", 20)
                pdf.multi_cell(0, 12, vol_name, align="C")
                pdf.ln(10)
                current_vol = vol_name

            # 检查是否需要新页（章节标题前空行够就继续，否则新页）
            if pdf.get_y() > 180:
                pdf.add_page()

            # 章节标题
            pdf.set_font(font_family, "", font_size + 4)
            title_text = f"第{ch.chapter_number}章 {ch.title}"
            pdf.multi_cell(0, 10, title_text, align="C")
            pdf.ln(5)

            # 正文
            pdf.set_font(font_family, "", font_size)
            paragraphs = (ch.content or "").split("\n")
            for para in paragraphs:
                stripped = para.strip()
                if stripped:
                    # 检查是否需要分页
                    if pdf.get_y() > 250:
                        pdf.add_page()
                        pdf.set_font(font_family, "", font_size)
                    pdf.multi_cell(0, 6.5, stripped, align="L")
                    pdf.ln(2)

            pdf.ln(5)

        pdf.output(file_path)
        logger.success(f"导出 PDF 成功: {file_path}")
        return file_path

    def _setup_pdf_cjk_font(self, pdf: "FPDF") -> str:
        """为 PDF 设置中文字体，返回字体族名称。"""
        # 候选字体路径（Windows 常见中文字体 TTF/TTC）
        candidates = [
            # TrueType 字体
            "C:\\Windows\\Fonts\\simhei.ttf",
            "C:\\Windows\\Fonts\\SIMFANG.TTF",
            "C:\\Windows\\Fonts\\SIMLI.TTF",
            "C:\\Windows\\Fonts\\SIMKAI.TTF",
            "C:\\Windows\\Fonts\\msyh.ttf",
            # TrueType Collection
            "C:\\Windows\\Fonts\\msyh.ttc",
            "C:\\Windows\\Fonts\\simsun.ttc",
            "C:\\Windows\\Fonts\\Deng.ttf",
            "C:\\Windows\\Fonts\\YaHei.ttf",
            "C:\\Windows\\Fonts\\ygyx.ttf",
        ]

        for font_path in candidates:
            if Path(font_path).exists():
                try:
                    ext = Path(font_path).suffix.lower()
                    if ext == ".ttc":
                        pdf.add_font("CJK", "", font_path, uni=True)
                    else:
                        pdf.add_font("CJK", "", font_path, uni=True)
                    logger.info(f"PDF 使用字体: {font_path}")
                    return "CJK"
                except Exception:
                    continue

        # 回退：使用内置字体（不完整支持中文，但不会崩溃）
        logger.warn("未找到系统 CJK 字体，PDF 中文可能无法正常显示")
        return "Helvetica"

    # ── 单章导出 ──────────────────────────────────────────────

    def export_chapter_txt(self, chapter_id: int, file_path: str) -> str:
        """导出单章为 TXT 文件。

        Args:
            chapter_id: 章节 ID
            file_path: 目标文件路径

        Returns:
            导出的文件路径
        """
        session = db_manager.get_project_session()
        try:
            chapter = session.query(Chapter).filter_by(id=chapter_id, is_deleted=False).first()
            if not chapter:
                raise ValueError(f"章节不存在: {chapter_id}")
            vol_name = chapter.volume.name if chapter.volume else ""
        finally:
            session.close()

        self._ensure_parent_dir(file_path)
        content = self._build_single_txt(chapter, vol_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.success(f"导出章节 TXT 成功: {file_path}")
        return file_path

    def export_chapter_md(self, chapter_id: int, file_path: str) -> str:
        """导出单章为 Markdown 文件。

        Args:
            chapter_id: 章节 ID
            file_path: 目标文件路径

        Returns:
            导出的文件路径
        """
        session = db_manager.get_project_session()
        try:
            chapter = session.query(Chapter).filter_by(id=chapter_id, is_deleted=False).first()
            if not chapter:
                raise ValueError(f"章节不存在: {chapter_id}")
            vol_name = chapter.volume.name if chapter.volume else ""
        finally:
            session.close()

        self._ensure_parent_dir(file_path)
        content = self._build_single_md(chapter, vol_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.success(f"导出章节 MD 成功: {file_path}")
        return file_path

    # ── 分卷导出 ──────────────────────────────────────────────

    def export_volume_txt(self, volume_id: int, file_path: str) -> str:
        """导出一个分卷的所有章节为 TXT 文件。

        Args:
            volume_id: 分卷 ID
            file_path: 目标文件路径

        Returns:
            导出的文件路径
        """
        session = db_manager.get_project_session()
        try:
            volume = session.query(Volume).filter_by(id=volume_id).first()
            if not volume:
                raise ValueError(f"分卷不存在: {volume_id}")
            chapters = (
                session.query(Chapter)
                .filter_by(volume_id=volume_id, is_deleted=False)
                .order_by(Chapter.chapter_number.asc())
                .all()
            )
            vol_name = volume.name
        finally:
            session.close()

        self._ensure_parent_dir(file_path)
        lines = []
        for ch in chapters:
            lines.append(f"=== 第{ch.chapter_number}章 {ch.title} ===")
            lines.append("")
            lines.append(ch.content or "")
            lines.append("")
            lines.append("")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.success(f"导出分卷 TXT 成功: {file_path}")
        return file_path

    def export_volume_md(self, volume_id: int, file_path: str) -> str:
        """导出一个分卷的所有章节为 Markdown 文件。

        Args:
            volume_id: 分卷 ID
            file_path: 目标文件路径

        Returns:
            导出的文件路径
        """
        session = db_manager.get_project_session()
        try:
            volume = session.query(Volume).filter_by(id=volume_id).first()
            if not volume:
                raise ValueError(f"分卷不存在: {volume_id}")
            chapters = (
                session.query(Chapter)
                .filter_by(volume_id=volume_id, is_deleted=False)
                .order_by(Chapter.chapter_number.asc())
                .all()
            )
            vol_name = volume.name
        finally:
            session.close()

        self._ensure_parent_dir(file_path)
        lines = [
            f"# {vol_name}",
            "",
        ]
        for ch in chapters:
            lines.append(f"## 第{ch.chapter_number}章 {ch.title}")
            lines.append("")
            lines.append('<div class="chapter">')
            lines.append("")
            lines.append(ch.content or "")
            lines.append("")
            lines.append("</div>")
            lines.append("")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.success(f"导出分卷 MD 成功: {file_path}")
        return file_path

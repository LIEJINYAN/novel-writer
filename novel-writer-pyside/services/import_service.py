"""从 TypeScript novel-writer v0.20.0 格式导入项目。"""
import json
import os
from pathlib import Path
from datetime import datetime

from models import db_manager, Project, Volume, Chapter, Character, ChapterAppearance, PlotArc, PlotNode
from utils.logger import logger
from utils.signal_bus import signal_bus


class ImportService:
    """导入服务 - 从原始 TypeScript 版 novel-writer 格式导入项目。"""

    @staticmethod
    def detect_original_project(path: str) -> bool:
        """检查目录是否为有效的原始项目。"""
        return (Path(path) / ".specify" / "config.json").exists()

    @staticmethod
    def import_original_project(path: str, target_name: str = None) -> int:
        """导入一个完整的原始项目到当前 SQLite 数据库。"""
        if not ImportService.detect_original_project(path):
            raise ValueError(f"路径不是有效的原始项目: {path}")

        root = Path(path)

        # 读取项目配置
        specify_cfg = ImportService._read_json(root / ".specify" / "config.json") or {}
        sys_cfg = ImportService._read_json(root / "spec" / "config.json") or {}

        project_name = target_name or specify_cfg.get("name") or root.name
        genre = specify_cfg.get("type", "")
        writing_method = specify_cfg.get("method") or sys_cfg.get("method", {}).get("current", "three-act")

        # 从系统配置提取目标字数
        pref = sys_cfg.get("preferences", {})
        chapter_len = pref.get("chapterLength", {})
        target_words = chapter_len.get("target", 0)

        session = db_manager.get_project_session()
        try:
            # 创建项目
            project = Project(
                name=project_name,
                genre=genre,
                writing_method=writing_method,
                target_words=target_words,
                description=specify_cfg.get("description", ""),
            )
            projects_dir = Path(db_manager.data_dir) / "projects" / project_name
            projects_dir.mkdir(parents=True, exist_ok=True)
            project.path = str(projects_dir)
            project.status = "active"
            session.add(project)
            session.flush()
            logger.success(f"项目创建成功: {project.name}")

            # 导入各模块
            ImportService._import_chapters(session, root, project)
            ImportService._import_characters(session, root, project)
            ImportService._import_plot_tracker(session, root, project)
            ImportService._import_tracking_notes(session, root, project)
            ImportService._import_knowledge(session, root, project)
            ImportService._import_memory(session, root, project)
            ImportService._import_experts(session, root, project)

            session.commit()
            logger.success(f"项目导入完成: {project.name} (id={project.id})")

            signal_bus.project_created.emit(project.id)
            return project.id

        except Exception as e:
            session.rollback()
            logger.error(f"导入项目失败: {e}")
            raise
        finally:
            session.close()

    # ------------------------------------------------------------------
    # 内部辅助方法
    # ------------------------------------------------------------------

    @staticmethod
    def _read_json(path: Path) -> dict | list | None:
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warn(f"读取 JSON 失败: {path} - {e}")
        return None

    @staticmethod
    def _read_text(path: Path) -> str | None:
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            logger.warn(f"读取文本失败: {path} - {e}")
        return None

    @staticmethod
    def _import_chapters(session, root: Path, project: Project):
        """从 stories/ 目录导入章节。

        支持两种结构：
        1. 扁平 stories/001.md, stories/002.md（最佳）
        2. 嵌套 stories/<name>/story.md（单个故事文件）
        3. 递归搜索所有 .md 文件
        """
        stories_dir = root / "stories"
        if not stories_dir.is_dir():
            logger.warn(f"stories 目录不存在: {stories_dir}")
            return

        # 创建默认分卷
        volume = Volume(
            title="第一卷",
            volume_number=1,
            sort_order=1,
            description="默认分卷",
        )
        session.add(volume)
        session.flush()

        # 递归搜索 .md 文件，按路径排序保证顺序
        md_files = sorted(
            stories_dir.rglob("*.md"),
            key=lambda p: p.relative_to(stories_dir),
        )
        if not md_files:
            logger.warn(f"stories 目录中没有 .md 文件")
            return

        for idx, md_file in enumerate(md_files, start=1):
            content = ImportService._read_text(md_file)
            if content is None:
                continue

            # 文件名映射到章节号
            try:
                chapter_number = int(md_file.stem)
            except ValueError:
                chapter_number = idx

            # 从内容提取标题
            title = md_file.stem
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("## ") or stripped.startswith("# "):
                    title = stripped.lstrip("#").strip()
                    break

            chapter = Chapter(
                volume_id=volume.id,
                project_id=project.id,
                chapter_number=chapter_number,
                title=title,
                content=content,
                word_count=sum(1 for c in content if not c.isspace()),
                status="draft",
            )
            session.add(chapter)
            logger.info(f"导入章节: #{chapter_number} {title}")

    @staticmethod
    def _import_characters(session, root: Path, project: Project):
        """从 spec/tracking/character-state.json 导入角色。

        原版格式：
        {
          "protagonist": { "name": "...", ... },
          "supportingCharacters": { "配角名": { "role": "...", ... }, ... },
          "characterGroups": { "active": [], ... },
          "appearanceTracking": [ { "chapter": N, "appearances": [...] } ]
        }
        """
        char_path = root / "spec" / "tracking" / "character-state.json"
        data = ImportService._read_json(char_path)
        if data is None or not isinstance(data, dict):
            return

        # 导入主角
        protagonist = data.get("protagonist")
        if isinstance(protagonist, dict) and protagonist.get("name"):
            char = Character(
                project_id=project.id,
                name=protagonist["name"],
                role_type="主角",
                status=protagonist.get("currentStatus", {}).get("health", "活跃"),
                arc=protagonist.get("development", {}).get("arc", ""),
            )
            session.add(char)
            session.flush()
            logger.info(f"导入角色(主角): {char.name}")

        # 导入配角
        supporting = data.get("supportingCharacters", {})
        if isinstance(supporting, dict):
            for name, info in supporting.items():
                if not isinstance(info, dict) or not name.strip():
                    continue
                char = Character(
                    project_id=project.id,
                    name=name,
                    role_type=info.get("role", "配角"),
                    status="活跃",
                    notes=info.get("arc", {}).get("planned", ""),
                )
                session.add(char)
                logger.info(f"导入角色(配角): {char.name}")

        # 导入出场记录
        appearances = data.get("appearanceTracking", [])
        if isinstance(appearances, list):
            for entry in appearances:
                chapter_num = entry.get("chapter")
                if not chapter_num:
                    continue
                # 查找对应章节
                ch = session.query(Chapter).filter(
                    Chapter.project_id == project.id,
                    Chapter.chapter_number == chapter_num,
                ).first()
                if not ch:
                    continue
                for app in entry.get("appearances", []):
                    if not isinstance(app, dict):
                        continue
                    app_char = session.query(Character).filter(
                        Character.project_id == project.id,
                        Character.name == app.get("character", ""),
                    ).first()
                    if app_char:
                        ca = ChapterAppearance(
                            character_id=app_char.id,
                            chapter_id=ch.id,
                            role=app.get("role", "次要"),
                            context=app.get("significance", ""),
                        )
                        session.add(ca)

    @staticmethod
    def _import_plot_tracker(session, root: Path, project: Project):
        """从 spec/tracking/plot-tracker.json 导入情节弧线和节点。"""
        plot_path = root / "spec" / "tracking" / "plot-tracker.json"
        data = ImportService._read_json(plot_path)
        if data is None:
            return

        arcs = data
        if isinstance(data, dict):
            arcs = data.get("arcs", data.get("plot_arcs", []))

        if isinstance(arcs, dict):
            arcs = list(arcs.values())

        if not isinstance(arcs, list):
            logger.warn("plot-tracker.json 格式不符合预期，跳过")
            return

        for i, arc_data in enumerate(arcs):
            if not isinstance(arc_data, dict):
                continue
            arc = PlotArc(
                project_id=project.id,
                name=arc_data.get("name", f"情节弧线 {i+1}"),
                description=arc_data.get("description", ""),
                sort_order=i,
            )
            session.add(arc)
            session.flush()

            nodes = arc_data.get("nodes", [])
            if isinstance(nodes, dict):
                nodes = list(nodes.values())
            if not isinstance(nodes, list):
                continue

            for j, node_data in enumerate(nodes):
                if not isinstance(node_data, dict):
                    continue
                node = PlotNode(
                    project_id=project.id,
                    arc_id=arc.id,
                    title=node_data.get("title", f"节点 {j+1}"),
                    description=node_data.get("description", ""),
                    status=node_data.get("status", "计划中"),
                    importance=node_data.get("importance", "重要"),
                    sort_order=j,
                    notes=node_data.get("notes", ""),
                )
                session.add(node)
                logger.info(f"导入情节节点: {node.title}")

    @staticmethod
    def _import_tracking_notes(session, root: Path, project: Project):
        """将 spec/tracking/ 下其他文件内容追加到项目描述。"""
        tracking_dir = root / "spec" / "tracking"
        if not tracking_dir.is_dir():
            return

        skipped = {"plot-tracker.json", "character-state.json"}
        notes = []
        for f in sorted(tracking_dir.iterdir()):
            if f.name in skipped or not f.is_file():
                continue
            content = ImportService._read_text(f)
            if content:
                notes.append(f"--- {f.name} ---\n{content}")

        if notes:
            extra = "\n\n".join(notes)
            project.description = (project.description + "\n\n" + extra) if project.description else extra
            logger.info(f"导入 {len(notes)} 个 tracking 文件")

    @staticmethod
    def _import_knowledge(session, root: Path, project: Project):
        """导入 spec/knowledge/ 的用户知识文件。"""
        d = root / "spec" / "knowledge"
        if not d.is_dir():
            return
        for f in sorted(d.rglob("*")):
            if not f.is_file() or f.suffix not in (".md", ".json", ".txt"):
                continue
            content = ImportService._read_text(f)
            if content:
                rel = f.relative_to(root)
                extra = f"--- {rel} ---\n{content}"
                project.description = (project.description + "\n\n" + extra) if project.description else extra
        logger.info("导入 spec/knowledge/")

    @staticmethod
    def _import_memory(session, root: Path, project: Project):
        """导入 .specify/memory/ 的创作记忆文件。

        原版 `novel init` 创建项目时会将 tools/memory/ 复制到项目下的
        .specify/memory/，包含 constitution.md 和 personal-voice.md。
        """
        memory_dir = root / ".specify" / "memory"
        if not memory_dir.is_dir():
            return
        for f in sorted(memory_dir.iterdir()):
            if not f.is_file():
                continue
            content = ImportService._read_text(f)
            if content:
                rel = f.relative_to(root)
                extra = f"--- {rel} ---\n{content}"
                project.description = (project.description + "\n\n" + extra) if project.description else extra
        logger.info("导入 .specify/memory/")

    @staticmethod
    def _import_experts(session, root: Path, project: Project):
        """experts/ 是工具源码级知识库，不包含在用户项目中，无需导入。"""
        pass

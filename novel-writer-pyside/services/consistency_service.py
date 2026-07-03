"""一致性检查服务 - 规则引擎 + AI 深度检查。"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable
from models import Chapter, Character, ChapterAppearance, TimelineEvent
from models.database import db_manager
from core.ai.ai_worker import AIWorker
from core.ai.manager import ai_manager
from core.ai.prompts.registry import get_template
from core.ai.base import Message


@dataclass
class CheckResult:
    """单个检查结果。"""
    category: str          # 角色/时间线/情节
    severity: str          # error/warning/info
    message: str           # 简述
    detail: str = ""       # 详情
    chapter_id: Optional[int] = None  # 可跳转章节


class ConsistencyService:

    def run_rules(self, project_id: int) -> list[CheckResult]:
        """执行三类规则检查。"""
        results: list[CheckResult] = []

        results.extend(self._check_character_aliases(project_id))
        results.extend(self._check_character_appearance_before_creation(project_id))
        results.extend(self._check_timeline_order(project_id))

        return results

    def _check_character_aliases(self, project_id: int) -> list[CheckResult]:
        """角色别名冲突检测。"""
        results = []
        session = db_manager.get_project_session()
        try:
            chars = session.query(Character).filter(
                Character.is_deleted == 0,
            ).all()

            # 构建角色名 → 角色映射
            name_map: dict[str, Character] = {}
            for c in chars:
                name_map[c.name] = c
                if c.aliases:
                    for alias in c.aliases.split(","):
                        alias = alias.strip()
                        if alias:
                            name_map[alias] = c

            # 遍历章节，检查别名使用
            chapters = session.query(Chapter).filter(
                Chapter.is_deleted == 0,
            ).all()

            for ch in chapters:
                if not ch.content_plain:
                    continue
                for name, owner in name_map.items():
                    if name in ch.content_plain:
                        # 检查这个 name 是否属于本章应该出现的角色
                        # 简单策略：如果 name 在某个章节中，但不是该章节预期角色
                        appearances = session.query(ChapterAppearance).filter(
                            ChapterAppearance.chapter_id == ch.id,
                            ChapterAppearance.character_id == owner.id,
                        ).first()
                        if not appearances and name != ch.title:
                            # name 出现在非所属章节的内容中可能是别名冲突
                            result = CheckResult(
                                category="角色",
                                severity="warning",
                                message=f"章节「{ch.title}」可能使用了其他角色的别名",
                                detail=f"「{name}」是角色「{owner.name}」的名称/别名，"
                                       f"出现在第{ch.chapter_number}章",
                                chapter_id=ch.id,
                            )
                            results.append(result)
                            break
        finally:
            session.close()

        return results

    def _check_character_appearance_before_creation(self, project_id: int) -> list[CheckResult]:
        """角色出场前置检测。"""
        results = []
        session = db_manager.get_project_session()
        try:
            chars = session.query(Character).filter(
                Character.is_deleted == 0,
            ).all()

            for c in chars:
                appearances = session.query(ChapterAppearance).options(
                    ChapterAppearance.chapter
                ).filter(
                    ChapterAppearance.character_id == c.id,
                ).order_by(ChapterAppearance.id).all()

                if not appearances or not c.created_at:
                    continue

                for app in appearances:
                    if app.chapter and app.chapter.created_at:
                        if app.chapter.created_at < c.created_at:
                            results.append(CheckResult(
                                category="角色",
                                severity="error",
                                message=f"角色「{c.name}」在创建前就已出场",
                                detail=f"第{app.chapter.chapter_number}章「{app.chapter.title}」"
                                       f"中有该角色的出场记录，但角色创建时间更晚",
                                chapter_id=app.chapter_id,
                            ))
        finally:
            session.close()

        return results

    def _check_timeline_order(self, project_id: int) -> list[CheckResult]:
        """时间线排序检测。"""
        results = []
        session = db_manager.get_project_session()
        try:
            events = session.query(TimelineEvent).order_by(TimelineEvent.sort_order).all()

            for i in range(1, len(events)):
                prev = events[i - 1]
                curr = events[i]

                # 简单检测：如果 story_date 可解析为数字，检查排序
                prev_num = self._extract_number(prev.story_date)
                curr_num = self._extract_number(curr.story_date)

                if prev_num is not None and curr_num is not None:
                    if curr_num < prev_num:
                        results.append(CheckResult(
                            category="时间线",
                            severity="warning",
                            message=f"时间线排序可能异常",
                            detail=f"事件「{curr.event_name}」的日期序号({curr_num}) "
                                   f"小于前一个事件「{prev.event_name}」({prev_num})",
                            chapter_id=curr.chapter_id,
                        ))
        finally:
            session.close()

        return results

    def _extract_number(self, text: str) -> Optional[int]:
        """从文本中提取数字序号。"""
        import re
        if not text:
            return None
        match = re.search(r"(\d+)", text)
        if match:
            return int(match.group(1))
        return None

    def run_ai_check(self, project_id: int,
                     on_chunk: Callable[[str], None],
                     on_done: Callable[[], None],
                     on_error: Callable[[str], None]) -> Optional[AIWorker]:
        """AI 深度一致性检查。"""
        session = db_manager.get_project_session()
        try:
            # 获取项目所有章节内容摘要
            chapters = session.query(Chapter).filter(
                Chapter.is_deleted == 0,
            ).order_by(Chapter.chapter_number).all()

            content_summary = "\n".join(
                f"第{c.chapter_number}章 {c.title}:\n{(c.content_plain or '')[:500]}"
                for c in chapters
            )

            if not content_summary.strip():
                on_error("项目中没有章节内容")
                return None

            template = get_template("consistency_check")
            message_dicts = template.render({"content": content_summary})
            messages = [Message(**m) for m in message_dicts]

            config = ai_manager._create_config_from_active()

            worker = AIWorker(messages, config)
            worker.chunk_received.connect(on_chunk)
            worker.finished.connect(on_done)
            worker.error.connect(on_error)
            worker.start()
            return worker
        finally:
            session.close()


consistency_service = ConsistencyService()

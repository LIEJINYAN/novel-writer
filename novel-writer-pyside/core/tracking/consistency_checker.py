"""一致性检查器 - 规则引擎 + 深度一致性检查。

提供核心数据库逻辑，供 services/consistency_service.py 委托调用。
"""

from __future__ import annotations
from typing import Optional
from dataclasses import dataclass
from models import Chapter, Character, ChapterAppearance, TimelineEvent
from models.database import DatabaseManager


@dataclass
class CheckResult:
    """单个检查结果。"""
    category: str          # 角色/时间线/情节
    severity: str          # error/warning/info
    message: str           # 简述
    detail: str = ""       # 详情
    chapter_id: Optional[int] = None  # 可跳转章节


class ConsistencyChecker:
    """一致性检查器 - 执行规则检查和一致性验证。"""

    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager

    # ===== 全面检查 =====

    def check_all(self, project_id: int) -> list[CheckResult]:
        """执行所有一致性检查。"""
        results: list[CheckResult] = []
        results.extend(self.check_character_consistency(project_id))
        results.extend(self.check_relationship_consistency(project_id))
        results.extend(self.check_world_rules(project_id))
        return results

    # ===== 角色一致性 =====

    def check_character_consistency(self, project_id: int) -> list[CheckResult]:
        """角色一致性检查：别名冲突 + 出场前置检测。"""
        results: list[CheckResult] = []
        results.extend(self._check_character_aliases(project_id))
        results.extend(self._check_appearance_before_creation(project_id))
        return results

    def _check_character_aliases(self, project_id: int) -> list[CheckResult]:
        """角色别名冲突检测。"""
        results = []
        session = self._db.get_project_session()
        try:
            chars = session.query(Character).filter(
                Character.is_deleted == 0,
            ).all()

            name_map: dict[str, Character] = {}
            for c in chars:
                name_map[c.name] = c
                if c.aliases:
                    for alias in c.aliases.split(","):
                        alias = alias.strip()
                        if alias:
                            name_map[alias] = c

            chapters = session.query(Chapter).filter(
                Chapter.is_deleted == 0,
            ).all()

            for ch in chapters:
                if not ch.content_plain:
                    continue
                for name, owner in name_map.items():
                    if name in ch.content_plain:
                        appearances = session.query(ChapterAppearance).filter(
                            ChapterAppearance.chapter_id == ch.id,
                            ChapterAppearance.character_id == owner.id,
                        ).first()
                        if not appearances and name != ch.title:
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

    def _check_appearance_before_creation(self, project_id: int) -> list[CheckResult]:
        """角色出场前置检测。"""
        results = []
        session = self._db.get_project_session()
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

    # ===== 时间线一致性 =====

    def check_timeline_consistency(self, project_id: int) -> list[CheckResult]:
        """时间线排序检测。"""
        results = []
        session = self._db.get_project_session()
        try:
            events = session.query(TimelineEvent).order_by(
                TimelineEvent.sort_order
            ).all()

            for i in range(1, len(events)):
                prev = events[i - 1]
                curr = events[i]

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

    @staticmethod
    def _extract_number(text: str) -> Optional[int]:
        """从文本中提取数字序号。"""
        import re
        if not text:
            return None
        match = re.search(r"(\d+)", text)
        if match:
            return int(match.group(1))
        return None

    # ===== 关系一致性 =====

    def check_relationship_consistency(self, project_id: int) -> list[CheckResult]:
        """关系一致性检查（预留扩展）。"""
        return []

    # ===== 世界观规则 =====

    def check_world_rules(self, project_id: int) -> list[CheckResult]:
        """世界观规则检查（预留扩展）。"""
        return []

    # ===== 规则运行（旧接口兼容） =====

    def run_rules(self, project_id: int) -> list[CheckResult]:
        """执行所有规则检查（兼容旧接口）。"""
        results: list[CheckResult] = []
        results.extend(self.check_character_consistency(project_id))
        results.extend(self.check_timeline_consistency(project_id))
        return results

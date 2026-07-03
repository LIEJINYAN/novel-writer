"""写作方法转换器 - 在不同方法间调整章节结构。"""

from typing import Optional
from .base import WritingMethod
from .advisor import method_advisor


class MethodConverter:
    """方法转换器。"""

    @staticmethod
    def convert_chapters(chapters: list[dict], from_method: str,
                         to_method: str) -> dict[str, list[int]]:
        """将章节从源方法映射到目标方法。

        Args:
            chapters: 章节列表，[{'title': ..., 'content': ...}, ...]
            from_method: 源方法名称（如 "三幕式"）
            to_method: 目标方法名称（如 "英雄之旅"）
        Returns:
            dict: {target_stage_name: [chapter_indices]}
        """
        src = method_advisor.get_method(from_method)
        dst = method_advisor.get_method(to_method)

        if not src or not dst:
            raise ValueError(f"方法不存在: {from_method if not src else to_method}")

        total = len(chapters)
        if total == 0:
            return {s.name: [] for s in dst.stages}

        # 按源方法阶段比例分配
        src_stage_count = len(src.stages)
        src_assignments = {}
        for i, stage in enumerate(src.stages):
            start = int(total * i / src_stage_count)
            end = int(total * (i + 1) / src_stage_count)
            src_assignments[stage.name] = list(range(start, end))

        # 源章节索引 → 目标阶段映射
        dst_stage_count = len(dst.stages)
        result = {s.name: [] for s in dst.stages}

        # 逐个章节映射到目标阶段
        for ch_idx in range(total):
            # 该章节在源方法中的进度比例
            progress = ch_idx / max(total, 1)
            # 对应目标阶段的索引
            dst_idx = min(int(progress * dst_stage_count), dst_stage_count - 1)
            dst_stage_name = dst.stages[dst_idx].name
            result[dst_stage_name].append(ch_idx)

        return result

    @staticmethod
    def suggest_reassignment(chapter_title: str, from_stage: str,
                             to_stage: str) -> str:
        """为章节迁移提供建议。"""
        suggestions = {
            ("第一幕", "平凡世界"): "开篇章节适合作为英雄之旅的平凡世界世界阶段",
            ("对抗", "考验"): "冲突章节适合映射到英雄之旅的历练阶段",
            ("结局", "复活"): "高潮章节适合作为英雄之旅的重生转折",
        }
        key = (from_stage, to_stage)
        return suggestions.get(key, f"章节「{chapter_title}」从「{from_stage}」迁移到「{to_stage}」")

    @staticmethod
    def get_conversion_summary(chapters: list[dict], from_method: str,
                               to_method: str) -> str:
        """生成转换摘要。"""
        mapping = MethodConverter.convert_chapters(chapters, from_method, to_method)
        dst = method_advisor.get_method(to_method)

        lines = [f"转换方法: {from_method} → {to_method}", f"总章节: {len(chapters)}章", ""]
        for stage in dst.stages:
            indices = mapping.get(stage.name, [])
            titles = [f"「{chapters[i]['title']}」" for i in indices if i < len(chapters)]
            lines.append(f"【{stage.name}】({len(indices)}章)")
            if titles:
                lines.append("  " + ", ".join(titles))
            lines.append("")

        return "\n".join(lines)


# 全局实例
method_converter = MethodConverter()

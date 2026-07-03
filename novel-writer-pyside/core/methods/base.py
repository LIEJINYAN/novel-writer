"""写作方法基类。"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MethodStage:
    """写作方法的一个阶段。"""
    name: str                      # 阶段名称（如"建置"）
    order: int                     # 顺序
    description: str               # 描述
    min_chapters: int = 1          # 最少章节数
    max_chapters: Optional[int] = None  # 最多章节数（None = 不限）
    color: str = "#7aa2f7"         # 对应颜色（用于 UI 显示）


class WritingMethod:
    """写作方法基类。"""
    
    name: str = ""                        # 方法名称
    description: str = ""                 # 方法描述
    stages: list[MethodStage] = []        # 阶段列表
    compatible_genres: list[str] = []     # 兼容的小说类型
    suitable_for: list[str] = []          # 适合的场景
    
    def analyze_outline(self, chapters: list[dict]) -> dict:
        """分析已有章节，返回各阶段的映射。
        
        Args:
            chapters: 章节列表，每个为 dict 含 title, content, order
        Returns:
            dict: {stage_name: [chapter_ids]}
        """
        total = len(chapters)
        result = {}
        stage_count = len(self.stages)
        
        if stage_count == 0 or total == 0:
            return result
        
        # 按比例分配章节到各个阶段
        for i, stage in enumerate(self.stages):
            start = int(total * i / stage_count)
            end = int(total * (i + 1) / stage_count)
            result[stage.name] = list(range(start, end))
        
        return result
    
    def get_stage_for_chapter(self, chapter_index: int, total_chapters: int) -> Optional[MethodStage]:
        """根据章节索引获取对应的方法阶段。"""
        stage_count = len(self.stages)
        if stage_count == 0:
            return None
        idx = min(int(chapter_index * stage_count / max(total_chapters, 1)), stage_count - 1)
        return self.stages[idx] if 0 <= idx < stage_count else None
    
    def suggest_chapter(self, stage_name: str) -> str:
        """为指定阶段建议章节内容。
        
        Args:
            stage_name: 阶段名称
        Returns:
            str: 建议描述
        """
        for stage in self.stages:
            if stage.name == stage_name:
                return stage.description
        return ""

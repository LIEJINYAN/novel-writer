"""写作方法推荐器。"""

from dataclasses import dataclass, field
from typing import Optional
from .base import WritingMethod
from .three_act import ThreeActMethod
from .hero_journey import HeroJourneyMethod
from .seven_point import SevenPointMethod


@dataclass
class Recommendation:
    """方法推荐结果。"""
    method_name: str                     # 方法名称
    score: int                           # 推荐分数 (0-100)
    reasons: list[str] = field(default_factory=list)  # 推荐理由


class MethodAdvisor:
    """写作方法推荐器。"""

    def __init__(self):
        self._methods: dict[str, WritingMethod] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """注册默认方法。"""
        for method in [ThreeActMethod(), HeroJourneyMethod(), SevenPointMethod()]:
            self._methods[method.name] = method
    
    def register(self, method: WritingMethod):
        """注册新方法。"""
        self._methods[method.name] = method
    
    def list_methods(self) -> list[str]:
        """列出所有已注册的方法名称。"""
        return list(self._methods.keys())
    
    def get_method(self, name: str) -> Optional[WritingMethod]:
        """获取指定方法。"""
        return self._methods.get(name)
    
    def recommend(self, genre: str = "", experience: str = "新手",
                  length: str = "长篇") -> list[Recommendation]:
        """推荐写作方法。
        
        Args:
            genre: 小说类型（玄幻/都市/言情/悬疑/科幻/历史/武侠等）
            experience: 用户经验（新手/进阶/资深）
            length: 目标篇幅（短篇/中篇/长篇）
        Returns:
            list[Recommendation]: 按分数降序排列的推荐列表
        """
        results = []
        for method in self._methods.values():
            score = self._calculate_score(method, genre, experience, length)
            reasons = self._get_reasons(method, genre, experience, length)
            results.append(Recommendation(method.name, score, reasons))
        
        # 按分数降序排列
        results.sort(key=lambda r: r.score, reverse=True)
        return results
    
    def _calculate_score(self, method: WritingMethod, genre: str,
                         experience: str, length: str) -> int:
        """计算方法的推荐分数。"""
        score = 50  # 基础分
        
        # 类型匹配 (+0~20)
        if genre and genre in method.compatible_genres:
            score += 20
        elif genre:
            # 部分兼容（类型在同一大类）
            broad_categories = {
                "玄幻": ["奇幻", "武侠", "仙侠"],
                "都市": ["言情", "现实"],
                "言情": ["都市", "青春"],
                "科幻": ["奇幻", "悬疑"],
                "悬疑": ["科幻", "都市"],
                "历史": ["武侠", "奇幻"],
                "武侠": ["玄幻", "历史", "仙侠"],
            }
            related = broad_categories.get(genre, [])
            if any(r in method.compatible_genres for r in related):
                score += 10
        
        # 经验匹配 (+0~15)
        if not experience:
            pass
        elif experience == "新手":
            if "新手" in method.suitable_for:
                score += 15
            elif "入门" in method.suitable_for:
                score += 10
        elif experience == "进阶":
            score += 5
        elif experience == "资深":
            if "进阶" in method.suitable_for or "资深" in method.suitable_for:
                score += 5
        
        # 篇幅匹配 (+0~15)
        stage_count = len(method.stages)
        if length == "短篇" and stage_count <= 5:
            score += 15
        elif length == "中篇" and 4 <= stage_count <= 8:
            score += 10
        elif length == "长篇" and stage_count >= 4:
            score += 15
        
        return min(score, 100)
    
    def _get_reasons(self, method: WritingMethod, genre: str,
                     experience: str, length: str) -> list[str]:
        """生成推荐理由。"""
        reasons = []
        
        if genre and genre in method.compatible_genres:
            reasons.append(f"适合 {genre} 类型")
        
        if not experience:
            pass
        elif experience == "新手" and "新手" in method.suitable_for:
            reasons.append("适合新手作者")
        
        if length == "短篇" and len(method.stages) <= 5:
            reasons.append(f"{len(method.stages)} 个阶段适合短篇节奏")
        elif length == "长篇" and len(method.stages) >= 4:
            reasons.append(f"{len(method.stages)} 个阶段保证长篇结构完整")
        
        if not reasons:
            reasons.append("通用写作方法")
        
        return reasons


# 全局实例
method_advisor = MethodAdvisor()

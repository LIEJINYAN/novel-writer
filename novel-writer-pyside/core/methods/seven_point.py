"""七点故事结构写作方法。"""

from .base import WritingMethod, MethodStage


class SevenPointMethod(WritingMethod):
    """七点故事结构 - Dan Wells 提出的简洁结构。"""
    
    name = "七点结构"
    description = "Dan Wells 提出的简洁故事结构，七个关键节点构成完整故事弧线，适合中短篇和节奏紧凑的作品。"
    compatible_genres = ["悬疑", "都市", "言情", "科幻", "玄幻"]
    suitable_for = ["中短篇", "节奏紧凑的故事", "快速创作"]
    
    stages = [
        MethodStage("1. 钩子", 0, "主角的初始状态，展示其性格、处境和渴望。", 1, 2, "#7aa2f7"),
        MethodStage("2. 转折点①", 1, "激励事件，打破主角的日常生活，迫使其开始行动。", 1, 1, "#bb9af7"),
        MethodStage("3. 推进", 2, "主角开始追逐目标，经历各种挑战，逐步成长。", 2, 4, "#f7768e"),
        MethodStage("4. 中点", 3, "故事的重要转折，主角从被动转为主动，或发现关键信息。", 1, 2, "#e0af68"),
        MethodStage("5. 推进（后半）", 4, "主角更加主动，但困难也越来越大，一切似乎要崩塌。", 2, 3, "#f7768e"),
        MethodStage("6. 转折点②", 5, "最黑暗的时刻，主角失去一切希望，但最终找到突破口。", 1, 1, "#bb9af7"),
        MethodStage("7. 结局", 6, "最终的高潮与解决，主角成功或失败，展示变化。", 1, 2, "#9ece6a"),
    ]

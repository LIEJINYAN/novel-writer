"""三幕式结构写作方法。"""

from .base import WritingMethod, MethodStage


class ThreeActMethod(WritingMethod):
    """三幕式结构 - 最经典的小说结构。"""
    
    name = "三幕式"
    description = "最经典的小说结构，将故事分为建置、对抗、结局三大部分，适合绝大多数小说类型。"
    compatible_genres = ["玄幻", "都市", "言情", "历史", "科幻", "悬疑", "武侠"]
    suitable_for = ["新手作者", "主流网文", "商业写作"]
    
    stages = [
        MethodStage("第一幕 - 建置", 0,
                    "建立世界观，介绍主角和日常生活，出现激励事件打破平衡，主角踏上旅程。", 2, 5, "#7aa2f7"),
        MethodStage("第二幕 - 对抗（前半）", 1,
                    "主角适应新世界，结识盟友/敌人，经历一系列考验，逐步成长。", 3, 8, "#bb9af7"),
        MethodStage("第二幕 - 对抗（后半）", 2,
                    "主角遭遇重大挫折或转折，面临最艰难的选择，为最终对抗做准备。", 3, 8, "#f7768e"),
        MethodStage("第三幕 - 结局", 3,
                    "最终对抗，解决核心冲突，展示主角的成长，收尾和余韵。", 2, 5, "#9ece6a"),
    ]

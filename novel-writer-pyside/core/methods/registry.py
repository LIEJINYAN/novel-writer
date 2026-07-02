"""写作方法论 - 方法定义与结构信息。"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class PlotNode:
    """情节节点定义。"""
    name: str
    description: str
    chapter_range: str  # 如 "1%-25%"
    order: int


@dataclass
class WritingMethodDef:
    """写作方法定义。"""
    id: str
    name: str
    description: str
    suitable_genres: List[str]
    suitable_length: str
    difficulty: str
    plot_nodes: List[PlotNode]
    tips: List[str]


# ========== 方法定义 ==========

THREE_ACT = WritingMethodDef(
    id="three-act",
    name="三幕结构",
    description="经典的故事结构，分为开端、中段、结尾三部分，适合大多数小说类型",
    suitable_genres=["通用", "现实", "爱情", "历史"],
    suitable_length="5万-50万字",
    difficulty="初级",
    plot_nodes=[
        PlotNode("开场", "介绍主角和世界观", "1%-5%", 1),
        PlotNode("激励事件", "打破平衡，故事正式开始", "5%-10%", 2),
        PlotNode("第一幕转折点", "主角做出关键决定", "22%-28%", 3),
        PlotNode("次要情节", "展开支线故事", "30%-45%", 4),
        PlotNode("中点转折", "故事发生重大变化", "48%-52%", 5),
        PlotNode("第二幕转折点", "主角面临最大挑战", "70%-75%", 6),
        PlotNode("高潮前奏", "为高潮铺垫", "85%-90%", 7),
        PlotNode("高潮", "故事最紧张的时刻", "90%-95%", 8),
        PlotNode("结局", "收束所有线索", "95%-100%", 9),
    ],
    tips=[
        "第一幕要快速抓人，5000字内抛出钩子",
        "第二幕是最长的部分，需要有足够的冲突和转折",
        "第三幕要紧凑有力，不要草草收尾",
    ],
)

HERO_JOURNEY = WritingMethodDef(
    id="hero-journey",
    name="英雄之旅",
    description="12阶段的英雄成长之旅，适合奇幻、史诗类作品",
    suitable_genres=["奇幻", "科幻", "冒险", "成长"],
    suitable_length="10万-100万字",
    difficulty="高级",
    plot_nodes=[
        PlotNode("平凡世界", "展现主角普通生活", "1%-5%", 1),
        PlotNode("冒险召唤", "打破平静的契机", "5%-8%", 2),
        PlotNode("拒绝召唤", "主角犹豫和退缩", "8%-10%", 3),
        PlotNode("遇见导师", "获得指引和帮助", "10%-15%", 4),
        PlotNode("跨越门槛", "进入非凡世界", "15%-20%", 5),
        PlotNode("考验盟友敌人", "适应新世界的挑战", "20%-40%", 6),
        PlotNode("深入虎穴", "接近最危险的区域", "40%-50%", 7),
        PlotNode("严峻考验", "面临最大的危机", "50%-55%", 8),
        PlotNode("获得奖赏", "取得重要成果", "55%-65%", 9),
        PlotNode("返回之路", "带着成果回归", "65%-80%", 10),
        PlotNode("复活重生", "最终考验和蜕变", "80%-95%", 11),
        PlotNode("带着宝物归来", "回归平凡世界，但已改变", "95%-100%", 12),
    ],
    tips=[
        "英雄之旅强调角色的内在成长，需要加强心理描写",
        "每个阶段都要有明确的事件推动",
        "导师可以在关键时刻再次出现",
    ],
)

STORY_CIRCLE = WritingMethodDef(
    id="story-circle",
    name="故事圈",
    description="8环节的循环结构，强调角色从舒适区出发到成长归来的循环",
    suitable_genres=["角色", "心理", "成长", "系列"],
    suitable_length="3万-20万字",
    difficulty="中级",
    plot_nodes=[
        PlotNode("舒适区", "主角在熟悉的环境", "1%-10%", 1),
        PlotNode("想要的东西", "主角渴望改变", "10%-15%", 2),
        PlotNode("进入新环境", "被迫或主动离开舒适区", "15%-25%", 3),
        PlotNode("适应过程", "努力适应新环境", "25%-45%", 4),
        PlotNode("得到想要的", "获得最初渴望的东西", "45%-55%", 5),
        PlotNode("付出代价", "为获得付出沉重代价", "55%-75%", 6),
        PlotNode("回到舒适区", "带着改变归来", "75%-90%", 7),
        PlotNode("彻底改变", "已经不再是原来的自己", "90%-100%", 8),
    ],
    tips=[
        "每个环节都要推进角色的内心变化",
        "循环结构可以嵌套使用，形成多层故事",
        "代价环节的力度决定了故事的深度",
    ],
)

SEVEN_POINT = WritingMethodDef(
    id="seven-point",
    name="七点结构",
    description="7个关键节点构成的紧凑情节结构，适合悬疑、动作类作品",
    suitable_genres=["悬疑", "惊悚", "动作", "商业"],
    suitable_length="5万-30万字",
    difficulty="初级",
    plot_nodes=[
        PlotNode("主角现状", "主角在故事开始时的状态", "1%-10%", 1),
        PlotNode("触发事件", "打破现状的导火索", "10%-15%", 2),
        PlotNode("一路前行", "主角开始行动，遇到挑战", "15%-40%", 3),
        PlotNode("中点转折", "从被动转为主动，或反之", "45%-55%", 4),
        PlotNode("困难重重", "主角遭遇最大挫折", "55%-70%", 5),
        PlotNode("绝地反击", "主角找到解决方法", "70%-85%", 6),
        PlotNode("最终结局", "故事收尾，主角改变", "85%-100%", 7),
    ],
    tips=[
        "七点结构需要明确的节奏控制点",
        "中点转折是故事最重要的分水岭",
        "每个节点之间要有递进的紧张感",
    ],
)

PIXAR_FORMULA = WritingMethodDef(
    id="pixar-formula",
    name="皮克斯公式",
    description="简单有力的故事公式，适合短篇、儿童文学和温情故事",
    suitable_genres=["儿童", "短篇", "温情", "寓言"],
    suitable_length="0.5万-5万字",
    difficulty="初级",
    plot_nodes=[
        PlotNode("从前...", "设定时间和背景", "1%-10%", 1),
        PlotNode("每天...", "展现日常生活", "10%-20%", 2),
        PlotNode("有一天...", "发生改变命运的事件", "20%-30%", 3),
        PlotNode("因为...", "主角做出决定的原因", "30%-40%", 4),
        PlotNode("因为...", "行动带来的后果", "40%-55%", 5),
        PlotNode("直到...", "故事出现转机", "55%-75%", 6),
        PlotNode("最后...", "故事的结局", "75%-90%", 7),
        PlotNode("从此...", "主角的成长和变化", "90%-100%", 8),
    ],
    tips=[
        "简单就是力量，不要添加过多的支线",
        "情感核心最重要，确定故事要传达的情绪",
        "适合用口头讲述的方式写，保持流畅自然",
    ],
)

FREESTYLE = WritingMethodDef(
    id="freestyle",
    name="自由模式",
    description="无固定结构，自由创作，适合有经验的作者或实验性作品",
    suitable_genres=["通用"],
    suitable_length="不限",
    difficulty="任意",
    plot_nodes=[
        PlotNode("自由创作", "没有固定结构限制", "0%-100%", 1),
    ],
    tips=[
        "自由模式需要较强的结构和节奏掌控能力",
        "建议在写作完成后进行结构性修改",
        "可以参考其他方法灵活组合使用",
    ],
)

SNOWFLAKE = WritingMethodDef(
    id="snowflake",
    name="雪花十步法",
    description="Randy Ingermanson 提出的递进式构建方法，从一句话逐步扩展到完整小说，适合长篇复杂故事",
    suitable_genres=["长篇史诗", "复杂结构", "多线索", "推理"],
    suitable_length="20万-100万字以上",
    difficulty="中级",
    plot_nodes=[
        PlotNode("一句话概述", "用 15 字以内概括核心故事", "0%-2%", 1),
        PlotNode("一段话扩展", "包含设置、冲突、高潮、结局的完整段落", "2%-5%", 2),
        PlotNode("角色概述", "每个主要角色的一页描述（目标、动机、冲突）", "5%-10%", 3),
        PlotNode("故事扩展", "将一段话扩展为一页（5 段：设置-进展-中点-高潮-结局）", "10%-15%", 4),
        PlotNode("角色详述", "每个角色扩展为完整背景故事", "15%-20%", 5),
        PlotNode("四页大纲", "将每段再扩展为一页，形成四页大纲", "20%-30%", 6),
        PlotNode("角色表格", "详细角色档案，包括关系网和成长弧线", "30%-40%", 7),
        PlotNode("场景列表", "每章/每场景一行描述，梳理完整时序", "40%-55%", 8),
        PlotNode("场景详述", "每个场景扩展为多段详细描写", "55%-75%", 9),
        PlotNode("初稿写作", "根据详细大纲正式开始写作", "75%-100%", 10),
    ],
    tips=[
        "前 5 步做足准备后再动笔，减少写作中的迷茫",
        "不必严格遵守所有步骤，可根据需要调整顺序",
        "适合多线索、多角色的复杂长篇故事",
        "从一句话到完整小说，每一步都是前一步的递进扩展",
    ],
)

# 方法注册表
METHOD_REGISTRY: Dict[str, WritingMethodDef] = {
    "three-act": THREE_ACT,
    "hero-journey": HERO_JOURNEY,
    "story-circle": STORY_CIRCLE,
    "seven-point": SEVEN_POINT,
    "pixar-formula": PIXAR_FORMULA,
    "snowflake": SNOWFLAKE,
    "freestyle": FREESTYLE,
}


def get_method(method_id: str) -> Optional[WritingMethodDef]:
    """获取方法定义。"""
    return METHOD_REGISTRY.get(method_id)


def list_methods() -> List[WritingMethodDef]:
    """列出所有方法。"""
    return list(METHOD_REGISTRY.values())


def list_method_choices() -> List[tuple]:
    """列出方法选择选项（用于 UI 下拉框）。"""
    return [
        ("three-act", "三幕结构 (Three-Act) - 经典故事结构"),
        ("hero-journey", "英雄之旅 (Hero's Journey) - 12阶段成长之旅"),
        ("story-circle", "故事圈 (Story Circle) - 8环节循环结构"),
        ("seven-point", "七点结构 (Seven Point) - 紧凑情节结构"),
        ("pixar-formula", "皮克斯公式 (Pixar Formula) - 简单有力"),
        ("snowflake", "雪花十步法 (Snowflake) - 系统化规划"),
        ("freestyle", "自由模式 - 无固定结构"),
    ]

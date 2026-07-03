"""雪花十步法写作方法。"""

from .base import WritingMethod, MethodStage


class SnowflakeMethod(WritingMethod):
    """雪花十步法 - Randy Ingermanson 提出的递进式构建方法。"""

    name = "雪花十步法"
    description = "Randy Ingermanson 提出的系统化写作方法，从一句话逐步扩展到完整小说，递进式构建适合复杂长篇故事。"
    compatible_genres = ["玄幻", "奇幻", "科幻", "推理", "历史"]
    suitable_for = ["长篇史诗", "复杂多线索故事", "系统化创作者"]

    stages = [
        MethodStage("1. 一句话概述", 0,
                    "用 15 字以内概括核心故事，一句话就能让人感兴趣。", 1, 1, "#7aa2f7"),
        MethodStage("2. 一段话扩展", 1,
                    "将一句话扩展为包含设置、冲突、高潮、结局的完整段落。", 1, 1, "#7aa2f7"),
        MethodStage("3. 角色概述", 2,
                    "每个主要角色的一页描述，包含目标、动机、冲突。", 1, 2, "#bb9af7"),
        MethodStage("4. 故事扩展", 3,
                    "将一段话扩展为一页（五段：设置、进展、中点、高潮、结局）。", 1, 1, "#bb9af7"),
        MethodStage("5. 角色详述", 4,
                    "每个角色扩展为完整背景故事，深入挖掘。", 1, 2, "#bb9af7"),
        MethodStage("6. 四页大纲", 5,
                    "将每段再扩展为一页，形成四页的完整大纲。", 1, 2, "#f7768e"),
        MethodStage("7. 角色表格", 6,
                    "详细角色档案，包括关系网和成长弧线。", 1, 2, "#f7768e"),
        MethodStage("8. 场景列表", 7,
                    "每章/每场景一行描述，梳理完整时序和节奏。", 2, 3, "#e0af68"),
        MethodStage("9. 场景详述", 8,
                    "每个场景扩展为多段详细描写，完善细节。", 2, 4, "#e0af68"),
        MethodStage("10. 初稿写作", 9,
                    "根据详细大纲正式开始写作，逐章推进。", 5, 30, "#9ece6a"),
    ]

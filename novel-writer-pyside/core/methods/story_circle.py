"""故事圈写作方法。"""

from .base import WritingMethod, MethodStage


class StoryCircleMethod(WritingMethod):
    """故事圈 - Dan Harmon 提出的8环节循环结构。"""

    name = "故事圈"
    description = "Dan Harmon 提出的8环节循环结构，强调角色从舒适区出发到成长归来的完整循环，适合角色驱动型故事。"
    compatible_genres = ["都市", "言情", "成长", "奇幻", "科幻"]
    suitable_for = ["角色驱动型故事", "系列作品", "中短篇"]

    stages = [
        MethodStage("1. 舒适区", 0,
                    "主角在熟悉的环境中，展现其日常生活的状态。", 1, 2, "#7aa2f7"),
        MethodStage("2. 想要的东西", 1,
                    "主角内心渴望改变或获得某样东西，但尚未行动。", 1, 1, "#7aa2f7"),
        MethodStage("3. 进入新环境", 2,
                    "主角被迫或主动离开舒适区，进入一个陌生的世界。", 1, 2, "#bb9af7"),
        MethodStage("4. 适应过程", 3,
                    "主角努力适应新环境，结识新的人，学习新的规则。", 2, 4, "#f7768e"),
        MethodStage("5. 得到想要的", 4,
                    "主角获得最初渴望的东西/达成目标，但发现这并非终点。", 1, 2, "#e0af68"),
        MethodStage("6. 付出代价", 5,
                    "主角为获得成功付出沉重代价，失去重要的东西。", 1, 3, "#f7768e"),
        MethodStage("7. 回到舒适区", 6,
                    "主角带着改变回到最初的环境，世界已不同。", 1, 2, "#bb9af7"),
        MethodStage("8. 彻底改变", 7,
                    "主角已经不再是原来的自己，完成了真正的转变。", 1, 2, "#9ece6a"),
    ]

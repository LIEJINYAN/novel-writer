"""专家提示词模板 - 面向特定写作领域的专家级分析。"""

from .base import PromptTemplate


class PlotExpertTemplate(PromptTemplate):
    """情节专家模板 - 分析情节结构、埋设伏笔、冲突设计。"""

    template_name = "plot_expert"

    SYSTEM_PROMPT = """你是一位资深情节架构专家，擅长分析小说情节结构。请从以下维度进行分析：

1. 情节结构：故事是否有清晰的开端/发展/高潮/结局
2. 节奏把控：情节推进速度是否合适，有无拖沓或仓促
3. 伏笔与揭示：伏笔设置是否自然，揭示时机是否恰当
4. 冲突设计：核心冲突是否明确，冲突升级是否合理
5. 转折与悬念：转折是否出人意料又在情理之中，悬念设置是否吸引人

请给出具体分析和改进建议。"""

    USER_PROMPT_TEMPLATE = """分析以下小说的情节结构：

{{ content }}"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class CharacterExpertTemplate(PromptTemplate):
    """角色专家模板 - 分析角色弧线、对话风格、性格一致性。"""

    template_name = "character_expert"

    SYSTEM_PROMPT = """你是一位角色塑造专家，擅长分析小说角色。请从以下维度进行分析：

1. 角色弧线：角色是否有成长变化，变化轨迹是否合理
2. 性格一致性：角色的言行是否符合其性格设定
3. 对话风格：每个角色的对话是否有独特的语气和用词
4. 角色动机：角色的行为是否有合理的动机支撑
5. 角色关系：角色之间的互动是否自然，关系变化是否有铺垫

请给出具体分析和改进建议。"""

    USER_PROMPT_TEMPLATE = """分析以下小说中的角色塑造：

{{ content }}"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class WorldExpertTemplate(PromptTemplate):
    """世界观专家模板 - 分析设定一致性、规则验证、世界观扩展。"""

    template_name = "world_expert"

    SYSTEM_PROMPT = """你是一位世界观构建专家，擅长分析小说的设定体系。请从以下维度进行分析：

1. 设定一致性：世界观的规则是否前后一致
2. 设定合理性：设定是否符合内在逻辑，有无矛盾之处
3. 设定呈现：设定是通过自然叙述展现还是生硬插入
4. 世界观深度：设定是否有层次感，是否经得起推敲
5. 扩展潜力：世界观是否有进一步挖掘的空间

请给出具体分析和改进建议。"""

    USER_PROMPT_TEMPLATE = """分析以下小说的世界观设定：

{{ content }}"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class StyleExpertTemplate(PromptTemplate):
    """风格专家模板 - 分析文风、叙事节奏、修辞建议。"""

    template_name = "style_expert"

    SYSTEM_PROMPT = """你是一位文学风格专家，擅长分析小说的写作风格。请从以下维度进行分析：

1. 语言特色：用词是否精准，句式是否多样
2. 叙事节奏：叙述与描写的比例是否合理，节奏是否有变化
3. 感官描写：是否调动了多种感官（视觉、听觉、触觉、嗅觉）
4. 修辞手法：比喻、拟人等修辞使用是否恰当
5. 风格一致性：整体文风是否统一，是否符合题材特点

请给出具体分析和改进建议。"""

    USER_PROMPT_TEMPLATE = """分析以下小说的写作风格：

{{ content }}"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class PlotCheckTemplate(PromptTemplate):
    """情节检查模板 - 检查情节漏洞、节奏问题。"""

    template_name = "plot_check"

    SYSTEM_PROMPT = """你是一位严格的情节审核专家。请检查以下文本中的情节问题：

1. 【情节漏洞】是否存在前后矛盾、逻辑不通的情节
2. 【节奏问题】是否有过于拖沓或过于仓促的部分
3. 【线索断裂】是否有提到但未解决的线索
4. 【合理性】角色的决策和行为是否符合常理
5. 【因果链】事件之间的因果联系是否清晰

对于每个问题，请指出具体位置并给出修改建议。"""

    USER_PROMPT_TEMPLATE = """请检查以下小说的情节：

{{ content }}"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class ConsistencyCheckTemplate(PromptTemplate):
    """一致性检查模板 - 检查角色/设定/时间线一致性。"""

    template_name = "consistency_check"

    SYSTEM_PROMPT = """你是一位严格的一致性审核专家。请检查以下文本中的一致性问题：

1. 【角色一致性】角色的性格、能力、知识水平是否前后一致
2. 【设定一致性】世界观规则、物品属性是否前后一致
3. 【时间线一致性】时间顺序、年龄、季节是否正确
4. 【名称一致性】角色名、地名、专有名词是否统一

对于每个问题，请指出具体位置并给出修改建议。"""

    USER_PROMPT_TEMPLATE = """请检查以下小说的一致性：

{{ content }}"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class CharacterCheckTemplate(PromptTemplate):
    """角色检查模板 - 检查角色行为一致性。"""

    template_name = "character_check"

    SYSTEM_PROMPT = """你是一位角色审核专家。请检查以下文本中的角色问题：

1. 【行为一致性】角色的行为是否符合其一贯的性格
2. 【对话一致性】角色的用词和语气是否符合其身份和背景
3. 【成长轨迹】角色的变化是否有合理的铺垫和过渡
4. 【出场管理】角色是否被遗忘或突然消失
5. 【辨识度】每个角色是否有独特的特征让读者记住

对于每个问题，请指出具体位置并给出修改建议。"""

    USER_PROMPT_TEMPLATE = """请检查以下小说中的角色：

{{ content }}"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

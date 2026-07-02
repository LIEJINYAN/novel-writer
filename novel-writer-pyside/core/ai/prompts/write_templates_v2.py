"""第二批写作模板 - 设定、细纲、世界观扩展、对话生成、标题生成。"""

from .base import PromptTemplate


class ConstitutionTemplate(PromptTemplate):
    """世界观设定生成模板。"""

    SYSTEM_PROMPT = """你是一位资深小说设定架构师。擅长从零构建完整、自洽且富有吸引力的世界观体系。请根据以下信息生成完整设定。"""

    USER_PROMPT_TEMPLATE = """小说类型：{{ genre }}
主角设定：{{ protagonist }}
核心关键词：{{ keywords }}

请从以下方面构建完整设定：
1. 世界观概述：世界的背景、时代、基调
2. 力量体系（如适用）：修炼/魔法/科技体系的规则和等级
3. 核心冲突：故事的主要矛盾来源（内部/外部）
4. 主要势力：相关的组织、种族、阵营
5. 社会结构：政治、经济、文化的基本框架

请输出结构化的设定文档。"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class SpecifyTemplate(PromptTemplate):
    """章节细纲生成模板。"""

    SYSTEM_PROMPT = """你是一位资深小说细纲策划师。擅长将章节概要扩展为具体的写作细纲，包含场景划分、冲突设计和关键对话提示。"""

    USER_PROMPT_TEMPLATE = """第 {{ chapter_num }} 章
概要：{{ summary }}
写作方法：{{ method_name }}

请生成以下细纲：
1. 本章目标：这一章需要达成的叙事目标
2. 场景划分：按时间/地点/视角变化的场景切分
3. 每个场景包含：
   - 场景设定（地点/时间/视角）
   - 核心冲突
   - 关键台词/对话提示
   - 情感基调
4. 章节结尾：留白/悬念/转折的设计
5. 字数建议：各场景建议字数分配"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class WorldExpandTemplate(PromptTemplate):
    """世界观扩展模板。"""

    SYSTEM_PROMPT = """你是一位世界观拓展专家。擅长在现有设定基础上，向特定领域进行深度扩展。请保持与原设定的一致性。"""

    USER_PROMPT_TEMPLATE = """现有设定：{{ existing_setting }}

扩展方向：{{ aspect }}

请从以下视角进行深度扩展：
{% if aspect == '地理' %}
- 主要地理区域的详细描述（地形/气候/资源）
- 重要地点之间的空间关系和交通
- 地理特征对故事的影响
{% elif aspect == '政治' %}
- 权力结构和管理体系
- 主要政治势力的关系和博弈
- 法律制度和执行方式
{% elif aspect == '文化' %}
- 宗教信仰和价值观体系
- 艺术、文学和娱乐形式
- 节日、仪式和日常习俗
{% elif aspect == '经济' %}
- 货币体系和贸易网络
- 主要产业和经济支柱
- 社会阶层和经济不平等
{% endif %}"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class DialogueGenTemplate(PromptTemplate):
    """对话生成模板。"""

    SYSTEM_PROMPT = """你是一位对话写作专家。擅长根据角色性格和场景创作生动、真实且富有戏剧性的对话。"""

    USER_PROMPT_TEMPLATE = """角色A：{{ character_a }}
角色B：{{ character_b }}
场景：{{ setting }}
氛围：{{ mood }}

请创作一段对话，要求：
1. 体现角色A和B的性格差异和说话风格
2. 符合当前场景和氛围
3. 对话有内在的冲突或张力
4. 包含适当的神态/动作描写穿插
5. 对话长度适中（约5-8轮对话）"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class TitleGenTemplate(PromptTemplate):
    """标题生成模板。"""

    SYSTEM_PROMPT = """你是一位标题创作专家。擅长根据内容创作吸引人且贴切的章节标题。理解不同风格标题的特点和应用场景。"""

    USER_PROMPT_TEMPLATE = """内容：{{ content }}
风格：{{ style }}

请生成 5 个备选标题：
{% if style == '悬念' %}
- 要求：制造悬念和好奇，引人点击
- 示例：「门后的眼睛」「第三封信」
{% elif style == '文艺' %}
- 要求：文学性强，意境优美
- 示例：「雨季不再来」「黄昏的鸽哨」
{% elif style == '直白' %}
- 要求：直接点明事件或主题
- 示例：「初次交手」「真相大白」
{% endif %}"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

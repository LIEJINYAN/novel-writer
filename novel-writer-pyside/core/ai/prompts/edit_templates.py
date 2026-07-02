"""编辑相关提示词模板：润色、重写、分析。"""
from .base import PromptTemplate


class PolishTemplate(PromptTemplate):
    """AI 润色模板。"""

    template_name = "polish"

    SYSTEM_PROMPT = """你是一位资深文学编辑，擅长小说文本润色。你的任务是在保持原意的前提下优化表达、修正语病、改善节奏。

润色风格说明：
- 简洁：删减冗余，使表达更精炼
- 优美：提升文采，使用更生动的词汇和修辞
- 正式：使用更规范和正式的表达
- 口语化：使表达更接近日常对话

请直接输出润色后的文本，不要添加任何说明、前缀或后缀。
{% if anti_ai %}
{{ anti_ai }}
{% endif %}"""

    USER_PROMPT_TEMPLATE = """请按「{{ style }}」风格润色以下文本：

{{ text }}"""

    def render(self, context: dict) -> list:
        system_content = self._render_template(self.SYSTEM_PROMPT, context)
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class RewriteTemplate(PromptTemplate):
    """AI 重写模板。"""

    template_name = "rewrite"

    SYSTEM_PROMPT = """你是一位专业的小说重写助手。你的任务是根据指定的改写方向，对文本进行重写。

改写方向说明：
- 扩写：在原有基础上丰富细节、对话、描写和环境渲染
- 缩写：保留核心信息，精简冗余描述
- 改视角：转换叙述视角（如从第一人称改为第三人称）
- 改人称：改变角色的人称代词

请直接输出重写后的文本，不要添加任何说明。
{% if anti_ai %}
{{ anti_ai }}
{% endif %}"""

    USER_PROMPT_TEMPLATE = """请按「{{ direction }}」方向重写以下文本：

{{ text }}"""

    def render(self, context: dict) -> list:
        system_content = self._render_template(self.SYSTEM_PROMPT, context)
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]


class AnalyzeTemplate(PromptTemplate):
    """AI 小说质量分析模板。"""

    template_name = "analyze"

    SYSTEM_PROMPT = """你是一位专业的小说质量分析专家。请从以下维度对章节内容进行评分（1-10分）并给出具体建议。

分析维度：
1. 情节节奏：情节推进是否流畅，张弛有度
2. 对话质量：对话是否自然，符合角色性格
3. 描写丰富度：环境、人物、心理描写是否到位
4. 逻辑一致性：情节发展是否符合逻辑和设定
5. AI 痕迹检测：文本是否存在明显的 AI 写作特征

对每个维度给出分数和简短分析，最后给出综合评分和改进建议。"""

    USER_PROMPT_TEMPLATE = """请分析以下{{ genre }}小说章节的内容质量：

{{ content }}"""

    def render(self, context: dict) -> list:
        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

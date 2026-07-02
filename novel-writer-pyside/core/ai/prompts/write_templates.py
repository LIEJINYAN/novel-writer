"""写作相关提示词模板。"""
from .base import PromptTemplate


class ContinueWriteTemplate(PromptTemplate):
    """AI 续写模板。"""

    SYSTEM_PROMPT = """你是一个专业的小说续写助手。请根据用户提供的小说内容，自然地续写故事。

写作要求：
1. 保持原有文风和叙事节奏
2. 情节发展自然合理
3. 人物性格保持一致
4. 续写约2000字左右
5. 不要重复已有内容
6. 直接输出续写内容，不要加任何说明或解释"""

    USER_PROMPT_TEMPLATE = """请续写以下小说内容：

## 作品信息
- 类型：{{ genre }}
- 写作方法：{{ writing_method }}
- 当前字数：{{ word_count }}

## 前情回顾
{{ previous_chapters }}

## 当前章节
{{ title }}

## 章节内容
{{ content }}

请从上文结束的地方自然续写："""

    def render(self, context: dict) -> list:
        # 截取内容尾部 2000 字，避免上下文过长
        content = context.get("content", "")
        if len(content) > 2000:
            content = content[-2000:]
            context = {**context, "content": content}

        # 截取前情回顾为最近 3000 字
        prev = context.get("previous_chapters", "")
        if len(prev) > 3000:
            prev = prev[-3000:]
            context = {**context, "previous_chapters": prev}

        system_content = self.SYSTEM_PROMPT
        user_content = self._render_template(self.USER_PROMPT_TEMPLATE, context)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

"""提示词模板包。"""
from .anti_ai_detection import get_anti_ai_prompt, ANTI_AI_GUIDELINES
from .base import PromptTemplate
from .write_templates import ContinueWriteTemplate
from .edit_templates import PolishTemplate, RewriteTemplate, AnalyzeTemplate
from .registry import PROMPT_REGISTRY, get_template, list_templates

__all__ = [
    "get_anti_ai_prompt",
    "ANTI_AI_GUIDELINES",
    "PromptTemplate",
    "ContinueWriteTemplate",
    "PolishTemplate",
    "RewriteTemplate",
    "AnalyzeTemplate",
    "PROMPT_REGISTRY",
    "get_template",
    "list_templates",
]

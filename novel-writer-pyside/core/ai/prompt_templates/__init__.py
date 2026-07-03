"""提示词模板包。"""
from .base import PromptTemplate
from .registry import PROMPT_REGISTRY, get_template, list_templates
from .anti_ai import ANTI_AI_SYSTEM
from .presets import (
    CREATIVE_CONFIG, EDITING_CONFIG, ANALYSIS_CONFIG,
    DIALOGUE_CONFIG, OUTLINE_CONFIG, CREATIVE_ENHANCEMENT,
)

__all__ = [
    "PromptTemplate",
    "PROMPT_REGISTRY",
    "get_template",
    "list_templates",
    "ANTI_AI_SYSTEM",
    "CREATIVE_CONFIG",
    "EDITING_CONFIG",
    "ANALYSIS_CONFIG",
    "DIALOGUE_CONFIG",
    "OUTLINE_CONFIG",
    "CREATIVE_ENHANCEMENT",
]

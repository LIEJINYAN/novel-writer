"""提示词模板注册表。"""
from .base import PromptTemplate
from .write_templates import ContinueWriteTemplate
from .edit_templates import PolishTemplate, RewriteTemplate, AnalyzeTemplate
from .expert_templates import (
    PlotExpertTemplate, CharacterExpertTemplate,
    WorldExpertTemplate, StyleExpertTemplate,
    PlotCheckTemplate, ConsistencyCheckTemplate,
    CharacterCheckTemplate,
)
from .write_templates_v2 import (
    ConstitutionTemplate, SpecifyTemplate,
    WorldExpandTemplate, DialogueGenTemplate, TitleGenTemplate,
)


PROMPT_REGISTRY: dict[str, PromptTemplate] = {
    "continue_write": ContinueWriteTemplate(),
    "polish": PolishTemplate(),
    "rewrite": RewriteTemplate(),
    "analyze": AnalyzeTemplate(),
    "plot_expert": PlotExpertTemplate(),
    "character_expert": CharacterExpertTemplate(),
    "world_expert": WorldExpertTemplate(),
    "style_expert": StyleExpertTemplate(),
    "plot_check": PlotCheckTemplate(),
    "consistency_check": ConsistencyCheckTemplate(),
    "character_check": CharacterCheckTemplate(),
    "constitution": ConstitutionTemplate(),
    "specify": SpecifyTemplate(),
    "world_expand": WorldExpandTemplate(),
    "dialogue_gen": DialogueGenTemplate(),
    "title_gen": TitleGenTemplate(),
}


def get_template(name: str) -> PromptTemplate | None:
    """获取模板实例。"""
    return PROMPT_REGISTRY.get(name)


def list_templates() -> list[str]:
    """列出所有模板名称。"""
    return list(PROMPT_REGISTRY.keys())

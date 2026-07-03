"""提示词模板注册表。"""
from .writing import (
    constitution_template, specify_template,
    clarify_template, plan_template, tasks_template, write_template,
)
from .editing import (
    polish_template, continue_write_template,
    rewrite_template, dialogue_template,
)
from .analysis import analyze_template
from .experts import (
    plot_expert_template, character_expert_template,
    world_expert_template, style_expert_template,
    plot_check_template, consistency_check_template,
    character_check_template,
)

PROMPT_REGISTRY = {
    # writing (6个)
    "constitution": constitution_template,
    "specify": specify_template,
    "clarify": clarify_template,
    "plan": plan_template,
    "tasks": tasks_template,
    "write": write_template,
    # editing (4个)
    "polish": polish_template,
    "continue_write": continue_write_template,
    "rewrite": rewrite_template,
    "dialogue": dialogue_template,
    # analysis (1个)
    "analyze": analyze_template,
    # experts (7个)
    "plot_expert": plot_expert_template,
    "character_expert": character_expert_template,
    "world_expert": world_expert_template,
    "style_expert": style_expert_template,
    "plot_check": plot_check_template,
    "consistency_check": consistency_check_template,
    "character_check": character_check_template,
}


def get_template(name: str):
    """获取模板实例。"""
    return PROMPT_REGISTRY.get(name)


def list_templates() -> list:
    """列出所有模板名称。"""
    return list(PROMPT_REGISTRY.keys())

"""分析模板 - 综合质量分析。"""
from .base import PromptTemplate, AIConfig

# ============================================================
# 综合质量分析
# ============================================================
ANALYZE_SYSTEM = """你是一位专业的小说分析顾问，擅长从多个维度评估小说质量。"""

ANALYZE_TEMPLATE = """请分析以下小说内容：

## 分析模式
{analyze_type}（框架分析/内容分析/专项分析）

## 专项分析焦点
{focus_area}（opening/pacing/character/foreshadow/logic/style）

## 待分析内容
{content}

## 追踪数据
- 角色状态：{character_state}
- 情节追踪：{plot_tracker}
- 关系网络：{relationships}

请按照以下结构输出分析报告：

# 质量分析报告

## 总体评分
- 框架完整性：X/10
- 内容质量：X/10
- 一致性：X/10
- 总评：X/10

## 详细分析
### 1. 框架分析（或内容分析）
...

### 2. 专项分析（如有）
...

## 发现的问题
1. [严重程度] 问题描述 → 修复建议
2. ...

## 改进建议
1. ...
2. ...
"""

analyze_template = PromptTemplate(
    name="analyze",
    description="综合质量分析",
    system_prompt=ANALYZE_SYSTEM,
    user_prompt_template=ANALYZE_TEMPLATE,
    default_config=AIConfig(temperature=0.5, max_tokens=6000),
)

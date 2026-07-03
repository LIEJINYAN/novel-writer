"""编辑模板 - 润色、续写、重写、对话生成。"""
from .base import PromptTemplate, AIConfig

# ============================================================
# 1. 润色
# ============================================================
POLISH_SYSTEM = """你是一位专业的文字编辑，精通中文小说润色。
你的润色原则：
1. 保持原意和风格不变
2. 优化语句流畅度
3. 增强情感表达
4. 消除AI痕迹
5. 具象化抽象表达"""

POLISH_TEMPLATE = """请润色以下文本：

**原文**：
{text}

**润色要求**：
- 风格：{style}（如：更生动/更克制/更抒情/更简洁）
- 目标：优化语言流畅度，增强情感表达
- 限制：不改变情节和角色行为
- 反AI检测：替换AI高频词，增加具象化描写

请直接输出润色后的文本，不要包含说明。"""

polish_template = PromptTemplate(
    name="polish",
    description="润色文本",
    system_prompt=POLISH_SYSTEM,
    user_prompt_template=POLISH_TEMPLATE,
    default_config=AIConfig(temperature=0.7, max_tokens=4000),
)

# ============================================================
# 2. 续写
# ============================================================
CONTINUE_WRITE_SYSTEM = """你是一位专业的小说创作者。
请根据已有上下文自然续写，保持风格一致性。"""

CONTINUE_WRITE_TEMPLATE = """请续写以下内容：

## 创作宪法摘要
{constitution_summary}

## 角色当前状态
{character_state}

## 前文内容（最后500字）
{previous_text}

## 续写要求
- 续写字数：约{target_words}字
- 保持人称和时态一致
- 自然衔接前文
- 推进情节发展

请直接输出续写内容。"""

continue_write_template = PromptTemplate(
    name="continue_write",
    description="续写内容",
    system_prompt=CONTINUE_WRITE_SYSTEM,
    user_prompt_template=CONTINUE_WRITE_TEMPLATE,
    default_config=AIConfig(temperature=0.8, max_tokens=4000),
)

# ============================================================
# 3. 重写
# ============================================================
REWRITE_SYSTEM = """你是一位专业的小说重写助手。你的任务是根据指定的改写方向，对文本进行重写。

改写方向说明：
- 扩写：在原有基础上丰富细节、对话、描写和环境渲染
- 缩写：保留核心信息，精简冗余描述
- 改视角：转换叙述视角（如从第一人称改为第三人称）
- 改人称：改变角色的人称代词

请直接输出重写后的文本，不要添加任何说明。"""

REWRITE_TEMPLATE = """请按「{direction}」方向重写以下文本：

{text}"""

rewrite_template = PromptTemplate(
    name="rewrite",
    description="重写文本",
    system_prompt=REWRITE_SYSTEM,
    user_prompt_template=REWRITE_TEMPLATE,
    default_config=AIConfig(temperature=0.7, max_tokens=4000),
)

# ============================================================
# 4. 对话生成
# ============================================================
DIALOGUE_SYSTEM = """你是一位专业的对话设计师，擅长创作自然、有个性的角色对话。"""

DIALOGUE_TEMPLATE = """请为以下场景生成角色对话：

**参与角色**：
{characters}

**角色关系**：
{relationships}

**场景设定**：
{scene_description}

**场景目标**：{scene_goal}

**对话要求**：
1. 每个角色有独特的说话方式
2. 对话要推动情节或揭示性格
3. 避免说明式对话（信息直接告知）
4. 加入动作描写和微表情
5. 自然的话题转折

请直接输出对话内容。"""

dialogue_template = PromptTemplate(
    name="dialogue",
    description="生成角色对话",
    system_prompt=DIALOGUE_SYSTEM,
    user_prompt_template=DIALOGUE_TEMPLATE,
    default_config=AIConfig(temperature=0.9, max_tokens=3000),
)

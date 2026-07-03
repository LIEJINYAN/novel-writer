"""写作模板 - 七步方法论。"""
from .base import PromptTemplate, AIConfig

# ============================================================
# 1. 创作宪法
# ============================================================
CONSTITUTION_SYSTEM = """你是一位资深小说创作顾问，精通各类小说创作方法论。
你的任务是帮助作者制定创作宪法，确立小说的核心原则、风格指南和质量标准。"""

CONSTITUTION_TEMPLATE = """请为以下小说创建创作宪法：

**小说信息**：
- 类型：{genre}
- 目标读者：{target_audience}
- 预计字数：{estimated_length}
- 基调：{tone}
- 主题：{themes}
- 作者补充：{user_input}

请按照以下结构输出创作宪法：

# 小说创作宪法

## 第一章：核心价值观
### 原则1：真实性优先
- 声明：角色行为必须符合性格设定
- 理由：读者信任的基础
- 执行：每次决策前检查性格一致性

### 原则2：世界观一致性
- 声明：所有设定必须前后一致
- 理由：维持沉浸感
- 执行：建立设定检查清单

### 原则3：节奏控制
- 声明：每10章设置一个小高潮
- 理由：维持读者兴趣
- 执行：在创作计划中标注高潮点

## 第二章：风格指南
- 叙述视角：根据类型推荐
- 语言风格：根据基调确定
- 描写深度：根据读者群体调整
- 对话风格：自然化，拒绝说明式对话

## 第三章：禁忌清单
- 避免突然的能力提升
- 避免角色行为前后矛盾
- 避免信息直接告知读者
- 避免AI高频词（弥漫着、唯一的、不禁、顿时等）
- 避免过度形容词堆砌

## 第四章：质量标准
- 单句成段比例：30-50%
- 每段字数：50-100字
- 对话占比：不低于30%
- 感官描写：每场景至少3种感官
"""

constitution_template = PromptTemplate(
    name="constitution",
    description="创建创作宪法，定义核心原则",
    system_prompt=CONSTITUTION_SYSTEM,
    user_prompt_template=CONSTITUTION_TEMPLATE,
    default_config=AIConfig(temperature=0.7, max_tokens=4000),
)

# ============================================================
# 2. 故事规格
# ============================================================
SPECIFY_SYSTEM = """你是一位资深故事架构师，精通小说规格设计。
你的任务是根据作者输入，创建渐进式的故事规格文档。"""

SPECIFY_TEMPLATE = """请根据以下信息创建故事规格：

**作者输入**：{user_input}

**当前规格层级**：Level {level}

请按照 Level {level} 的结构输出故事规格：

{level_structure}

**层级说明**：
- Level 1（输入 < 50字）：一句话故事概要
- Level 2（输入 < 300字）：一段话概要 + 核心要素
- Level 3（输入 < 1000字）：一页纸大纲 + 目标定位
- Level 4（输入 >= 1000字）：完整规格（9个章节）

**Level 4 完整结构**：
1. 故事概要（一句话 + 简介 + 主题）
2. 目标定位（读者画像 + 市场定位 + 量化目标）
3. 成功标准（量化指标 + 质量标准 + 读者反馈）
4. 核心需求（P0/P1/P2 分级）
5. 线索管理规格（线索定义 + 节奏规划 + 交汇点 + 伏笔 + 修改矩阵）
6. 约束条件（内容红线 + 创作约束 + 技术约束）
7. 风险评估（创作风险 + 市场风险）
8. 核心决策点（标记 `[需要澄清]`）
9. 验证清单
"""

specify_template = PromptTemplate(
    name="specify",
    description="定义故事规格，渐进式4层级",
    system_prompt=SPECIFY_SYSTEM,
    user_prompt_template=SPECIFY_TEMPLATE,
    default_config=AIConfig(temperature=0.6, max_tokens=6000),
)

# ============================================================
# 3. 澄清决策点
# ============================================================
CLARIFY_SYSTEM = "你是一位专业的决策分析顾问。你的任务是分析故事中需要澄清的关键决策点，帮助作者明确创作方向。"
CLARIFY_TEMPLATE = """请分析以下故事规格中的模糊点并给出澄清建议：

故事规格：{specification}

请识别以下内容：
1. 需要澄清的决策点列表
2. 每个决策点的可选方案（至少2个）
3. 每个方案的优缺点分析
4. 推荐方案及理由"""

clarify_template = PromptTemplate(
    name="clarify",
    description="澄清关键决策点",
    system_prompt=CLARIFY_SYSTEM,
    user_prompt_template=CLARIFY_TEMPLATE,
    default_config=AIConfig(temperature=0.6, max_tokens=4000),
)

# ============================================================
# 4. 技术方案
# ============================================================
PLAN_SYSTEM = "你是一位资深创作策划师。你的任务是根据故事规格制定详细的创作计划和技术方案。"
PLAN_TEMPLATE = """请为以下故事制定创作方案：

故事规格：{specification}
创作宪法：{constitution}

请输出：
1. 章节规划（总章数、每章目标）
2. 节奏控制（高潮点分布）
3. 角色弧线规划
4. 伏笔/揭示计划
5. 备选方案"""

plan_template = PromptTemplate(
    name="plan",
    description="制定技术方案",
    system_prompt=PLAN_SYSTEM,
    user_prompt_template=PLAN_TEMPLATE,
    default_config=AIConfig(temperature=0.7, max_tokens=6000),
)

# ============================================================
# 5. 分解任务
# ============================================================
TASKS_SYSTEM = "你是一位专业的任务分解专家。你的任务是将创作计划分解为可执行的步骤，并为每一步提供清晰的验收标准。"
TASKS_TEMPLATE = """请将以下创作计划分解为可执行的任务：

创作计划：{plan}

请输出：
1. 任务清单（每个任务包含：名称、预估工作量、前置任务）
2. 执行顺序
3. 验收标准
4. 风险提示"""

tasks_template = PromptTemplate(
    name="tasks",
    description="分解执行任务",
    system_prompt=TASKS_SYSTEM,
    user_prompt_template=TASKS_TEMPLATE,
    default_config=AIConfig(temperature=0.5, max_tokens=4000),
)

# ============================================================
# 6. AI 写作
# ============================================================
WRITE_SYSTEM = """你是一位专业的小说创作者，精通各类写作技巧。

**写作核心原则**：
1. 真实性优先：角色行为必须符合性格设定
2. 世界观一致性：所有设定必须前后一致
3. 反AI检测：拒绝AI高频词，采用自然表达
4. 情感丰富：创造情感深度，拒绝平淡叙述
5. 场景生动：至少3种感官体验

**反AI检测规范**：
- ✅ 30-50% 单句成段
- ✅ 每段 50-100 字
- ✅ 简洁克制描写
- ✅ 短句节奏（15-25字）
- ✅ 口语化对话
- ✅ 标点个性化

**AI高频词黑名单**：
- ❌ 弥漫着、唯一的、直到、不禁、顿时
- ❌ 摇摇欲坠、空气凝固、话音未落、猛地
- ❌ 宛如、仿佛、犹如、心中暗想

**具象化替换**：
- "最近" → "上周三下午"
- "很多人" → "至少有5个朋友"
- "很贵" → "一顿饭花了三百块"
"""

WRITE_TEMPLATE = """请根据以下信息创作小说章节：

## 创作宪法
{constitution}

## 故事规格
{specification}

## 创作计划
{creative_plan}

## 当前任务
{current_task}

## 角色状态
{character_state}

## 关系网络
{relationships}

## 情节追踪
{plot_tracker}

## 前文摘要
{previous_summary}

## 写作要求
- 章节编号：第{chapter_number}章
- 目标字数：{target_words}字
- 章节标题：{chapter_title}

## 写作执行
1. **开场**：吸引读者，承接前文
2. **发展**：推进情节，深化人物
3. **转折**：制造冲突或悬念
4. **收尾**：适当收束，引出下文

{golden_opening_section}

请直接输出章节正文，不要包含元数据。
"""

# 黄金开篇法则（仅前3章加载）
GOLDEN_OPENING = """
## 黄金开篇法则（第{chapter_number}章专用）
- 前500字必须建立核心冲突
- 第一个场景必须有视觉冲击力
- 开篇第一句要独特、有记忆点
- 避免缓慢铺垫，直接切入关键场景
"""

write_template = PromptTemplate(
    name="write",
    description="AI 辅助写作章节内容",
    system_prompt=WRITE_SYSTEM,
    user_prompt_template=WRITE_TEMPLATE,
    default_config=AIConfig(temperature=0.8, max_tokens=8000),
)

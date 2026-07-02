# Phase 3 剩余功能实现计划

## 第三批：上下文管理 + 通义千问/豆包（高优先级）

### [x] Task 3.1: Token 计数器

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `core/ai/context/token_counter.py`
  - 集成 `tiktoken` 库，未安装时优雅降级为估算模式
  - `TokenCounter` 类支持 `count()`、`count_messages()`、`get_model_max_tokens()`
  - 支持 9 大模型族映射（gpt-4, gpt-4o, claude, gemini, deepseek, qwen 等）
- **Acceptance Criteria**: AC-1

### [x] Task 3.2: 上下文构建器

- **Priority**: high
- **Depends On**: Task 3.1
- **Description**:
  - 创建 `core/ai/context/context_builder.py`
  - `ContextBuilder.build_chapter_context()` — 章节+项目+角色上下文
  - `ContextBuilder.build_project_context()` — 项目级上下文
  - `ContextBuilder.build_analysis_context()` — 分析专用上下文
  - 无数据库时优雅降级
- **Acceptance Criteria**: AC-1

### [x] Task 3.3: 上下文裁剪

- **Priority**: high
- **Depends On**: Task 3.1
- **Description**:
  - 创建 `core/ai/context/context_pruner.py`
  - `ContextPruner.prune()` — 按优先级段落裁剪
  - `ContextPruner.prune_messages()` — 裁剪聊天历史（保留 system）
  - `ContextPruner.estimate_window()` — 窗口使用估算
- **Acceptance Criteria**: AC-1

### [x] Task 3.4: 上下文管理器集成

- **Priority**: high
- **Depends On**: Task 3.2, Task 3.3
- **Description**:
  - 创建 `core/ai/context_manager.py`
  - `AIContextManager` 整合 token_counter + context_builder + context_pruner
  - `get_chapter_context()` / `get_analysis_context()` / `get_chat_context()` / `estimate()` / `count()`
- **Acceptance Criteria**: AC-1

### [x] Task 3.5: 通义千问适配器

- **Priority**: low
- **Depends On**: None
- **Description**:
  - 创建 `core/ai/providers/tongyi_provider.py` — 兼容 OpenAI API
  - 创建 `core/ai/providers/doubao_provider.py` — 兼容 OpenAI API
- **Acceptance Criteria**: AC-1

### [x] Task 3.6: 注册通义千问/豆包到 AIManager

- **Priority**: low
- **Depends On**: Task 3.5
- **Description**:
  - 修改 `core/ai/manager.py`：注册 tongyi 和 doubao
  - 共 7 个提供商（openai, deepseek, ollama, anthropic, gemini, tongyi, doubao）
- **Acceptance Criteria**: AC-1

---

## 第四批：AI 润色差分对比 + 反 AI 检测（中优先级）

### [x] Task 4.1: 润色差分对比对话框

- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 创建 `ui/dialogs/ai_polish_diff_dialog.py`
  - `AIPolishDiffDialog`：左右两栏 + 颜色高亮差异 + 统计信息 + 应用/取消/重新润色
  - `DiffHighlighter`：QSyntaxHighlighter 子类，绿色/红色/黄色标记变更
- **Acceptance Criteria**: AC-2

### [x] Task 4.2: 润色对话框集成到主窗口

- **Priority**: medium
- **Depends On**: Task 4.1
- **Description**:
  - 修改 `ui/main_window.py`：润色完成后弹出差分对话框，用户确认后才应用
  - 添加 `_on_ai_rewrite_chunk` / `_on_ai_rewrite_finished` 方法（重写保持直接替换）
- **Acceptance Criteria**: AC-2

### [x] Task 4.3: 反 AI 检测规范

- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 创建 `core/ai/prompts/anti_ai_detection.py` — 7 条反 AI 写作规范
  - 修改 `edit_templates.py`：PolishTemplate 和 RewriteTemplate 支持 `{{ anti_ai }}` 变量
- **Acceptance Criteria**: AC-2

---

## 第五批：写作方法系统（中优先级）

### [x] Task 5.1: WritingMethod 基类

- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 创建 `core/ai/writing_methods/base.py`
  - `WritingMethod` 基类：name, stages, analyze_outline, get_stage_for_chapter, suggest_chapter
  - `MethodStage` 数据类：name, order, description, min_chapters, max_chapters, color
- **Acceptance Criteria**: AC-3

### [x] Task 5.2: 具体方法实现（3+ 种）

- **Priority**: medium
- **Depends On**: Task 5.1
- **Description**:
  - `ThreeActMethod`（三幕式：4 个阶段）
  - `HeroJourneyMethod`（英雄之旅：12 个阶段）
  - `SevenPointMethod`（七点结构：7 个阶段）
- **Acceptance Criteria**: AC-3

### [x] Task 5.3: 方法推荐器

- **Priority**: medium
- **Depends On**: Task 5.2
- **Description**:
  - 创建 `core/ai/writing_methods/advisor.py`
  - `MethodAdvisor.recommend(genre, experience, length)` — 按分数降序推荐
  - 评分逻辑：基础 50 + 类型匹配 + 经验匹配 + 篇幅匹配
- **Acceptance Criteria**: AC-3

### [x] Task 5.4: 方法大纲面板集成

- **Priority**: medium
- **Depends On**: Task 5.2
- **Description**:
  - 修改 `ui/sidebar/outline_panel.py`：添加方法选择器 + 阶段彩色指示条
  - 添加 `method_changed` 信号 + `get_current_method()` / `set_method()` / `load_method()`
- **Acceptance Criteria**: AC-3

---

## 第六批：高级提示词模板 + 创作向导（低优先级）

### [x] Task 6.1: 专家提示词模板

- **Priority**: low
- **Depends On**: None
- **Description**:
  - 创建 `core/ai/prompts/expert_templates.py`
  - 4 个专家模板：PlotExpertTemplate, CharacterExpertTemplate, WorldExpertTemplate, StyleExpertTemplate
  - 3 个分析补充模板：PlotCheckTemplate, ConsistencyCheckTemplate, CharacterCheckTemplate
  - 注册到 PROMPT_REGISTRY（共 11 个模板）
- **Acceptance Criteria**: AC-4

### [x] Task 6.2: 分析模板集补充

- **Priority**: low
- **Depends On**: None
- **Description**: 与 Task 6.1 合并实现

### [x] Task 6.3: 创作向导

- **Priority**: low
- **Depends On**: Task 5.4
- **Description**:
  - 创建 `ui/dialogs/creation_wizard.py`
  - 4 步向导：选择类型 → 选择方法（含推荐）→ 设定主角/世界观 → 预览大纲
  - `project_created` 信号发射创建结果
- **Acceptance Criteria**: AC-4

---

# 批次依赖关系

```
第三批 = Task 3.1 → 3.2 → 3.3 → 3.4
         Task 3.5 → 3.6（与 3.1-3.4 无依赖）
         3.5 和 3.1-3.4 可并行

第四批 = Task 4.1 → 4.2
         Task 4.3（与 4.1-4.2 无依赖）
         4.3 和 4.1-4.2 可并行

第五批 = Task 5.1 → 5.2 → 5.3
         Task 5.4（依赖 5.2）
         Task 5.1-5.4 不依赖第三/四批

第六批 = Task 6.1, 6.2 无依赖
         Task 6.3 依赖 5.4
```

# 批次间依赖
- 第四批不依赖第三批，可以并行
- 第五批不依赖第三/四批，可以并行
- 第六批的 6.3 依赖第五批

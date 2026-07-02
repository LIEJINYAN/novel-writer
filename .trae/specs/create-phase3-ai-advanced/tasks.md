# Phase 3 第二批：AI 高级功能 - 实现计划

## [x] Task 1: 安装新依赖
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 requirements.txt 添加 `anthropic>=0.30` 和 `google-generativeai>=0.6.0`
  - 安装新依赖
- **Acceptance Criteria**: AC-1, AC-2
- **Notes**: 使用 venv 中的 pip 安装

## [x] Task 2: Anthropic 适配器
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `core/ai/providers/anthropic_provider.py`
  - 继承 `BaseAIProvider`
  - 使用 `anthropic` Python SDK（`from anthropic import Anthropic`）
  - 实现 `chat()`：调用 `client.messages.create()`
  - 实现 `chat_stream()`：stream=True，yield delta.text
  - 实现 `test_connection()`：调用 `client.models.list()` 或简单 list 验证
  - 实现 `list_models()`：返回常用 Claude 模型列表
  - 错误处理：捕获 `anthropic.APIError`、`anthropic.AuthenticationError` 等
  - `default_models = ["claude-sonnet-4", "claude-haiku-3-5"]`
- **Acceptance Criteria**: AC-1
- **Notes**: Anthropic Messages API 与 OpenAI Chat Completions API 格式不同

## [x] Task 3: Google Gemini 适配器
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `core/ai/providers/gemini_provider.py`
  - 继承 `BaseAIProvider`
  - 使用 `google-generativeai` SDK
  - 实现 `chat()`、`chat_stream()`、`test_connection()`、`list_models()`
  - `default_models = ["gemini-2.0-flash", "gemini-2.0-pro"]`
- **Acceptance Criteria**: AC-2
- **Notes**: Gemini SDK 的消息格式与 OpenAI 不同

## [x] Task 4: 注册新提供商到 AIManager
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 修改 `core/ai/manager.py`：注册 Anthropic 和 Gemini
- **Acceptance Criteria**: AC-1, AC-2
- **Notes**: 注册后共 5 个提供商

## [x] Task 5: 润色/重写/分析提示词模板
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `core/ai/prompts/edit_templates.py`
  - PolishTemplate、RewriteTemplate、AnalyzeTemplate
  - 注册到 PROMPT_REGISTRY
- **Acceptance Criteria**: AC-3, AC-4, AC-5
- **Notes**: 使用 Jinja2 模板引擎

## [x] Task 6: AI 编辑服务（润色/重写）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 创建 `core/ai/editing_service.py`
  - `polish()` 和 `rewrite()` 方法
  - 复用 AIWorker
- **Acceptance Criteria**: AC-3, AC-4
- **Notes**: 润色/重写完成后替换选中文本

## [x] Task 7: AI 分析服务
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 创建 `core/ai/analysis_service.py`
  - `analyze_chapter()` 方法
- **Acceptance Criteria**: AC-5
- **Notes**: 分析结果在对话面板展示

## [x] Task 8: AI 对话面板
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 创建 `ui/sidebar/ai_chat_panel.py`
  - AIChatPanel：消息气泡、输入框、发送按钮、流式回复
- **Acceptance Criteria**: AC-6
- **Notes**: 只用于自由对话

## [x] Task 9: 主窗口集成 AI 高级功能
- **Priority**: high
- **Depends On**: Task 6, Task 7, Task 8
- **Description**:
  - 修改 `ui/main_window.py`：润色/重写/分析/对话面板集成
  - 快捷键 Ctrl+Shift+P（润色）、Ctrl+Shift+R（重写）、Ctrl+Shift+A（分析）
- **Acceptance Criteria**: AC-3, AC-4, AC-5, AC-6
- **Notes**: 润色/重写需要选中文本

## [x] Task 10: QSS 主题适配（第二批）
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 修改 `ui/styles/dark.qss` 和 `ui/styles/light.qss`
  - 添加 AI 对话面板样式
- **Acceptance Criteria**: AC-6
- **Notes**: 沿用现有 QSS 风格体系

# Task Dependencies
- Task 1 → Task 2, Task 3
- Task 2, Task 3 → Task 4
- Task 5（无依赖，可与 Task 2-4 并行）
- Task 5, Task 7（第一批）→ Task 6
- Task 5 → Task 7
- Task 7 → Task 8（分析结果展示在对话面板）
- Task 6, Task 7, Task 8 → Task 9
- Task 8 → Task 10

# 并行执行建议
- Task 1（安装依赖）与 Task 5（提示词模板）无依赖，可并行
- Task 2（Anthropic）和 Task 3（Gemini）无依赖，可并行
- Task 4（注册提供商）在 Task 2+3 完成后执行
- Task 6（编辑服务）和 Task 7（分析服务）无依赖，可在 Task 5 后并行
- Task 8（对话面板）在 Task 7 后执行，与 Task 9 部分重叠
- Task 10（QSS）在 Task 8 后执行

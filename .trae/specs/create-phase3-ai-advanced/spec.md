# Phase 3 第二批：AI 高级功能（润色/重写/分析 + 更多提供商）

## Why

Phase 3 第一批完成了"AI 续写"这一最小闭环，但仅有续写功能不足以覆盖完整写作场景。用户还需要：
- 对已写内容进行润色和重写
- 对章节质量进行分析和评估
- 支持更多 AI 提供商（Claude、Gemini）以满足不同需求
- 通过对话方式与 AI 讨论写作思路

## What Changes

- **新增 2 个 AI 提供商**：Anthropic (Claude) 适配器、Google Gemini 适配器
- **新增 3 个 AI 编辑功能**：润色、重写、分析
- **新增 1 个 UI 组件**：AI 对话面板（侧边栏中与 AI 多轮对话）
- **扩展提示词模板**：添加润色模板、重写模板、分析模板
- **新增菜单/快捷键**：润色、重写的右键菜单和快捷键
- **AI 面板增强**：新增润色/重写/分析按钮，区分不同操作模式

## Impact

- 新增文件：`core/ai/providers/anthropic_provider.py`、`core/ai/providers/gemini_provider.py`
- 新增文件：`core/ai/prompts/edit_templates.py`（润色/重写/分析模板）
- 新增文件：`core/ai/analysis_service.py`（分析服务）
- 新增文件：`ui/sidebar/ai_chat_panel.py`（AI 对话面板）
- 修改 `core/ai/manager.py`：注册新提供商
- 修改 `core/ai/writing_service.py`：扩展为编辑服务（润色/重写）
- 修改 `ui/main_window.py`：集成新功能
- 修改 `ui/sidebar/ai_panel.py`：扩展操作按钮
- 修改 `ui/styles/dark.qss`、`light.qss`：对话面板样式
- 注册新提供商到 `core/ai/prompts/registry.py`

## Requirements

### FR-1: Anthropic 适配器
- 支持 Claude 系列模型（claude-sonnet-4、claude-haiku-3-5 等）
- 使用 `anthropic` Python SDK
- 支持流式输出（stream=True）
- 支持 API Base 自定义
- 错误映射：将 anthropic SDK 异常映射到 AIProviderError 层级

### FR-2: Google Gemini 适配器
- 支持 Gemini 系列模型（gemini-2.0-flash、gemini-2.0-pro 等）
- 使用 `google-generativeai` Python SDK
- 支持流式输出
- 错误映射

### FR-3: 润色功能（Polishing）
- 用户选中编辑器中的文本片段
- 右键菜单或 AI 面板选择"AI 润色"
- AI 在保持原意的前提下优化表达、修正语病、改善节奏
- 支持多种润色风格（简洁、优美、正式、口语化）
- 流式输出替换选中文本

### FR-4: 重写功能（Rewriting）
- 用户选中编辑器中的文本片段
- 选择"AI 重写"并指定改写方向（扩写、缩写、改视角、改人称等）
- 流式输出替换选中文本

### FR-5: 章节分析功能（Analysis）
- 对当前章节进行质量分析
- 分析维度：情节节奏、对话质量、描写丰富度、逻辑一致性、AI 痕迹检测
- 分析结果显示在 AI 对话面板中，而非直接修改编辑器内容
- 给出分数和建议

### FR-6: AI 对话面板
- 侧边栏新增"AI 对话"标签页
- 多轮对话界面：消息列表（QListWidget 或 QTextBrowser）
- 输入框 + 发送按钮（支持 Enter 发送）
- 对话历史保存在当前会话中
- 支持清空对话、复制消息
- 流式显示 AI 回复

### FR-7: 提示词模板扩展
- 润色模板：system 提示词 + 选中文本作为 user 消息
- 重写模板：system 提示词 + 改写方向参数 + 选中文本
- 分析模板：system 提示词 + 章节全文作为分析对象
- 所有模板使用 Jinja2 渲染，与第一批模板系统一致

### FR-8: 主窗口集成
- 编辑器右键菜单添加"AI 润色"、"AI 重写"、"AI 分析"选项
- AI 面板扩展：区分续写/润色/重写/分析模式
- AI 对话面板嵌入右侧侧边栏
- 快捷键 Ctrl+Shift+P（润色）、Ctrl+Shift+R（重写）

## Out of Scope
- AI 差分对比显示（润色前后对比高亮）— 第三批
- 上下文管理器、Token 计数、上下文裁剪 — 第三批
- 创作向导 UI（七步法向导）— 第四批
- 写作方法推荐 — 第四批
- 批量分析（多章节同时分析）— 第三批

## Acceptance Criteria

### AC-1: Anthropic 适配
- **Given**: 用户配置了 Anthropic API Key
- **When**: 测试连接
- **Then**: 连接成功，可获取模型列表，可流式调用
- Verification: programmatic

### AC-2: Gemini 适配
- **Given**: 用户配置了 Gemini API Key
- **When**: 测试连接
- **Then**: 连接成功，可流式调用
- Verification: programmatic

### AC-3: 润色功能
- **Given**: 用户在编辑器中选中文本
- **When**: 右键菜单 → "AI 润色"
- **Then**: AI 替换选中文本为润色后版本
- Verification: human-judgment

### AC-4: 重写功能
- **Given**: 用户在编辑器中选中文本
- **When**: 右键菜单 → "AI 重写" → 选择改写方向
- **Then**: AI 替换选中文本为重写后版本
- Verification: human-judgment

### AC-5: 章节分析
- **Given**: 用户打开一个章节
- **When**: 点击 AI 面板的"分析"按钮
- **Then**: 在对话面板中显示多维度分析结果
- Verification: human-judgment

### AC-6: AI 对话面板
- **Given**: 用户打开 AI 对话面板
- **When**: 输入消息并发送
- **Then**: AI 回复以流式方式显示在对话中，可连续对话
- Verification: human-judgment

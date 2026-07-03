# Phase 3 第一批：AI 基础设施与续写功能

## Overview
- **Summary**: 实现 AI 提供商抽象层、3 个具体适配器（OpenAI/DeepSeek/Ollama）、AI 管理器、AI 设置对话框、基础提示词模板系统和 AI 续写服务（流式输出），让用户能配置 AI 并在编辑器中一键续写。
- **Purpose**: 为后续所有 AI 功能（润色、重写、分析、对话等）奠定基础设施，第一批聚焦"能用 AI 续写"这一最小闭环。
- **Target Users**: 小说创作者，需要 AI 辅助续写章节内容。

## Goals
- 建立可扩展的 AI Provider 抽象层，支持未来添加更多提供商
- 实现 OpenAI、DeepSeek、Ollama 三个适配器（覆盖云端 API + 本地模型）
- AI 管理器统一管理提供商注册、切换、配置
- AI 设置对话框：配置 API Key、选择模型、设置参数
- 基础提示词模板系统：PromptTemplate 基类 + 续写模板
- AI 续写服务：流式输出，打字机效果插入编辑器
- AI 面板：模型选择、操作按钮、进度提示
- 编辑器续写按钮：右键菜单或快捷按钮触发续写

## Non-Goals (Out of Scope)
- Anthropic/Gemini/通义千问适配器（第二批）
- 润色、重写、分析等编辑功能（第二批）
- AI 对话面板、多轮对话（第三批）
- 上下文管理器、Token 计数、上下文裁剪（第三批）
- 专家模板系统（第四批）
- 写作方法推荐算法、方法转换（第四批）
- 创作向导 UI（第四批）
- AI 润色差分对比显示（第二批）

## Background & Context
- 原版 Novel Writer 是 CLI 工具，AI 调用通过 Claude Code/Cursor 等 CLI 代理完成
- PySide6 桌面版需要在应用内直接调用 AI API
- 已有 `AIProvider` 数据模型（[ai_provider.py](file:///I:/AI写小说/AI小说软件开发/novel-writer-2/novel-writer-pyside/models/ai_provider.py)），包含 name、api_key_encrypted、api_base、default_model、temperature、max_tokens 字段
- 已有 SignalBus 中的 AI 信号：ai_generation_started/finished/chunk_received/error
- 已有 AppConfig 中的 AI 默认配置
- 技术选型：OpenAI Python SDK 统一处理 OpenAI 和 DeepSeek（兼容接口），Ollama 用 httpx 调用本地 API

## Functional Requirements

### FR-1: AI Provider 抽象层
- 定义 `Message`（role/content）、`AIConfig`（model/temperature/max_tokens/stream）、`AIResponse`（content/usage/model）数据结构
- 定义 `BaseAIProvider` 抽象基类：`chat()`、`chat_stream()`、`test_connection()`、`list_models()`
- 所有适配器继承基类，统一接口

### FR-2: OpenAI 适配器
- 支持 GPT-4o、GPT-4o-mini、GPT-4-turbo 等模型
- 使用 openai Python SDK（>=1.0）
- 支持流式输出（stream=True）
- 支持 API Base 自定义（兼容第三方 OpenAI 兼容接口）

### FR-3: DeepSeek 适配器
- 支持 DeepSeek Chat、DeepSeek Reasoner
- 复用 OpenAI SDK（DeepSeek 兼容 OpenAI 接口）
- API Base 默认 `https://api.deepseek.com/v1`

### FR-4: Ollama 适配器
- 支持本地部署的模型（llama3、qwen2 等）
- 使用 httpx 直接调用 Ollama REST API（`http://localhost:11434/api/chat`）
- 支持流式输出（ndjson 解析）
- 支持自动获取本地已安装模型列表

### FR-5: AI 管理器
- 单例模式 `AIManager`
- 提供商注册：启动时自动注册 OpenAI/DeepSeek/Ollama
- 配置管理：从数据库加载已配置的提供商
- 当前激活提供商：切换、获取
- 统一调用入口：`chat()`、`chat_stream()`
- API Key 加密存储：使用 base64 + 机器码简单加密（非高安全性场景）

### FR-6: AI 设置对话框
- 提供商列表：显示所有已注册的提供商及状态（已配置/未配置）
- 配置表单：API Key（密码输入框）、API Base、默认模型、温度、Max Tokens
- 测试连接按钮：调用 `test_connection()`，显示成功/失败
- 模型列表：点击"获取模型列表"按钮拉取可用模型
- 保存/取消按钮
- 激活提供商：选择当前使用的提供商

### FR-7: 提示词模板系统
- `PromptTemplate` 基类：模板渲染、变量替换（使用 Jinja2）
- 续写模板：基于当前章节内容、前一章摘要、项目信息生成续写提示词
- 模板变量：`{title}`、`{content}`、`{prev_summary}`、`{genre}`、`{writing_method}`、`{word_count}`
- 模板存储：内置默认模板，未来支持自定义

### FR-8: AI 续写服务
- `WritingAIService`：封装续写逻辑
- 流式输出：通过 QThread + Signal 实现非阻塞流式调用
- 打字机效果：逐字/逐句插入编辑器当前光标位置
- 可取消：用户可中途停止生成
- 错误处理：网络错误、API 错误、Token 超限等友好提示

### FR-9: AI 面板 UI
- 底部或右侧面板，包含：
  - 提供商/模型选择下拉框
  - 温度滑块（0.0 - 2.0）
  - 续写按钮
  - 生成进度指示器（旋转图标 + 取消按钮）
  - 状态文本（"正在生成..."、"已生成 XXX 字"、"生成失败"）

### FR-10: 编辑器续写集成
- 编辑器右键菜单添加"AI 续写"选项
- 工具栏添加续写按钮
- 快捷键 Ctrl+I 触发续写
- 续写内容插入到当前光标位置
- 生成过程中禁用编辑器（只读模式）

## Non-Functional Requirements

### NFR-1: 响应性
- AI 调用必须在后台线程执行，不阻塞 UI
- 流式输出实时显示，延迟 < 500ms

### NFR-2: 安全性
- API Key 加密存储在数据库中，不明文显示
- API Key 不写入日志

### NFR-3: 可扩展性
- 新增 AI 提供商只需继承 BaseAIProvider 并注册，无需修改现有代码
- 新增提示词模板只需继承 PromptTemplate 并注册

### NFR-4: 容错性
- 网络超时自动重试（最多 2 次）
- API 错误显示友好提示，不崩溃
- 流式输出中断后保留已生成内容

### NFR-5: 兼容性
- OpenAI SDK 版本 >= 1.0（新版 API）
- Ollama 兼容 0.1.x+ 版本
- Windows 环境正常工作

## Constraints
- **Technical**: Python 3.11+, PySide6 6.11.1, SQLAlchemy 2.0, openai >= 1.0, httpx
- **Business**: API Key 安全存储，不明文暴露
- **Dependencies**: openai Python SDK, httpx（新增依赖）

## Assumptions
- 用户已有 OpenAI 或 DeepSeek 的 API Key，或已本地部署 Ollama
- 续写功能依赖当前章节内容作为上下文，暂不支持复杂的上下文管理（第三批做）
- 第一批暂不实现 Token 计数和上下文裁剪，长内容可能被截断

## Acceptance Criteria

### AC-1: AI Provider 抽象层
- **Given**: 开发者需要添加新的 AI 提供商
- **When**: 创建新类继承 BaseAIProvider 并实现 chat/chat_stream/test_connection
- **Then**: 新提供商自动可用，无需修改 AIManager 或 UI 代码
- **Verification**: `programmatic`

### AC-2: OpenAI 适配器
- **Given**: 用户配置了有效的 OpenAI API Key
- **When**: 点击"测试连接"按钮
- **Then**: 显示"连接成功"，并能获取可用模型列表
- **Verification**: `programmatic`

### AC-3: OpenAI 流式续写
- **Given**: 用户打开一个章节，配置好 OpenAI 提供商
- **When**: 点击"AI 续写"按钮
- **Then**: AI 生成内容以流式方式逐字插入编辑器光标位置，可中途取消
- **Verification**: `human-judgment`

### AC-4: DeepSeek 适配器
- **Given**: 用户配置了 DeepSeek API Key 和 API Base
- **When**: 切换到 DeepSeek 并测试连接
- **Then**: 连接成功，能调用续写
- **Verification**: `programmatic`

### AC-5: Ollama 适配器
- **Given**: 用户本地运行了 Ollama 并加载了模型
- **When**: 配置 Ollama 提供商（默认 localhost:11434）
- **Then**: 能获取本地模型列表，能调用续写
- **Verification**: `programmatic`

### AC-6: AI 管理器
- **Given**: 应用启动
- **When**: AIManager 初始化
- **Then**: 自动注册 OpenAI/DeepSeek/Ollama 三个提供商，从数据库加载已保存的配置
- **Verification**: `programmatic`

### AC-7: AI 设置对话框
- **Given**: 用户打开"AI 设置"对话框
- **When**: 填写 API Key、选择模型、点击保存
- **Then**: 配置保存到数据库，API Key 加密存储，激活的提供商可切换
- **Verification**: `human-judgment`

### AC-8: 续写提示词模板
- **Given**: 用户在编辑器中点击续写
- **When**: 系统构建提示词
- **Then**: 包含当前章节标题、内容（截取尾部 2000 字）、项目类型等信息
- **Verification**: `programmatic`

### AC-9: 流式输出 UI 响应
- **Given**: AI 正在流式生成内容
- **When**: 内容逐字返回
- **Then**: 编辑器实时显示生成内容，UI 不卡顿，可点击"取消"停止
- **Verification**: `human-judgment`

### AC-10: 续写按钮集成
- **Given**: 用户在编辑器中编辑章节
- **When**: 点击工具栏续写按钮 / 右键菜单"AI 续写" / 按 Ctrl+I
- **Then**: 触发 AI 续写，内容插入光标位置
- **Verification**: `human-judgment`

### AC-11: 错误处理
- **Given**: API Key 无效或网络不通
- **When**: 用户触发续写
- **Then**: 显示友好的错误提示（"API Key 无效" / "网络连接失败"），不崩溃
- **Verification**: `human-judgment`

### AC-12: API Key 安全
- **Given**: 用户保存了 API Key
- **When**: 查看数据库
- **Then**: API Key 以加密形式存储，不在任何日志中明文输出
- **Verification**: `programmatic`

## ~~Open Questions~~ ✅ 全部已决策
- [x] **Ollama 适配器** → 使用 httpx 直接调用（无需 ollama Python 包）
- [x] **续写字数选择** → 默认 2000 字，AIPanel 提供字数选择器（QComboBox 500-10000）
- [x] **API Key 加密** → 使用 cryptography 库，`utils/crypto.py` 已实现

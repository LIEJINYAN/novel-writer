# Phase 3 第一批：AI 基础设施与续写功能 - 验证检查清单

## 依赖与基础设施
- [x] Checkpoint 1: requirements.txt 包含 `openai>=1.0` 和 `httpx>=0.27`
- [x] Checkpoint 2: `import openai` 和 `import httpx` 在 venv 中成功
- [x] Checkpoint 3: .env.example 包含 AI 相关环境变量示例（OPENAI_API_KEY、DEEPSEEK_API_KEY、OLLAMA_HOST 等）

## AI Provider 抽象层
- [x] Checkpoint 4: `core/ai/base.py` 定义了 `Message`、`AIConfig`、`AIResponse` 数据结构
- [x] Checkpoint 5: `BaseAIProvider` 是抽象基类，包含 `chat()`、`chat_stream()`、`test_connection()`、`list_models()` 抽象方法
- [x] Checkpoint 6: `BaseAIProvider` 不能直接实例化
- [x] Checkpoint 7: `AIProviderError` 异常类层级已定义

## OpenAI 适配器
- [x] Checkpoint 8: `OpenAIProvider` 继承 `BaseAIProvider`
- [x] Checkpoint 9: `name` 属性为 `"openai"`，`display_name` 为 `"OpenAI"`
- [x] Checkpoint 10: `default_models` 包含 `gpt-4o`、`gpt-4o-mini`
- [x] Checkpoint 11: 使用 openai SDK >= 1.0 的新版 API（`from openai import OpenAI`）
- [x] Checkpoint 12: `chat()` 方法返回 `AIResponse` 对象
- [x] Checkpoint 13: `chat_stream()` 是生成器，逐个 yield 字符串 chunk
- [x] Checkpoint 14: 支持 api_base 自定义

## DeepSeek 适配器
- [x] Checkpoint 15: `DeepSeekProvider` 继承 `OpenAIProvider`
- [x] Checkpoint 16: `name` 属性为 `"deepseek"`，`display_name` 为 `"DeepSeek"`
- [x] Checkpoint 17: `default_api_base` 为 `"https://api.deepseek.com/v1"`
- [x] Checkpoint 18: `default_models` 包含 `deepseek-chat`、`deepseek-reasoner`

## Ollama 适配器
- [x] Checkpoint 19: `OllamaProvider` 继承 `BaseAIProvider`
- [x] Checkpoint 20: `name` 属性为 `"ollama"`，`display_name` 为 `"Ollama"`
- [x] Checkpoint 21: `default_api_base` 为 `"http://localhost:11434"`
- [x] Checkpoint 22: 使用 httpx 调用 Ollama REST API
- [x] Checkpoint 23: `chat_stream()` 正确解析 ndjson 流式响应
- [x] Checkpoint 24: `list_models()` 通过 GET `/api/tags` 获取本地模型
- [x] Checkpoint 25: Ollama 未运行时 `test_connection()` 返回 False 而非崩溃

## API Key 加密工具
- [x] Checkpoint 26: `utils/crypto.py` 定义了 `encrypt_api_key()` 和 `decrypt_api_key()`
- [x] Checkpoint 27: `decrypt_api_key(encrypt_api_key("test"))` == `"test"`
- [x] Checkpoint 28: 加密结果不包含原始 key 明文
- [x] Checkpoint 29: `get_machine_code()` 在同一机器上返回一致结果

## AI 管理器
- [x] Checkpoint 30: `AIManager` 是单例类
- [x] Checkpoint 31: `init()` 自动注册 OpenAI/DeepSeek/Ollama 三个提供商
- [x] Checkpoint 32: `list_providers()` 返回 3 个提供商的名称、显示名、配置状态
- [x] Checkpoint 33: `save_config()` 将 API Key 加密后存入数据库
- [x] Checkpoint 34: `load_configs()` 从数据库加载并解密 API Key
- [x] Checkpoint 35: `get_active_provider()` 在未配置时返回 None
- [x] Checkpoint 36: `set_active_provider()` 切换激活提供商
- [x] Checkpoint 37: `chat()` 和 `chat_stream()` 通过激活提供商调用

## 提示词模板系统
- [x] Checkpoint 38: `PromptTemplate` 基类定义了 `render(context) -> list[Message]` 接口
- [x] Checkpoint 39: `ContinueWriteTemplate` 生成 system + user 消息
- [x] Checkpoint 40: 续写模板包含章节标题、内容、类型、写作方法等变量
- [x] Checkpoint 41: 内容超过 2000 字时自动截取尾部
- [x] Checkpoint 42: `PROMPT_REGISTRY` 包含 `continue_write` 模板

## AI 续写服务
- [x] Checkpoint 43: `AIWorker` 继承 `QThread`
- [x] Checkpoint 44: `AIWorker` 有 `chunk_received(str)`、`finished(str)`、`error(str)` 信号
- [x] Checkpoint 45: `cancel()` 方法能中断流式生成
- [x] Checkpoint 46: `WritingAIService.continue_write()` 方法签名正确
- [x] Checkpoint 47: 无激活提供商时抛出友好异常而非崩溃
- [x] Checkpoint 48: 网络错误捕获后通过 error 信号发送

## AI 设置对话框
- [x] Checkpoint 49: `AISettingsDialog` 继承 `QDialog`
- [x] Checkpoint 50: 左侧提供商列表显示 3 个提供商及状态
- [x] Checkpoint 51: API Key 输入框默认隐藏文本（echoMode=Password）
- [x] Checkpoint 52: 有"测试连接"按钮，点击后异步执行不阻塞 UI
- [x] Checkpoint 53: 有"获取模型列表"按钮
- [x] Checkpoint 54: 保存按钮调用 `AIManager.save_config()`
- [x] Checkpoint 55: 温度输入范围 0.0-2.0，Max Tokens 范围 256-32768
- [x] Checkpoint 56: 对话框可通过菜单"设置 → AI 设置"打开

## AI 面板 UI
- [x] Checkpoint 57: `AIPanel` 继承 `QWidget`
- [x] Checkpoint 58: 有提供商/模型选择下拉框
- [x] Checkpoint 59: 有温度滑块及数值显示
- [x] Checkpoint 60: 有续写按钮，生成时变为取消按钮
- [x] Checkpoint 61: 有进度指示器（旋转动画或等效）
- [x] Checkpoint 62: 有状态文本显示
- [x] Checkpoint 63: `continue_write_requested` 信号正确连接

## 主窗口集成
- [x] Checkpoint 64: 菜单栏"设置"菜单有"AI 设置"菜单项
- [x] Checkpoint 65: 右侧面板有"AI"标签页
- [x] Checkpoint 66: `_on_ai_continue_write()` 获取当前章节并创建 AIWorker
- [x] Checkpoint 67: `_on_ai_chunk_received()` 在编辑器光标位置插入文本
- [x] Checkpoint 68: `_on_ai_finished()` 恢复编辑器可编辑状态
- [x] Checkpoint 69: `_on_ai_error()` 显示友好错误提示
- [x] Checkpoint 70: `_on_ai_cancel()` 停止 AIWorker
- [x] Checkpoint 71: 编辑器右键菜单有"AI 续写"选项
- [x] Checkpoint 72: 工具栏有续写按钮
- [x] Checkpoint 73: 快捷键 Ctrl+I 触发续写
- [x] Checkpoint 74: AIWorker 实例保存在 self 中防止被 GC

## QSS 主题适配
- [x] Checkpoint 75: dark.qss 包含 `#ai_panel` 样式
- [x] Checkpoint 76: light.qss 包含 `#ai_panel` 样式
- [x] Checkpoint 77: 暗色主题下 AI 面板视觉协调
- [x] Checkpoint 78: 亮色主题下 AI 面板视觉协调

## 综合验证
- [x] Checkpoint 79: 应用启动时 AIManager 自动初始化，不报错
- [x] Checkpoint 80: 未配置任何提供商时，续写按钮显示提示"请先配置 AI 提供商"
- [x] Checkpoint 81: 配置 OpenAI 后，续写生成内容流式插入编辑器
- [x] Checkpoint 82: 生成过程中可取消，已生成内容保留
- [x] Checkpoint 83: API Key 无效时显示"API Key 无效"而非崩溃
- [x] Checkpoint 84: 网络不通时显示"网络连接失败"而非崩溃
- [x] Checkpoint 85: 暗色/亮色主题切换后 AI 面板样式正常

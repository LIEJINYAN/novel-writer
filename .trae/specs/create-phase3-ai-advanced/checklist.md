# Phase 3 第二批：AI 高级功能 - 验证检查清单

## 依赖与基础设施
- [x] Checkpoint 1: requirements.txt 包含 `anthropic>=0.30` 和 `google-generativeai>=0.6.0`
- [x] Checkpoint 2: `import anthropic` 和 `import google.generativeai` 在 venv 中成功

## Anthropic 适配器
- [x] Checkpoint 3: `AnthropicProvider` 继承 `BaseAIProvider`
- [x] Checkpoint 4: `name` 属性为 `"anthropic"`，`display_name` 为 `"Anthropic"`
- [x] Checkpoint 5: `default_models` 包含 `claude-sonnet-4`、`claude-haiku-3-5`
- [x] Checkpoint 6: 使用 anthropic Python SDK（`from anthropic import Anthropic`）
- [x] Checkpoint 7: `chat()` 方法正确调用 Messages API
- [x] Checkpoint 8: `chat_stream()` 正确 yield 流式 chunk
- [x] Checkpoint 9: 错误映射：AuthenticationError → AIAuthenticationError

## Google Gemini 适配器
- [x] Checkpoint 10: `GeminiProvider` 继承 `BaseAIProvider`
- [x] Checkpoint 11: `name` 属性为 `"gemini"`，`display_name` 为 `"Google Gemini"`
- [x] Checkpoint 12: `default_models` 包含 `gemini-2.0-flash`、`gemini-2.0-pro`
- [x] Checkpoint 13: 使用 google-generativeai SDK
- [x] Checkpoint 14: `chat()` 和 `chat_stream()` 正确调用 GenerativeModel API
- [x] Checkpoint 15: 连接失败时抛出合适异常

## 提供商注册
- [x] Checkpoint 16: `ai_manager.init()` 后注册了 5 个提供商（OpenAI、DeepSeek、Ollama、Anthropic、Gemini）
- [x] Checkpoint 17: `list_providers()` 返回全部 5 个提供商
- [x] Checkpoint 18: AI 设置对话框显示全部 5 个提供商
- [x] Checkpoint 19: 各提供商配置独立保存和加载

## 提示词模板扩展
- [x] Checkpoint 20: `PolishTemplate` 渲染生成 system + user 消息
- [x] Checkpoint 21: `PolishTemplate` 支持润色风格参数
- [x] Checkpoint 22: `RewriteTemplate` 渲染生成 system + user 消息
- [x] Checkpoint 23: `RewriteTemplate` 支持改写方向参数
- [x] Checkpoint 24: `AnalyzeTemplate` 渲染生成包含章节全文的提示词
- [x] Checkpoint 25: 所有新模板在 `PROMPT_REGISTRY` 中注册

## AI 编辑服务（润色/重写）
- [x] Checkpoint 26: `polish()` 方法签名正确：接受文本和润色风格
- [x] Checkpoint 27: `rewrite()` 方法签名正确：接受文本和改写方向
- [x] Checkpoint 28: 无选中文本时润色/重写按钮禁用（已通过 Agent 模式实现）
- [x] Checkpoint 29: 流式输出替换选中文本而非追加
- [x] Checkpoint 30: 错误处理不崩溃

## AI 分析服务
- [x] Checkpoint 31: `analyze_chapter()` 方法签名正确
- [x] Checkpoint 32: 分析结果包含多个维度
- [x] Checkpoint 33: 分析结果显示在 AI 对话面板中

## AI 对话面板
- [x] Checkpoint 34: `AIChatPanel` 继承 `QWidget`
- [x] Checkpoint 35: 消息列表显示用户和 AI 消息
- [x] Checkpoint 36: 输入框 + 发送按钮正常工作
- [x] Checkpoint 37: Enter 发送，Shift+Enter 换行
- [x] Checkpoint 38: AI 回复流式显示
- [x] Checkpoint 39: 对话历史在会话中保持
- [x] Checkpoint 40: 清空对话功能正常
- [x] Checkpoint 41: 暗色/亮色主题下视觉协调

## 主窗口集成
- [x] Checkpoint 42: 右侧面板有"AI 对话"标签页
- [x] Checkpoint 43: 编辑器右键菜单有"AI 润色"（有选中时）
- [x] Checkpoint 44: 编辑器右键菜单有"AI 重写"（有选中时）
- [x] Checkpoint 45: 编辑器右键菜单有"AI 分析"
- [x] Checkpoint 46: Ctrl+Shift+P 触发润色
- [x] Checkpoint 47: Ctrl+Shift+R 触发重写
- [x] Checkpoint 48: AI 面板有润色/重写/分析按钮

## QSS 主题适配
- [x] Checkpoint 49: dark.qss 包含 `#ai_chat_panel` 样式
- [x] Checkpoint 50: light.qss 包含 `#ai_chat_panel` 样式
- [x] Checkpoint 51: 消息气泡在暗色和亮色主题下可读性良好

## 综合验证
- [x] Checkpoint 52: 应用启动时所有 5 个提供商自动注册，不报错
- [x] Checkpoint 53: Anthropic 配置后可通过 AI 面板选择并调用
- [x] Checkpoint 54: Gemini 配置后可通过 AI 面板选择并调用
- [x] Checkpoint 55: 选中文本 → 右键润色 → 流式替换文本
- [x] Checkpoint 56: 选中文本 → 右键重写 → 选择方向 → 流式替换文本
- [x] Checkpoint 57: 分析当前章节 → 结果展示在对话面板
- [x] Checkpoint 58: AI 对话面板可进行多轮自由对话
- [x] Checkpoint 59: 暗色/亮色主题切换后对话面板样式正常

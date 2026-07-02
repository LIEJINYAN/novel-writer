# AI 面板双模式架构 — 检查清单

## 工具注册中心
- [x] Checkpoint 1.1: `Tool` 数据类定义完整（name/description/parameters/handler/category/icon）
- [x] Checkpoint 1.2: `ToolRegistry` 实现 register/unregister/get/list
- [x] Checkpoint 1.3: `get_descriptions()` 生成 LLM 可读的工具描述
- [x] Checkpoint 1.4: 全局实例 `tool_registry` 可导入

## 基础工具
- [x] Checkpoint 2.1: `read_chapter` 工具注册并可用
- [x] Checkpoint 2.2: `continue_write` 工具注册并可用
- [x] Checkpoint 2.3: `polish_text` 工具注册并可用
- [x] Checkpoint 2.4: `rewrite_text` 工具注册并可用
- [x] Checkpoint 2.5: `analyze_chapter` 工具注册并可用
- [x] Checkpoint 2.6: 每个工具有完整的 description 和 parameters schema
- [x] Checkpoint 2.7: 每个工具返回 `{success, message, data}` 结构

## Agent 执行器
- [x] Checkpoint 3.1: `AgentExecutor` 接收 provider 和 config
- [x] Checkpoint 3.2: `execute()` 返回 Generator[AgentEvent]
- [x] Checkpoint 3.3: AgentEvent 支持 thinking/tool_call/tool_result/text/error/done 事件
- [x] Checkpoint 3.4: 自然语言"帮我分析第三章"触发 analyze_chapter 工具
- [x] Checkpoint 3.5: 自然语言"续写"触发 continue_write 工具
- [x] Checkpoint 3.6: 纯聊天内容不触发工具调用

## AI 面板双模式
- [x] Checkpoint 4.1: 面板顶部有 Chat/Agent 模式切换控件
- [x] Checkpoint 4.2: Chat 模式使用 chat_service 纯文字对话
- [x] Checkpoint 4.3: Agent 模式使用 AgentExecutor
- [x] Checkpoint 4.4: 工具调用在消息区展示为工具卡片
- [x] Checkpoint 4.5: 工具卡片可折叠展开
- [x] Checkpoint 4.6: 切换模式时对话历史保留
- [x] Checkpoint 4.7: 模型选择/AI 设置两个模式共享
- [x] Checkpoint 4.8: 切换模式不中断正在进行的生成

## QSS 主题
- [x] Checkpoint 5.1: 模式切换按钮在暗色主题下正常显示
- [x] Checkpoint 5.2: 模式切换按钮在亮色主题下正常显示
- [x] Checkpoint 5.3: 工具卡片在两种主题下可读

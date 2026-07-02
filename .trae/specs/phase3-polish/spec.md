# Phase 3 体验打磨

## Why

Phase 3 功能全部完成但用户体验有粗糙之处：对话不持久化（重启丢失）、Agent 工具太少、流式输出有延迟、温度调节不方便。四个问题都集中在 AI 交互体验上，一次性打磨到位。

## What Changes

| 改动 | 说明 |
|------|------|
| 对话持久化 | Chat/Agent 历史保存到 SQLite，重启可恢复 |
| 工具扩充 | 新增 search_web、preview_html、list_chapters 3 个工具 |
| 流式优化 | QTimer 轮询 → QThread 信号驱动，消除 50ms 延迟 |
| 温度恢复 | 在 Chat 输入框上方加一个小型温度滑动条（窄条，不占空间） |
| 快捷键 | Ctrl+Shift+P 润色、Ctrl+Shift+R 重写、Ctrl+Shift+A 分析 |

## Impact

- `core/ai/chat_service.py` — 历史持久化（JSON 文件存储）
- `core/ai/agent/tools/search_web.py` — 新增搜索工具
- `core/ai/agent/tools/preview_html.py` — 新增预览工具
- `core/ai/agent/tools/list_chapters.py` — 新增章节列表工具
- `ui/sidebar/ai_panel.py` — 流式改用 QThread + 温度滑块恢复 + 快捷键注册
- `ui/main_window.py` — 添加 3 个 AI 快捷键

## Requirements

### FR-1: 对话持久化
- 聊天历史保存到 `~/.novel-writer/chat_history/` 目录
- 每个会话一个 `.json` 文件
- 文件格式：`{session_id}.json` → `[{"role": "user", "content": "..."}, ...]`
- 自动加载：启动时扫描目录，恢复会话列表
- 自动保存：每次 AI 回复完成后写入文件
- 最近 20 个会话的摘要显示在会话下拉框中（超出则清理最旧的）

### FR-2: 新增 Agent 工具
- `search_web(query)` — 调用搜索引擎（requests + 简易解析），返回搜索结果摘要
- `preview_html(html_content)` — 将 HTML 写入临时文件并用默认浏览器打开
- `list_chapters(project_id)` — 列出项目所有章节的 ID 和标题
- 注册到 tool_registry
- 不是必选的，第一个不需要依赖外部服务

### FR-3: 流式输出优化
- 创建 `StreamWorker(QThread)` 类，在独立线程中消费 Generator
- 通过 Signal 发送文本块到 UI 线程
- 移除现有的 QTimer 轮询机制
- 响应时间从 50ms 降到真正的流式（< 5ms）

### FR-4: 温度滑块
- 在 Chat 输入框上方添加一个小型水平滑块
- 宽度自适应，不额外占行
- 数值范围 0.0-2.0，步长 0.1，默认 0.8
- 当前值显示在滑块右侧（小字）

### FR-5: AI 快捷键
- Ctrl+Shift+P: 润色选中文本（已有信号，连接即可）
- Ctrl+Shift+R: 重写选中文本
- Ctrl+Shift+A: 分析当前章节
- 编辑器无焦点时不响应

## Out of Scope
- Phase 4 角色/情节追踪
- 对话历史多设备同步
- 插件系统

## Acceptance Criteria

### AC-1: 持久化
- 发送消息后重启应用 → 会话列表和内容恢复
- 20+ 会话时最旧的被清理

### AC-2: 新工具
- `search_web("Python教程")` 返回搜索结果
- `list_chapters(1)` 返回项目 1 的所有章节
- Agent 模式下可识别并调用新工具

### AC-3: 流式
- 两次文本块间隔 < 10ms（视觉上连续）
- 取消生成立即停止

### AC-4: 温度
- 滑块在输入框上方可见
- 调整后对 AI 输出有实际影响

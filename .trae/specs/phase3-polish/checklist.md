# Phase 3 体验打磨 - 检查清单

## 工具扩充
- [x] Checkpoint 1.1: `search_web` 工具注册到 tool_registry
- [x] Checkpoint 1.2: `list_chapters` 工具注册到 tool_registry
- [x] Checkpoint 1.3: `preview_html` 工具注册到 tool_registry
- [x] Checkpoint 1.4: `tool_registry.count` 从 5 增加到 8

## 流式优化
- [x] Checkpoint 2.1: `StreamWorker(QThread)` 实现 chunk_received/finished/error 信号
- [x] Checkpoint 2.2: Chat 模式使用 StreamWorker
- [x] Checkpoint 2.3: Agent 模式使用 StreamWorker
- [x] Checkpoint 2.4: 旧 QTimer 轮询代码已移除
- [x] Checkpoint 2.5: `stop()` 方法可取消生成

## 对话持久化
- [x] Checkpoint 3.1: 发送消息后 `.json` 文件写入 `~/.novel-writer/chat_history/`
- [x] Checkpoint 3.2: 重启应用后会话列表恢复
- [x] Checkpoint 3.3: 点击历史会话加载历史消息
- [x] Checkpoint 3.4: 超过 20 个会话时清理最旧的

## 温度滑块
- [x] Checkpoint 4.1: 滑块在输入框上方
- [x] Checkpoint 4.2: 数值范围 0.0-2.0，默认 0.8
- [x] Checkpoint 4.3: `get_temperature()` 返回滑块值
- [x] Checkpoint 4.4: 滑块不额外占行（maxHeight=16）

## AI 快捷键
- [x] Checkpoint 5.1: Ctrl+Shift+P 触发润色
- [x] Checkpoint 5.2: Ctrl+Shift+R 触发重写
- [x] Checkpoint 5.3: Ctrl+Shift+A 触发分析
- [x] Checkpoint 5.4: 编辑器菜单显示 AI 操作项

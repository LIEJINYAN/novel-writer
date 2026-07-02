# Phase 3 体验打磨 - 实现计划

## 第一批：工具扩充 + 流式优化（高优先级）

### [x] Task 1: 新增 Agent 工具（3 个）

- **Priority**: high
- **Depends On**: None（依赖 tool_registry，已存在）
- **Description**:
  - 创建 `core/ai/agent/tools/search_web.py`
  - 创建 `core/ai/agent/tools/list_chapters.py`
  - 创建 `core/ai/agent/tools/preview_html.py`
  - 更新 `core/ai/agent/tools/__init__.py`
- **Verification**: `tool_registry.count` 从 5 → 8

### [x] Task 2: 流式输出优化（QThread 替代 QTimer）

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 添加 `StreamWorker(QThread)` 类
  - 修改 `_send_chat` 和 `_send_agent` 改用 StreamWorker
  - 移除旧 QTimer 轮询代码
- **Verification**: 流式输出无明显卡顿

---

## 第二批：持久化 + 温度 + 快捷键（中优先级）

### [x] Task 3: 对话历史持久化

- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 修改 `core/ai/chat_service.py`：JSON 文件持久化到 `~/.novel-writer/chat_history/`
  - 加载/保存/清理逻辑
- **Verification**: 发送消息后重启可恢复

### [x] Task 4: 温度滑块恢复

- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 在输入框上方添加窄条温度滑块
  - `get_temperature()` 从滑块取值
- **Verification**: 滑块可拖动，值正确

### [x] Task 5: AI 快捷键注册

- **Priority**: low
- **Depends On**: None
- **Description**:
  - Ctrl+Shift+P(润色) / R(重写) / A(分析)
  - 编辑菜单显示 AI 操作项
- **Verification**: 快捷键可触发对应操作

# Task Dependencies
- 全部 5 个 Task 无依赖，可并行执行

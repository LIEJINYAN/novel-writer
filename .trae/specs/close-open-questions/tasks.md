# Tasks

## Task 1: 编辑器行号显示
- [x] SubTask 1.1: EditorWidget 已有 LineNumberArea
- [x] SubTask 1.2: 行号与文本同步滚动（updateRequest 连接）
- [x] SubTask 1.3: QSS 中已定义行号区域颜色

## Task 2: 撤销/重做 UI 补充
- [x] SubTask 2.1: 工具栏添加撤销/重做按钮 ✅ 刚完成
- [x] SubTask 2.2: Ctrl+Z / Ctrl+Y 快捷键（QKeySequence.Undo/Redo）
- [x] SubTask 2.3: 按钮状态随 Undo/Redo 栈变化（undoAvailable/redoAvailable 信号连接）

## Task 3: 自动保存配置
- [x] SubTask 3.1: AI 设置对话框已含自动保存配置
- [x] SubTask 3.2: QSpinBox 范围 10-300，默认 30
- [x] SubTask 3.3: QSettings 存储，`_reload_autosave_interval()` 读取
- [x] SubTask 3.4: 菜单"设置 → AI 设置"已连接

## Task 4: 续写字数选择
- [x] SubTask 4.1: AIPanel 已有 QComboBox（500-2000，可编辑）
- [x] SubTask 4.2: `continue_write_requested` 信号携带 int 字数参数
- [x] SubTask 4.3: AIWorker / WritingAIService 接收 `max_tokens` 参数
- [x] SubTask 4.4: PromptTemplate 使用字数参数控制生成长度

## Task 5: 拖拽排序确认 + 撤销
- [x] SubTask 5.1: `_on_tree_rows_moved` 有 toast 确认
- [x] SubTask 5.2: 取消还原（snapshot 机制）
- [x] SubTask 5.3: `_undo_reorder` 使用 snapshot 恢复
- [x] SubTask 5.4: 撤销后项目树刷新

## Task 6: 大纲面板跳转
- [x] SubTask 6.1: `node_clicked` → `_on_node_chapter_clicked` → `navigate_to_chapter` 信号
- [x] SubTask 6.2: `navigate_to_chapter` 连接 `_open_chapter_editor`，已打开则切换标签页

# Task Dependencies
全部无依赖，所有任务在本次开始前已基本实现。本次仅补了撤销/重做工具栏按钮。

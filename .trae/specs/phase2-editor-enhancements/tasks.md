# Phase 2 编辑系统（第二批）- The Implementation Plan

## [x] Task 1: 右侧面板容器改造
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 将右侧 Dock 的内容从简单 QLabel 改造为 QTabWidget 多面板
  - 两个标签页："大纲" 和 "统计"
  - 每个标签页对应一个面板 widget（先放占位，后续 Task 填充）
  - 修改 `ui/main_window.py` 的 `_init_docks` 方法
  - 面板 objectName 设置为 `sidebar_tabs`
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 右侧面板有两个标签页
  - `human-judgement` TR-1.2: 标签页切换正常，样式与主题协调
- **Notes**: 先搭容器，内容由后续 Task 填充

## [x] Task 2: 大纲面板
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 创建 `ui/sidebar/outline_panel.py` 大纲面板组件
  - 从写作方法注册表（`core/methods/registry.py`）读取当前项目的写作方法节点
  - 每个节点显示：名称、描述、章节范围
  - 显示进度条（根据当前章节字数估算进度）
  - 点击节点可跳转到对应章节范围（如果有对应章节）
  - 项目打开/切换时刷新大纲内容
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 模块可正常导入，OutlinePanel 类可实例化
  - `programmatic` TR-2.2: 能正确从注册表读取 7 种方法的节点
  - `human-judgement` TR-2.3: 节点列表显示清晰，进度条直观
- **Notes**: 进度估算：按章节号/总章节数 或 字数/目标字数

## [x] Task 3: 统计面板
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 创建 `ui/sidebar/stats_panel.py` 统计面板组件
  - 显示统计项：
    - 项目总字数
    - 章节总数
    - 分卷数
    - 目标字数进度条（如果设置了目标）
    - 平均每章字数
    - 今日新增字数（可选，简化版可不做）
  - 项目打开/切换、章节保存时刷新统计
  - 使用 QProgressBar 显示进度
- **Acceptance Criteria Addressed**: AC-3, AC-11
- **Test Requirements**:
  - `programmatic` TR-3.1: 模块可正常导入，StatsPanel 类可实例化
  - `programmatic` TR-3.2: 统计数据计算正确（总字数=各章字数之和）
  - `human-judgement` TR-3.3: 统计信息布局清晰，进度条直观
- **Notes**: 统计数据从数据库实时查询，不缓存（项目小，性能足够）

## [x] Task 4: 搜索替换面板
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 创建 `ui/components/search_panel.py` 搜索替换面板组件
  - 功能：搜索输入框、替换输入框（可折叠/展开）、搜索按钮、上一个/下一个、替换、全部替换
  - 显示匹配计数（"第 3 个，共 12 个"）
  - 支持大小写敏感切换（可选，简化版可默认不敏感）
  - 信号：search_next、search_prev、replace、replace_all
  - Ctrl+F 打开搜索面板，Esc 关闭
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: 模块可正常导入，SearchPanel 类可实例化
  - `programmatic` TR-4.2: 所有按钮和输入框正常工作
  - `human-judgement` TR-4.3: 面板布局紧凑，操作便捷
- **Notes**: 面板放编辑器底部，类似 VSCode 的搜索栏

## [x] Task 5: 全文搜索服务
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 在 `services/chapter_service.py` 中添加搜索方法
  - `search_in_project(project_id, keyword) -> list`：在项目所有章节中搜索，返回匹配列表
  - 每个匹配项包含：chapter_id、chapter_title、match_count、snippet（上下文片段）
  - 使用 SQL LIKE 查询（不区分大小写）
  - 在主窗口中集成：底部搜索栏，输入后实时显示结果列表
  - 点击结果跳转到对应章节并高亮匹配文本
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: search_in_project() 正确返回匹配结果
  - `programmatic` TR-5.2: 点击结果能正确打开章节并定位
  - `human-judgement` TR-5.3: 搜索响应快速，结果展示清晰
- **Notes**: 搜索结果列表可以用 QListWidget 展示；高亮使用 QTextEdit 的 extraSelections

## [x] Task 6: 项目树拖拽排序
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 启用 QTreeWidget 的拖拽功能（setDragEnabled, setAcceptDrops, setDropIndicatorShown）
  - 设置拖拽模式：InternalMove（内部移动）
  - 实现章节拖拽：
    - 同一分卷内拖拽 → 重新编号章节号
    - 跨分卷拖拽 → 修改 volume_id 并在新分卷重新编号
  - 实现分卷拖拽：调整 sort_order
  - 拖拽完成后更新数据库
  - 刷新项目树显示
- **Acceptance Criteria Addressed**: AC-7, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-6.1: 章节拖拽后数据库中 chapter_number 正确更新
  - `programmatic` TR-6.2: 分卷拖拽后 sort_order 正确更新
  - `programmatic` TR-6.3: 跨分卷拖拽后 volume_id 和 chapter_number 都正确
  - `human-judgement` TR-6.4: 拖拽操作流畅，视觉反馈清晰
- **Notes**: 重写 dropEvent 或使用 itemChanged 信号检测位置变化；拖拽后刷新 _open_chapters 映射（因为章节号变了标签标题要更新）

## [x] Task 7: 主窗口集成搜索面板
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - 在主窗口中添加底部搜索面板（默认隐藏）
  - Ctrl+F 切换显示/隐藏搜索面板
  - Esc 隐藏搜索面板
  - 搜索面板与编辑器联动：输入搜索词后高亮所有匹配项
  - 上一个/下一个按钮在匹配项间跳转
  - 替换功能：替换当前、全部替换
  - 搜索面板样式适配暗色/亮色主题
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: Ctrl+F 显示/隐藏搜索面板
  - `human-judgement` TR-7.2: 搜索高亮正确显示
  - `human-judgement` TR-7.3: 替换功能正常工作
- **Notes**: 搜索面板用 QWidget 加 QVBoxLayout 放编辑器下方；用 setVisible 控制显示

## [x] Task 8: QSS 主题适配
- **Priority**: low
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 暗色主题：大纲面板、统计面板、搜索面板的 QSS 样式
  - 亮色主题：同上
  - 进度条样式（QProgressBar）
  - 搜索结果高亮样式
  - 确保所有新组件在两个主题下都正常显示
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `human-judgement` TR-8.1: 暗色主题下所有新组件视觉舒适
  - `human-judgement` TR-8.2: 亮色主题下所有新组件视觉舒适
  - `human-judgement` TR-8.3: 切换主题时所有组件即时更新样式
- **Notes**: 参考现有 dark.qss 和 light.qss 的命名约定

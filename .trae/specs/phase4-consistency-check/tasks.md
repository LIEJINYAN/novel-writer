# Phase 4-C：一致性检查 - 实现计划

## [x] Task 1: 一致性检查服务

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `services/consistency_service.py`，`consistency_service` 单例
  - `CheckResult` 数据类：category(角色/时间线/情节), severity(error/warning/info), message, chapter_id(可选), detail
  - `run_rules(project_id) -> list[CheckResult]`：执行 3 类规则：
    1. **角色别名检测**：从 `Chapter` 表加载所有章节正文，对每个已加入项目的角色（含 aliases），检查正文中是否使用了其他角色的 name/aliases。如章节 A 用户角色 1 的别名"小狼"引用，但那是角色 2 的别名 → warning
    2. **角色出场前置**：对比 `ChapterAppearance.created_at` 和 `Character.created_at`，如果角色在某个出场记录中的时间早于角色创建时间 → error
    3. **时间线排序**：遍历 `TimelineEvent`，对 `story_date` 尝试解析为数字序号，检查 `sort_order` 是否递增 → warning
  - `run_ai_check(project_id, callback)`：调用 `analysis_service.analyze_chapter()` 传给当前章节的 `content`，复用现有 AI worker 流式输出机制。简化实现：使用 `core.ai.ai_worker.AIWorker` 直接调用 `consistency_check` 模板。
  - 遵循现有 Service 模式，无状态，每次扫描重新生成结果
- **Verification**: `run_rules` 返回正确结构的结果列表，`run_ai_check` 返回 AIWorker 实例

## [x] Task 2: 检查面板

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `ui/sidebar/check_panel.py`
  - `CheckPanel(QWidget)`：
    - 连接 `signal_bus.project_opened` / `project_closed`
    - `clear()` 方法
  - 顶部按钮栏：
    - "规则扫描"按钮 — 调用 `run_rules`，填充树形视图
    - "AI 深度检查"按钮 — 调用 `run_ai_check`，创建 `AIWorker` 线程
      - 无 AI 配置时禁用按钮 + 提示"请先在 AI 设置中配置提供商"
      - 运行时显示"AI 检查中...", 完成后更新
  - 中间：QTreeWidget，两级结构：
    - 顶层：类别节点（"角色问题"/"时间线问题"/"情节问题"/"AI 分析"），显示数量
    - 子节点：问题详情，按 severity 着色
      - error = #E74C3C (红)
      - warning = #F39C12 (黄)
      - info = #95A5A6 (灰)
    - 双击子节点：如果有 chapter_id，发射 `navigate_to_chapter(chapter_id)` 信号
  - 底部：QLabel 状态显示
- **Verification**: 规则扫描展示归类结果，AI 检查流式输出到 AI 分析节点下

## [x] Task 3: 主窗口集成 + QSS

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 修改 `ui/main_window.py`：
    - 引入 `CheckPanel`
    - 侧边栏添加"检查"标签页
    - 连接 `navigate_to_chapter` 到 `_open_chapter_editor`
    - close 时调用 `check_panel.clear()`
  - 修改 `ui/styles/dark.qss` / `light.qss`：
    - `QWidget#check_panel` 样式
    - `.check-error` / `.check-warning` / `.check-info` 颜色类
- **Verification**: 侧边栏显示"检查"标签页，双击问题跳转章节

# Task Dependencies
- Task 1 → Task 2 → Task 3

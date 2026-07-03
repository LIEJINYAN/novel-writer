# Phase 4-C：一致性检查 Spec

## Why

小说写到中后期，角色名字混淆、时间线矛盾、情节漏洞在所难免。当前软件没有任何工具帮助作者发现这些问题。规则引擎可以秒级扫描出明显的矛盾，AI 则可以发现更深层的逻辑问题。

## What Changes

| 改动 | 说明 |
|------|------|
| 规则检测引擎 | 3 类规则扫描：角色别名冲突、角色出场前置、时间线排序异常 |
| AI 深度检查 | 复用已有的 `consistency_check`/`plot_check`/`character_check` 模板 |
| 检查面板 | 侧边栏"检查"标签页，结果分类展示+着色+点击跳转 |
| 一键运行 | 打开项目自动运行规则扫描，AI 检查需手动点击 |

## Impact

- **新增** `services/consistency_service.py` — 规则引擎 + AI 检查编排
- **新增** `ui/sidebar/check_panel.py` — 检查结果面板
- **修改** `ui/main_window.py` — 侧边栏添加"检查"标签页，连接跳转信号
- **修改** `ui/styles/dark.qss` / `light.qss` — 检查面板样式

## Requirements

### FR-1: 规则检测引擎

`ConsistencyService` 提供 3 类规则检查，全部是本地扫描，秒级返回：

**角色别名检测**：遍历项目所有章节正文，如果一个章节中角色 A 使用了角色 B 的别名，标记为 warning。

**角色出场前置**：如果角色在某一章"出场"（`ChapterAppearance`），但该角色在后续章节才创建（`created_at`），标记为 error。

**时间线排序**：如果 `TimelineEvent` 的 `story_date` 文本可解析为数字序号（如"第3章"、"事件2"），检查 `sort_order` 是否与序号合理对应。

所有检查结果统一返回格式：
```python
{"category": "角色" | "时间线" | "情节",
 "severity": "error" | "warning" | "info",
 "message": "描述文本",
 "chapter_id": int | None,  # 可跳转的章节
 "detail": str}             # 详情说明
```

### FR-2: AI 深度检查

调用 `core.ai.analysis_service` 执行 `consistency_check` 模板，展示结果到面板（流式输出，如同当前 AI 对话模式）。

### FR-3: 检查面板

- 侧边栏标签页"检查"
- 顶部：**"规则扫描"**（本地） + **"AI 深度检查"**（需要 AI 配置）两个按钮
- 中间：QTreeWidget 结果树
  - 顶层按类别分组："角色问题"、"时间线问题"、"情节问题"、"AI 分析"
  - 子节点：问题详情，着色 — error=红色，warning=黄色，info=灰色
  - 可点击跳转：如果问题有关联章节，双击跳转到该章节
- 底部：状态标签（"扫描完成：发现 3 个问题" / "AI 检查中..."）

#### 场景：运行规则检查
- **WHEN** 用户点击"规则扫描"
- **THEN** 秒级返回结果，面板显示问题数量和详情

#### 场景：AI 深度检查
- **WHEN** 用户点击"AI 深度检查"
- **THEN** 调用 AI 流式输出结果到面板

#### 场景：点击问题跳转
- **WHEN** 用户双击有 `chapter_id` 的问题
- **THEN** 发射 `navigate_to_chapter(chapter_id)` 信号

### FR-4: 主窗口集成

- 侧边栏添加"检查"标签页
- 连接 `navigate_to_chapter` 信号到章节打开方法
- close 项目时清空检查面板

## Out of Scope
- 自动保存检查结果到数据库
- 检查规则自定义配置
- 批量自动修复

## Acceptance Criteria

### AC-1
- 点击"规则扫描"后展示检测结果
- 角色别名/出场前置/时间线排序 3 类规则正确触发

### AC-2
- 有问题的条目双击可跳转到对应章节
- 无关联章节的问题条目不可跳转

### AC-3
- AI 深度检查调通并流式展示结果
- 未配置 AI 时按钮禁用并有提示

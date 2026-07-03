# Phase 4-A：关系追踪 + 时间线 - 实现计划

## [x] Task 1: 关系/派系/时间线数据模型

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `models/relationship.py`，包含 4 个模型：
    - `Relationship`：project_id, character_a_id, character_b_id, relationship_type, description, current_relation, intensity(1-10), notes, created_at, updated_at
    - `RelationshipChange`：relationship_id, chapter_id, change_type, old_relation, new_relation, description, created_at
    - `Faction`：project_id, name, description, leader_id(→characters.id, SET NULL), goals(Text), status, created_at, updated_at
    - `FactionMember`：faction_id, character_id, role_in_faction, is_core_member, sort_order
  - 创建 `models/timeline.py`：
    - `TimelineEvent`：project_id, event_name, description, story_date, chapter_id(SET NULL), location, importance, sort_order, created_at, updated_at
  - 所有 FK 使用 `ondelete` 策略，`project_id` 全部 `ondelete="CASCADE"`
  - 更新 `models/__init__.py` 导出新模型
- **Verification**: `from models import Relationship, Faction, FactionMember, RelationshipChange, TimelineEvent` 成功

## [x] Task 2: 关系服务

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `services/relationship_service.py`，`relationship_service` 单例
  - **关系 CRUD**：
    - `create(project_id, character_a_id, character_b_id, ...)` → 验证不重复 + 自动记录 RelationshipChange(change_type="新建")
    - `get(relationship_id)` → 含变化历史、角色信息
    - `update(relationship_id, **data)` → 比较变化字段，自动记录 RelationshipChange(change_type="变化")
    - `delete(relationship_id)` → 软删除
    - `list(project_id, search="")` → 按角色名搜索
  - **派系 CRUD**：
    - `create_faction(project_id, name, ...)` → 含成员
    - `get_faction(faction_id)` → 含领导者名、成员列表
    - `update_faction` / `delete_faction`
    - `list_factions(project_id)` → 含成员数
    - `add_member` / `remove_member`
  - 遵循现有 `CharacterService` 模式：session 管理、异常处理
- **Verification**: 创建关系和派系 → 数据库中对应记录正确，修改关系自动记录变化

## [x] Task 3: 时间线服务

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `services/timeline_service.py`，`timeline_service` 单例
  - `create(project_id, event_name, ...)` → 新建事件
  - `get(event_id)` → 含章节标题
  - `update` / `delete` / `batch_delete`
  - `list(project_id, search="")` → 按 `sort_order` 排序
- **Verification**: 创建/编辑/删除事件操作正常，列表按 sort_order 排序

## [x] Task 4: 关系对话框

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `ui/dialogs/relationship_dialog.py`
  - `RelationshipDialog(QDialog)`：
    - 角色 A / 角色 B 下拉（QComboBox，列出项目角色，可互换）
    - 关系类型下拉（QComboBox：盟友/敌对/恋人/家人/师徒/中立/其他）
    - 强度滑动条（QSlider，1-10，显示数值）
    - 关系描述（QTextEdit）
    - 变化历史列表（QListWidget，只读，显示 "第X章: A→B"）
    - 保存验证：角色 A ≠ 角色 B
  - 创建 `ui/dialogs/faction_dialog.py`
  - `FactionDialog(QDialog)`：
    - 派系名称、描述、状态下拉
    - 领导者下拉（QComboBox，可选"无"）
    - 目标（QTextEdit，每行一条）
    - 成员列表（QListWidget + 添加/移除按钮）
    - 添加成员时弹出角色选择对话框（QInputDialog 或用 QComboBox 下拉选择）
  - 样式遵循现有对话框风格（`QFormLayout` + `QDialogButtonBox`）
- **Verification**: 对话框打开/保存/取消正常，数据写入数据库

## [x] Task 5: 关系面板

- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 创建 `ui/sidebar/relationship_panel.py`
  - `RelationshipPanel(QWidget)`：
    - 顶部：搜索框 + 新建关系/新建派系按钮
    - 中间：QTabWidget，两个子标签页
      - **关系表**：QTableWidget，列：角色A、角色B、类型、强度
      - **派系列表**：QTableWidget，列：派系名、领导者、成员数、状态
    - 双击行 → 打开对应对话框
    - 右键菜单：编辑/删除
    - 打开项目时自动加载数据
- **Verification**: 面板显示关系/派系数据，双击编辑，右键删除

## [x] Task 6: 时间线事件对话框 + 时间线面板

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 `ui/dialogs/timeline_event_dialog.py`
  - `TimelineEventDialog(QDialog)`：
    - 事件名称、描述（QTextEdit）
    - 故事内日期（QLineEdit）
    - 地点（QLineEdit）
    - 关联章节（QComboBox，列出项目章节，可选"无"）
    - 重要性（QComboBox：核心/重要/次要）
  - 创建 `ui/sidebar/timeline_panel.py`
  - `TimelinePanel(QWidget)`：
    - 顶部：搜索框 + 新建事件按钮
    - 中间：QListWidget，每项显示格式：
      - `[核心] 第5章: 主角觉醒 — 第3年春`
      - 核心=红色圆点、重要=蓝色圆点、次要=灰色圆点
    - 双击行 → 打开 TimelineEventDialog
    - 右键菜单：编辑/删除
    - 支持 shift 多选后右键批量删除
- **Verification**: 面板显示事件列表，颜色标记正确，新建/编辑/删除正常

## [x] Task 7: 主窗口集成

- **Priority**: high
- **Depends On**: Task 5, Task 6
- **Description**:
  - 修改 `ui/main_window.py`：
    - 在 `_init_sidebar()` 中添加"关系"标签页（RelationshipPanel）
    - 在 `_init_sidebar()` 中添加"时间线"标签页（TimelinePanel）
    - 遵循现有"角色""情节"标签页的注册方式
    - 打开/切换项目时刷新这两个面板
  - 修改 `ui/styles/dark.qss` 和 `ui/styles/light.qss`：
    - `.relationship-panel` / `.timeline-panel` 基础背景
    - `.importance-core` (红色)、`.importance-major` (蓝色)、`.importance-minor` (灰色) 颜色
- **Verification**: 侧边栏显示"关系""时间线"标签页，数据与当前项目绑定

# Task Dependencies
- Task 1（数据模型）→ Task 2（关系服务）, Task 3（时间线服务）
- Task 2 → Task 4（关系对话框）, Task 5（关系面板）
- Task 3 → Task 6（时间线事件对话框+面板）
- Task 5, Task 6 → Task 7（主窗口集成）

# 并行执行建议
- Task 2 和 Task 3 无依赖，可并行
- Task 4 和 Task 5 顺序执行（对话框 → 面板调用对话框）

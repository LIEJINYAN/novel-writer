# 追踪系统视觉化组件 Spec

## Why

路线图 Phase 4 定义了追踪系统的视觉化组件，当前只实现了数据层（CRUD），可视化界面缺失。关系图谱、时间轴、出场记录、检查报告、世界观管理 UI 均为待实现状态。

## What Changes

1. **关系图谱** — 角色关系可视化（QGraphicsView + QGraphicsScene）
2. **时间轴可视化** — 时间线事件水平轴视图
3. **出场记录管理 UI** — 角色出场标记面板 + 频率分析
4. **冲突管理 UI** — 冲突列表和升级程度管理
5. **检查报告面板** — 一致性检查结果的可视化展示 + AI 修复建议
6. **世界观设定管理 UI** — 地点/规则/物品的树形管理

## Impact
- Affected code: `ui/sidebar/tracking_panel.py`、`ui/sidebar/character_panel.py`、`ui/dialogs/`、`core/tracking/`

## ADDED Requirements

### Requirement: 关系图谱
系统 SHALL 使用 QGraphicsView 绘制角色关系图谱。

#### Scenario: 可视化关系
- **WHEN** 用户打开追踪面板 → 关系标签页
- **THEN** 显示角色节点（圆形）和关系连线（带方向箭头和文字标签）
- **AND** 节点可拖拽布局，滚轮缩放

### Requirement: 时间轴可视化
系统 SHALL 提供水平时间轴视图。

#### Scenario: 查看时间线
- **WHEN** 用户查看时间线标签页
- **THEN** 事件按时间顺序排列在水平轴上
- **AND** 点击事件显示详情

### Requirement: 出场记录管理
系统 SHALL 提供角色出场记录面板。

#### Scenario: 标记出场
- **WHEN** 用户在角色编辑中勾选章节
- **THEN** 记录角色登场/缺席
- **AND** 显示出场频率统计

### Requirement: 冲突管理 UI
系统 SHALL 提供冲突列表管理界面。

### Requirement: 检查报告面板
系统 SHALL 显示一致性检查结果报告。

### Requirement: 世界观管理 UI
系统 SHALL 提供地点/规则/物品的树形管理。

## MODIFIED Requirements
无

## REMOVED Requirements
无

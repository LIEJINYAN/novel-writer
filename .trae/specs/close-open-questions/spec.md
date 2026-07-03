# 收尾 Open Questions Spec

## Why
汇总并解决各阶段 Spec 中遗留的 Open Questions，统一决策后落地实现。

## What Changes
- **编辑器行号**: 添加行号区域（gutter）
- **撤销/重做历史**: 补全 Undo/Redo 功能及 UI
- **自动保存配置**: 设置面板可配自动保存间隔
- **续写字数选择**: AI 续写时用户可选择字数
- **API Key 加密**: 已用 cryptography 库实现（仅确认）
- **Ollama 适配器**: 已用 httpx 实现（仅确认）
- **拖拽排序确认 + 撤销**: 分卷/章节拖拽时确认提示 + 撤销入口
- **大纲面板跳转**: 点击大纲面板节点跳转到对应章节编辑器

## Impact
- Affected specs: phase2-editor-system, phase2-editor-enhancements, create-phase3-ai-foundation
- Affected code: `editor_widget.py`, `main_window.py`, `search_panel.py`, `ai_panel.py`, `outline_panel.py`, `project_tree.py`, 新增设置面板

## ADDED Requirements

### Requirement: 编辑器行号
The system SHALL display line numbers in the editor's gutter area.

#### Scenario: 行号显示
- **WHEN** 用户打开编辑器
- **THEN** 编辑器左侧显示行号，与文本内容同步滚动

#### Scenario: 行号更新
- **WHEN** 用户增删行
- **THEN** 行号自动更新

### Requirement: 撤销/重做
The system SHALL provide Undo/Redo actions accessible via toolbar and keyboard shortcuts.

#### Scenario: 撤销
- **WHEN** 用户按下 Ctrl+Z 或点击撤销按钮
- **THEN** 编辑器回退一步操作

#### Scenario: 重做
- **WHEN** 用户按下 Ctrl+Y 或点击重做按钮
- **THEN** 编辑器重做一步操作

### Requirement: 自动保存配置
The system SHALL allow users to configure auto-save interval in a settings panel.

#### Scenario: 打开设置面板
- **WHEN** 用户点击菜单"设置 → 编辑器设置"
- **THEN** 弹出设置对话框，包含"自动保存间隔"输入框

#### Scenario: 修改自动保存间隔
- **WHEN** 用户修改自动保存间隔并保存
- **THEN** 自动保存定时器使用新间隔

### Requirement: 续写字数选择
The system SHALL allow users to set the word count for AI continuation via a spinbox or slider in the AI panel.

#### Scenario: 选择续写字数
- **WHEN** 用户点击"AI 续写"前在字数选择器中选择字数
- **THEN** 续写请求携带用户指定的字数参数，默认 2000

### Requirement: 拖拽排序确认 + 撤销
The system SHALL show a confirmation dialog before drag-sort operations and provide undo capability.

#### Scenario: 确认对话框
- **WHEN** 用户拖拽章节到新位置
- **THEN** 弹出确认对话框显示变更内容，有"确认"、"取消"选项

#### Scenario: 撤销
- **WHEN** 用户点击"撤销排序"按钮或在状态栏点击撤销链接
- **THEN** 章节顺序恢复为拖拽前的状态

### Requirement: 大纲面板跳转
The system SHALL navigate to the corresponding chapter in the editor when a node in the outline panel is clicked.

#### Scenario: 点击跳转
- **WHEN** 用户单击大纲面板中的章节节点
- **THEN** 编辑器切换到该章节的标签页

## MODIFIED Requirements

### Requirement: 搜索历史记录 (已实现)
**Change**: Open Question 中原本建议第一批不加，实际已实现。
**Current State**: 搜索/替换历史已持久化至 `search_history.json`，无需额外改动。

## REMOVED Requirements
无

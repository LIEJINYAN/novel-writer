# UI/UX 余量功能实现 Spec

## Why

`006_UIUX设计规范.md` 定义了 7 项功能在代码中只有占位或完全缺失：专注模式（F11）、字体缩放、底部 AI 对话面板、图标系统、对话框细节对齐、响应式布局策略、AI 打字机效果交互确认流程。

## What Changes

1. **专注模式** (F11)：隐藏所有面板和工具栏，编辑器全屏，当前段落高亮
2. **字体缩放**：Ctrl++/-/0 实现字号增减 2px 和重置
3. **底部 AI 对话面板**：新增 `QDialog` 浮动窗口，替代侧边栏 AI 面板的对话功能
4. **图标系统**：7 个自定义 SVG 图标，注册到 Qt 图标引擎
5. **新建项目对话框细节对齐**：字段顺序、默认值、尺寸与文档一致
6. **AI 设置对话框细节对齐**：Provider/Model/Temperature/MaxTokens 布局与文档一致
7. **响应式布局**：窗口 < 1000px 时自动收起一个侧栏

## Impact
- Affected specs: `006_UIUX设计规范.md` 第 2-11 节
- Affected code: `ui/main_window.py`、`ui/sidebar/ai_panel.py`、`ui/dialogs/new_project_dialog.py`、`ui/dialogs/ai_settings_dialog.py`、`resources/icons/`（新建）

## ADDED Requirements

### Requirement: 专注模式
系统 SHALL 提供专注模式，F11 切换。

#### Scenario: 专注模式开启
- **WHEN** 用户按 F11
- **THEN** 菜单栏、工具栏、左右侧栏、底部面板隐藏，编辑器区域最大化
- **AND** 状态栏保留显示
- **AND** 当前段落背景色高亮，其他内容降低不透明度

### Requirement: 字体缩放
系统 SHALL 支持编辑器字体实时缩放。

#### Scenario: 放大/缩小
- **WHEN** 用户按 Ctrl++
- **THEN** 编辑器字号增加 2px
- **WHEN** 用户按 Ctrl+0
- **THEN** 字号重置为初始值

### Requirement: 底部 AI 对话面板
系统 SHALL 提供可隐藏的底部 AI 对话浮动面板。

#### Scenario: 打开底部 AI 面板
- **WHEN** 用户按 Ctrl+Shift+A 或点击菜单
- **THEN** 底部出现 AI 对话面板，与侧边栏 AI 面板共享会话状态

### Requirement: 响应式布局
系统 SHALL 窗口宽度 < 1000px 时自动隐藏左侧栏。

#### Scenario: 窗口缩放
- **WHEN** 窗口宽度降至 1000px 以下
- **THEN** 左侧项目树面板自动隐藏
- **WHEN** 窗口宽度恢复 1400px 以上
- **THEN** 恢复原始布局

## MODIFIED Requirements
- `ui/dialogs/new_project_dialog.py` 字段顺序/默认值与文档 6.1 节一致
- `ui/dialogs/ai_settings_dialog.py` UI 布局与文档 6.2 节一致

## REMOVED Requirements
无

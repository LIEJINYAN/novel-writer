# UI/UX 设计对齐 Spec

## Why

`006_UIUX设计规范.md` 定义了完整的 UI/UX 设计规范（布局、QSS 主题、编辑器、面板、对话框、菜单、快捷键），但实际实现存在多处偏离：亮色和护眼黄主题缺失、菜单项（写作/Writing、追踪/Tracking）不全、快捷键有缺口、底部 AI 面板未实现。

## What Changes

1. 创建亮色主题 `light.qss` 和护眼黄主题 `sepia.qss`，按文档色板定义
2. 按文档补充缺失的菜单项（写作/Writing 七步菜单、追踪/Tracking 子菜单、专家模式子菜单）
3. 补充缺失的快捷键（Ctrl+W 关闭标签页、Ctrl+H 替换、Ctrl++/-/0 字体缩放等）
4. AI 面板按文档补充（温度滑块、Max Tokens 旋钮）
5. 补全状态栏信息（行数、段落数、项目名、AI 模型名）

## Impact
- Affected specs: `006_UIUX设计规范.md` 第 2-10 节
- Affected code: `ui/styles/`（新增 QSS 文件）、`ui/main_window.py`（菜单/快捷键）、`ui/sidebar/ai_panel.py`（AI 面板 UI）、`ui/main_window.py`（状态栏）

## ADDED Requirements

### Requirement: 亮色主题 light.qss
系统 SHALL 提供亮色主题 QSS 文件，使用文档定义的亮色色板。

#### Scenario: 主题切换
- **WHEN** 用户在视图 → 主题 → 亮色
- **THEN** 应用 `light.qss` 样式表

### Requirement: 菜单项补齐
系统 SHALL 补充文档定义的缺失菜单项。

#### Scenario: 写作菜单
- **WHEN** 查看菜单栏
- **THEN** 看到「写作」菜单含 7 步菜单项 + AI 审计
#### Scenario: 追踪菜单
- **WHEN** 查看菜单栏
- **THEN** 看到「追踪」菜单含情节检查、时间线、关系图谱等

### Requirement: 快捷键补齐
系统 SHALL 补充文档定义的缺失快捷键。

#### Scenario: 编辑器快捷键
- **WHEN** 按 `Ctrl+W`
- **THEN** 关闭当前标签页

## MODIFIED Requirements
### Requirement: 状态栏信息补齐
状态栏补充行数、段落数、项目名称、AI 提供商名。

## REMOVED Requirements
无

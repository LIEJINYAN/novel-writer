# Phase 2 编辑系统（第一批）- Product Requirement Document

## Overview
- **Summary**: 实现小说编辑器核心功能，包括章节编辑、分卷管理、章节 CRUD、字数统计和自动保存，让用户可以在应用中真正开始写作。
- **Purpose**: Phase 1 搭建了项目框架，Phase 2 第一批目标是让应用具备基础写作能力——用户可以打开项目、创建分卷和章节、编辑内容、自动保存。
- **Target Users**: 小说作者、内容创作者

## Goals
- 用户可以点击项目树中的章节，在编辑器中打开并编辑内容
- 用户可以新建、重命名、删除章节和分卷
- 编辑器实时显示字数统计（中文字数、段落数）
- 编辑内容自动保存到数据库，防止数据丢失
- 项目树右键菜单提供完整的操作入口

## Non-Goals (Out of Scope)
- 富文本格式化（加粗、斜体等）- 纯文本编辑即可
- AI 续写、润色等 AI 功能（Phase 3）
- 搜索替换功能（Phase 2 第二批）
- 拖拽排序（Phase 2 第二批）
- 从原版项目导入（Phase 2 第二批）
- 角色、情节追踪系统（Phase 4）

## Background & Context
- Phase 1 已完成：项目脚手架、SQLAlchemy + SQLite 数据层、Alembic 迁移、PySide6 主窗口、暗色/亮色主题、项目 CRUD、写作方法注册表
- 现有数据模型：Project → Volume → Chapter，Chapter 已有 content、word_count 等字段
- 现有信号总线：已定义 chapter_created/chapter_deleted/chapter_saved/chapter_switched/content_changed/word_count_updated 等信号
- 现有 UI：QTabWidget 作为中央编辑器区域，项目树在左侧 Dock 中，支持右键菜单（当前仅项目节点有操作）

## Functional Requirements

- **FR-1**: 章节编辑器 - 点击项目树中的章节节点，在中央标签页中打开编辑器，支持纯文本编辑
- **FR-2**: 多标签页管理 - 支持同时打开多个章节，标签页可关闭，切换标签页对应不同章节
- **FR-3**: 章节 CRUD - 通过右键菜单或菜单新建、重命名、删除章节
- **FR-4**: 分卷管理 - 通过右键菜单新建、重命名、删除分卷
- **FR-5**: 字数实时统计 - 编辑时实时统计中文字数和段落数，显示在状态栏
- **FR-6**: 自动保存 - 编辑内容后定时（默认 30 秒）自动保存到数据库
- **FR-7**: 手动保存 - 支持 Ctrl+S 手动保存当前章节
- **FR-8**: 项目树刷新 - 章节/分卷增删改后自动刷新项目树显示
- **FR-9**: 编辑状态指示 - 未保存的章节标签页显示修改标记（如 * 号）

## Non-Functional Requirements

- **NFR-1**: 章节打开时间 < 500ms（1 万字以内章节）
- **NFR-2**: 字数统计响应延迟 < 100ms（输入后立即更新）
- **NFR-3**: 自动保存不阻塞 UI（后台线程或异步）
- **NFR-4**: 编辑器支持 10 万字以上大章节不明显卡顿
- **NFR-5**: 与现有暗色/亮色主题完全兼容

## Constraints
- **Technical**: PySide6 + SQLAlchemy + SQLite，必须使用现有项目结构和编码风格
- **Business**: 第一批必须在合理时间内完成（约 1-2 周），聚焦核心编辑能力
- **Dependencies**: 依赖 Phase 1 已有的数据模型、信号总线、项目服务、主窗口框架

## Assumptions
- 纯文本编辑器使用 QPlainTextEdit（比 QTextEdit 更轻量，适合纯文本写作）
- 字数统计按中文字符计数（排除空白字符），段落数按换行分段
- 自动保存间隔默认 30 秒，可配置
- 删除章节和分卷使用软删除（is_deleted 标记）
- 新建章节时自动分配章节号（当前分卷最大章节号 +1）

## Acceptance Criteria

### AC-1: 点击章节打开编辑器
- **Given**: 用户已打开一个包含分卷和章节的项目
- **When**: 用户双击或单击项目树中的章节节点
- **Then**: 中央区域创建新标签页，显示章节标题和编辑器内容，标签页标题为章节名称
- **Verification**: `human-judgment`

### AC-2: 多标签页切换
- **Given**: 用户已打开多个章节标签页
- **When**: 用户点击不同标签页
- **Then**: 编辑器内容切换到对应章节，状态栏字数更新为当前章节字数
- **Verification**: `human-judgment`

### AC-3: 新建章节
- **Given**: 用户在项目树中选中一个分卷节点
- **When**: 用户右键选择"新建章节"
- **Then**: 弹出输入框让用户输入章节标题，确认后在该分卷末尾创建新章节，项目树刷新，自动打开新章节
- **Verification**: `human-judgment`

### AC-4: 重命名章节
- **Given**: 用户在项目树中选中一个章节节点
- **When**: 用户右键选择"重命名章节"
- **Then**: 弹出输入框显示当前标题，修改确认后章节标题更新，项目树和标签页同步更新
- **Verification**: `human-judgment`

### AC-5: 删除章节
- **Given**: 用户在项目树中选中一个章节节点
- **When**: 用户右键选择"删除章节"并确认
- **Then**: 章节被软删除，项目树移除该节点，如果该章节有打开的标签页则关闭
- **Verification**: `programmatic`

### AC-6: 新建分卷
- **Given**: 用户已打开一个项目
- **When**: 用户右键项目节点选择"新建分卷"
- **Then**: 弹出输入框让用户输入分卷名称，确认后创建新分卷，项目树刷新
- **Verification**: `human-judgment`

### AC-7: 重命名分卷
- **Given**: 用户在项目树中选中一个分卷节点
- **When**: 用户右键选择"重命名分卷"
- **Then**: 弹出输入框显示当前名称，修改确认后分卷名称更新，项目树同步更新
- **Verification**: `human-judgment`

### AC-8: 删除分卷
- **Given**: 用户在项目树中选中一个分卷节点
- **When**: 用户右键选择"删除分卷"并确认
- **Then**: 分卷及其下所有章节被软删除，项目树移除该分卷，已打开的章节标签页关闭
- **Verification**: `programmatic`

### AC-9: 实时字数统计
- **Given**: 用户正在编辑一个章节
- **When**: 用户输入或删除文字
- **Then**: 状态栏字数实时更新，显示中文字数和段落数
- **Verification**: `human-judgment`

### AC-10: 自动保存
- **Given**: 用户编辑了章节内容但未手动保存
- **When**: 距离上次修改超过自动保存间隔（默认 30 秒）
- **Then**: 内容自动保存到数据库，状态栏短暂显示"已自动保存"
- **Verification**: `human-judgment`

### AC-11: 手动保存
- **Given**: 用户正在编辑一个章节
- **When**: 用户按下 Ctrl+S 或点击保存按钮
- **Then**: 章节内容立即保存到数据库，状态栏显示"已保存"
- **Verification**: `human-judgment`

### AC-12: 未保存标记
- **Given**: 用户修改了章节内容但尚未保存
- **When**: 查看标签页标题
- **Then**: 标签页标题后显示 * 号表示未保存
- **Verification**: `human-judgment`

### AC-13: 保存后标记清除
- **Given**: 标签页显示未保存标记
- **When**: 内容被保存（自动或手动）
- **Then**: 标签页的 * 号消失
- **Verification**: `human-judgment`

### AC-14: 关闭标签页提示
- **Given**: 用户要关闭一个有未保存修改的标签页
- **When**: 用户点击标签页关闭按钮
- **Then**: 弹出确认对话框询问是否保存，可选"保存"、"不保存"、"取消"
- **Verification**: `human-judgment`

### AC-15: 主题兼容
- **Given**: 应用运行中
- **When**: 用户切换暗色/亮色主题
- **Then**: 编辑器、标签页、状态栏等所有新组件都正确切换样式
- **Verification**: `human-judgment`

## Open Questions
- [ ] 编辑器是否需要行号显示？（建议：第一批不加，后续加）
- [ ] 是否需要撤销/重做历史记录？（QPlainTextEdit 自带，默认启用）
- [ ] 自动保存间隔是否需要让用户配置？（建议：先固定 30 秒，后续加设置面板）

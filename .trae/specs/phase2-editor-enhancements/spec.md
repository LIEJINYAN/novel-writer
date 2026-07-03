# Phase 2 编辑系统（第二批）- Product Requirement Document

## Overview
- **Summary**: 实现编辑器增强功能，包括右侧面板（大纲+统计）、全文搜索替换、项目树拖拽排序，提升写作效率和用户体验。
- **Purpose**: Phase 2 第一批完成了核心编辑能力，第二批聚焦于提升写作体验——让作者能看到大纲和写作进度，快速定位内容，灵活调整章节顺序。
- **Target Users**: 小说作者、内容创作者

## Goals
- 右侧面板提供大纲视图和写作统计，帮助作者掌控全局
- 全文搜索替换，快速定位和修改内容
- 拖拽排序章节和分卷，直观调整结构
- 所有功能与现有编辑器、主题系统无缝集成

## Non-Goals (Out of Scope)
- AI 续写、润色等 AI 功能（Phase 3）
- 角色、情节追踪系统（Phase 4）
- 从原版项目导入（后续批次）
- 导出功能（TXT/MD/EPUB/PDF）（后续批次）
- 富文本格式化（加粗、斜体等）
- 插件系统（Phase 5）

## Background & Context
- Phase 1 已完成：项目脚手架、数据层、主窗口、主题系统、项目 CRUD
- Phase 2 第一批已完成：章节编辑器、分卷/章节 CRUD、字数统计、自动保存、标签页管理
- 现有右侧 Dock（AI 助手）目前只有占位文本，可以改造为多标签页面板
- 项目树使用 QTreeWidget，原生支持拖拽功能
- 写作方法注册表（core/methods/registry.py）已有 7 种方法的结构化节点数据，可用于大纲面板

## Functional Requirements

- **FR-1**: 右侧面板容器 - 将右侧 Dock 改造为 QTabWidget 多面板，支持"大纲"和"统计"两个标签
- **FR-2**: 大纲面板 - 显示当前项目的写作方法阶段列表，展示每个阶段的名称、描述、章节范围
- **FR-3**: 统计面板 - 显示项目总字数、章节数、分卷数、目标进度、每日字数等统计信息
- **FR-4**: 全文搜索 - 支持在项目所有章节中搜索关键词，显示匹配结果列表，点击跳转到对应章节
- **FR-5**: 搜索替换 - 支持替换单个或批量替换所有匹配项
- **FR-6**: 搜索高亮 - 在编辑器中高亮显示搜索结果
- **FR-7**: 章节拖拽排序 - 在项目树中拖拽章节调整顺序，自动更新章节号
- **FR-8**: 分卷拖拽排序 - 在项目树中拖拽分卷调整顺序
- **FR-9**: 拖拽跨分卷 - 支持将章节拖拽到其他分卷

## Non-Functional Requirements

- **NFR-1**: 搜索响应时间 < 1 秒（10 万字项目）
- **NFR-2**: 拖拽操作流畅，无明显卡顿
- **NFR-3**: 右侧面板切换不影响编辑器性能
- **NFR-4**: 与现有暗色/亮色主题完全兼容
- **NFR-5**: 所有操作可撤销（拖拽排序后可恢复）或有确认提示

## Constraints
- **Technical**: PySide6 + SQLAlchemy + SQLite，必须使用现有项目结构和编码风格
- **Business**: 第二批聚焦于编辑器增强，不涉及 AI 和追踪系统
- **Dependencies**: 依赖 Phase 2 第一批的编辑器、章节服务、主窗口框架

## Assumptions
- 搜索使用 SQLite LIKE 查询，暂不引入 FTS5 全文索引（后续优化）
- 拖拽排序通过 QTreeWidget 的内置拖拽功能实现，数据层更新章节号
- 大纲面板根据项目写作方法从注册表读取节点定义，展示进度（按章节字数估算）
- 统计面板数据实时计算（每次切换时重新统计）

## Acceptance Criteria

### AC-1: 右侧面板容器
- **Given**: 用户打开了一个项目
- **When**: 查看右侧 Dock 面板
- **Then**: 右侧面板顶部有标签页切换，包含"大纲"和"统计"两个标签
- **Verification**: `human-judgment`

### AC-2: 大纲面板显示
- **Given**: 用户打开了一个有写作方法的项目
- **When**: 切换到"大纲"标签页
- **Then**: 显示该写作方法的所有阶段节点，每个节点显示名称、描述、章节范围
- **Verification**: `human-judgment`

### AC-3: 统计面板显示
- **Given**: 用户打开了一个有多个章节的项目
- **When**: 切换到"统计"标签页
- **Then**: 显示项目总字数、章节数、分卷数、目标字数进度条、平均每章字数等信息
- **Verification**: `human-judgment`

### AC-4: 全文搜索
- **Given**: 用户打开了一个有多个章节的项目
- **When**: 用户按下 Ctrl+F 或通过菜单打开搜索框，输入关键词并搜索
- **Then**: 显示匹配结果列表，每个结果显示章节名称和匹配内容片段
- **Verification**: `human-judgment`

### AC-5: 搜索结果跳转
- **Given**: 搜索结果列表中有多个匹配项
- **When**: 用户点击某个搜索结果
- **Then**: 打开对应章节的编辑器，光标定位到匹配位置并高亮
- **Verification**: `human-judgment`

### AC-6: 搜索替换
- **Given**: 用户在搜索框中输入了搜索词和替换词
- **When**: 用户点击"替换"或"全部替换"
- **Then**: 单个替换当前匹配项，或批量替换所有匹配项，并更新数据库
- **Verification**: `programmatic`

### AC-7: 章节拖拽排序
- **Given**: 用户在项目树中看到多个章节
- **When**: 用户拖拽一个章节到同一分卷内的不同位置
- **Then**: 章节顺序改变，章节号自动重新编号，数据库同步更新
- **Verification**: `human-judgment`

### AC-8: 分卷拖拽排序
- **Given**: 用户在项目树中看到多个分卷
- **When**: 用户拖拽一个分卷到不同位置
- **Then**: 分卷顺序改变，sort_order 自动更新，数据库同步更新
- **Verification**: `human-judgment`

### AC-9: 章节跨分卷拖拽
- **Given**: 用户在项目树中看到多个分卷，每个分卷有章节
- **When**: 用户拖拽一个章节到另一个分卷
- **Then**: 章节移动到目标分卷，章节号在新分卷中重新编号
- **Verification**: `human-judgment`

### AC-10: 主题兼容
- **Given**: 应用运行中
- **When**: 用户切换暗色/亮色主题
- **Then**: 右侧面板、搜索框、搜索结果等所有新组件都正确切换样式
- **Verification**: `human-judgment`

### AC-11: 统计数据准确
- **Given**: 项目中有若干章节，每章有不同字数
- **When**: 查看统计面板
- **Then**: 总字数等于所有章节字数之和，章节数准确，进度计算正确
- **Verification**: `programmatic`

## ~~Open Questions~~ ✅ 全部已决策
- [x] **搜索入口** → 编辑器右上方浮动搜索面板 + Ctrl+F 快捷键
- [x] **搜索历史记录** → 已实现，持久化至 `search_history.json`，支持 ↑↓ 浏览
- [x] **拖拽排序撤销** → 有确认提示 + Toast 撤销按钮 + `_undo_reorder` snapshot 机制
- [x] **大纲面板跳转** → 已实现，`navigate_to_chapter` 连接 `_open_chapter_editor`

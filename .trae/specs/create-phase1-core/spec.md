# Phase 1: 核心框架搭建 Spec

## Why

搭建 Novel Writer PySide6 版的核心基础设施，包括应用框架、数据库、主窗口 UI、基础项目管理功能，使应用能从零到可运行并完成最基本的小说项目创建流程。

## What Changes

- **项目脚手架**：完善项目目录结构和 Python 包配置
- **应用入口**：统一的应用启动流程（数据库初始化、主题加载、窗口显示）
- **数据层**：SQLite 数据库（WAL 模式）+ 4 张核心表（projects/volumes/chapters/ai_providers）
- **UI 框架**：PySide6 主窗口（菜单栏、工具栏、Dock 面板、标签编辑器、状态栏）
- **暗色主题**：完整的 QSS 暗色主题样式
- **项目管理**：项目 CRUD（创建/打开/列表/归档）+ 项目统计
- **信号总线**：Qt 信号驱动的模块间通信机制
- **日志系统**：控制台 + 文件日志
- **配置管理**：.env 环境变量 + AppConfig 单例

## Impact

- 新建 `novel-writer-pyside/` 独立项目目录（与原版 TypeScript 代码隔离）
- Python 虚拟环境（venv）+ 依赖管理（requirements.txt）
- 影响后续所有 Phase 作为基础依赖
- 遵循的代码规范：Black（行宽100）/ Ruff / Mypy

## ADDED Requirements

### Requirement: 应用启动

The system SHALL provide a unified application entry point.

#### Scenario: 正常启动
- **WHEN** 用户运行 `python app/main.py`
- **THEN** 应用初始化数据库 → 加载暗色主题 → 创建主窗口并显示 → 状态栏显示"就绪"
- **AND** 日志文件写入 `~/.novel-writer/logs/` 目录

#### Scenario: 数据库初始化失败
- **WHEN** 数据库文件无法创建（如权限不足）
- **THEN** 应用应记录错误日志并以退出码 1 退出

### Requirement: 主窗口

The system SHALL provide a PySide6 QMainWindow with standard desktop application structure.

#### Scenario: 主窗口布局
- **WHEN** 应用启动
- **THEN** 窗口标题为 "Novel Writer"，默认大小 1400×900，最小 1000×600
- **AND** 包含菜单栏、工具栏、左侧项目 Dock、中央标签编辑器、右侧 AI 面板 Dock、底部状态栏

#### Scenario: 菜单结构
- **WHEN** 用户查看菜单栏
- **THEN** 应包含"文件"（新建/打开/保存/退出）、"视图"（主题选择）、"帮助"（关于）三个菜单
- **AND** 快捷键支持：Ctrl+N（新建）、Ctrl+O（打开）、Ctrl+S（保存）、Ctrl+Q（退出）

### Requirement: 数据库

The system SHALL use SQLite with SQLAlchemy ORM for local data storage.

#### Scenario: 数据库初始化
- **WHEN** 应用首次启动
- **THEN** `~/.novel-writer/novel_writer.db` 文件被创建
- **AND** 启用 WAL 模式、busy_timeout 5000ms、foreign_keys=ON

#### Scenario: 数据表结构
- **THEN** 应包含以下数据表：
  - `projects`：小说项目（名称/类型/写作方法/状态/目标字数/时间戳）
  - `volumes`：分卷（所属项目/名称/排序）
  - `chapters`：章节（所属分卷/章节号/标题/内容/字数/状态/软删除）
  - `ai_providers`：AI 提供商配置（名称/API Key 加密/默认模型/温度参数/启用状态）

### Requirement: 项目管理

The system SHALL support create, open, list, and archive operations for novel projects.

#### Scenario: 新建项目
- **WHEN** 用户点击"新建项目"菜单按钮或 Ctrl+N
- **THEN** 弹出新建项目对话框，包含：项目名称（必填）、小说类型（下拉选择）、写作方法（6种可选）、目标字数、项目简介
- **AND** 点击"创建项目"后，验证名称非空 → 创建数据库记录 → 创建默认分卷"第一卷" → 状态栏显示成功消息

#### Scenario: 项目树
- **WHEN** 项目被创建或打开
- **THEN** 左侧 Dock 中显示项目树（包含分卷结构）

### Requirement: 暗色 UI 主题

The system SHALL provide a complete dark theme via QSS.

#### Scenario: 主题应用
- **WHEN** 应用启动
- **THEN** 应用加载 `dark.qss` 并应用到全局
- **AND** 主题覆盖：主窗口/菜单栏/工具栏/Dock/树视图/编辑器/标签页/按钮/输入框/滚动条/状态栏/分割器

#### Scenario: 主题切换
- **WHEN** 用户选择视图 → 主题 → 亮色
- **THEN** 动态切换到亮色主题

### Requirement: 信号总线

The system SHALL provide a global Qt Signal-based communication bus for module decoupling.

#### Scenario: 信号定义
- **THEN** 信号总线应支持：project_opened/closed/created、chapter_created/deleted/saved/switched、ai_generation_started/finished/error、status_message、word_count_updated、theme_changed、sidebar_toggled

### Requirement: 日志系统

The system SHALL log to both console and file with timestamps and log levels.

#### Scenario: 日志输出
- **WHEN** 应用运行
- **THEN** 控制台显示彩色日志（info/success/warn/error/debug）
- **AND** 日志文件写入 `~/.novel-writer/logs/YYYY-MM-DD.log`

### Requirement: 配置管理

The system SHALL load configuration from .env file with sensible defaults.

#### Scenario: 配置加载
- **WHEN** 应用启动
- **THEN** 从 `.env` 文件加载配置
- **AND** 提供默认值：数据目录 `~/.novel-writer`、语言 `zh-CN`、主题 `dark`、默认 AI 提供商 `openai`、默认模型 `gpt-4o`

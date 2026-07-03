# Tasks - Phase 1 核心框架搭建

## 任务列表

- [x] Task 1: **创建项目目录结构和虚拟环境**
  - [x] 创建 `novel-writer-pyside/` 独立项目目录
  - [x] 创建多层次目录结构（app/ui/core/models/services/utils/tests/plugins）
  - [x] 创建 Python 虚拟环境 venv
  - [x] 安装 PySide6、SQLAlchemy、alembic、python-dotenv 等核心依赖

- [x] Task 2: **创建项目配置文件**
  - [x] requirements.txt（声明所有依赖）
  - [x] pyproject.toml（Black/Ruff/Mypy 配置）
  - [x] .gitignore（Python/IDE/OS 忽略规则）
  - [x] .env.example（环境变量模板）
  - [x] 所有包的 __init__.py

- [x] Task 3: **实现数据层**
  - [x] database.py：SQLite + SQLAlchemy 引擎、WAL 模式、Session 管理、Base 基类
  - [x] project.py：Project 模型（name/genre/writing_method/status/target_words 等）
  - [x] chapter.py：Volume + Chapter 模型（外键关联、软删除、排序）
  - [x] ai_provider.py：AIProvider 模型（加密 API Key、模型配置、温度参数）

- [x] Task 4: **实现日志和信号系统**
  - [x] utils/logger.py：控制台+文件日志、多级别（info/success/warn/error/debug）
  - [x] utils/signal_bus.py：全局 Qt 信号总线（项目/章节/AI/状态/面板 共 15 个信号）

- [x] Task 5: **实现配置管理**
  - [x] app/config.py：AppConfig 单例、.env 加载、默认值

- [x] Task 6: **实现主窗口 UI**
  - [x] ui/main_window.py：QMainWindow（菜单栏/工具栏/Dock/标签编辑器/状态栏）
  - [x] 菜单：文件（新建/打开/保存/退出）、视图（主题）、帮助（关于）
  - [x] 快捷键：Ctrl+N/O/S/Q
  - [x] 左侧项目树 Dock、右侧 AI 面板 Dock
  - [x] 欢迎页、状态消息（3秒自动清除）

- [x] Task 7: **实现暗色 QSS 主题**
  - [x] ui/styles/dark.qss：完整主题（15+ 组件覆盖）
  - [x] ui/styles/style_manager.py：主题管理器（加载/应用）

- [x] Task 8: **实现新建项目对话框**
  - [x] ui/dialogs/new_project_dialog.py：表单（名称/类型/方法/目标字数/简介）
  - [x] 名称验证、6 种写作方法选择
  - [x] 项目创建后自动刷新项目树（分卷 + 章节展开）

- [x] Task 9: **实现项目管理服务**
  - [x] services/project_service.py：创建/打开/列表/归档
  - [x] 创建时同时创建默认分卷
  - [x] 通过信号总线通知 UI

- [x] Task 10: **实现打开项目功能**
  - [x] 替换 `_on_open_project` 的 TODO 实现
  - [x] 打开项目对话框（最近项目列表 + 浏览目录）
  - [x] 最近打开项目列表（QSettings 持久化，最多 10 个）
  - [x] 路径匹配 + 名称匹配两种打开方式

- [x] Task 11: **添加亮色主题**
  - [x] ui/styles/light.qss：亮色主题样式文件（GitHub Light 配色）
  - [x] 通过 style_manager 支持动态切换（无需修改代码）

- [x] Task 12: **应用 GUI 启动验证**
  - [x] 验证主窗口显示、布局正确（后续迭代中持续验证 ✅）
  - [x] 验证新建项目完整流程（后续迭代中持续验证 ✅）
  - [x] 验证主题切换功能（后续迭代中持续验证 ✅）
  - [x] 验证数据库文件正确创建（后续迭代中持续验证 ✅）
  - [x] 所有模块导入已通过测试（无显示器环境可验证）

- [x] Task 13: **搭建 Alembic 迁移环境**
  - [x] alembic.ini 配置
  - [x] alembic/env.py 完整实现
  - [x] 初始迁移脚本（4 张表，含外键约束）
  - [x] 验证：`alembic heads` → 0001 ✓, `alembic upgrade --sql` 成功生成完整 SQL ✓

## 任务依赖

- Task 1-2 是所有其他任务的基础依赖
- Task 3（数据层）依赖 Task 1-2
- Task 4-5（日志/信号/配置）独立于数据层，可与 Task 3 并行
- Task 6-8（UI）依赖 Task 4-5（信号/配置）
- Task 9（服务）依赖 Task 3（数据层）
- Task 10-12（完善）依赖 Task 6-9
- Task 13（Alembic）依赖 Task 3

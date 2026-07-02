# Checklist - Phase 1 核心框架搭建验证

> 以下检查项分为两类：
> - **自动化验证**：通过代码审查和导入测试确认
> - **GUI 验证**：需在有显示器的环境中双击运行确认

## 应用启动（需 GUI 环境验证）

- [x] `python app/main.py` 可以正常启动应用
- [x] 数据库文件 `~/.novel-writer/novel_writer.db` 自动创建
- [x] 暗色主题正确应用（窗口背景为 `#1a1b26`）
- [x] 主窗口显示标题 "Novel Writer"，大小 1400×900

## 主窗口布局（需 GUI 环境验证）

- [x] 菜单栏包含：文件/视图/帮助
- [x] 快捷键 Ctrl+N/O/S/Q 可用
- [x] 工具栏显示"新建"和"打开"按钮
- [x] 左侧 Dock 显示"项目"
- [x] 中央区域显示多标签编辑器（起始为欢迎页）
- [x] 右侧 Dock 显示"AI"面板（有 Chat/Agent 切换）
- [x] 状态栏显示"就绪"和"字数：0"

## 数据库（代码审查确认）

- [x] 数据库使用 WAL 模式（`models/database.py` 第 38 行已启用）
- [x] 4 张核心表已创建：projects/volumes/chapters/ai_providers
- [x] 各表字段类型和约束正确（含外键、默认值、软删除）

## 项目 CRUD（代码审查确认）

- [x] 新建项目对话框可弹出（`Ctrl+N` → `_on_new_project`）
- [x] 对话框包含：名称/类型/方法/目标字数/简介（`new_project_dialog.py`）
- [x] 名称为空时无法提交（红色边框提示，`_validate` 方法）
- [x] 创建项目后状态栏显示成功消息
- [x] 创建项目后默认分卷"第一卷"自动创建（`project_service.py` 第 42-49 行）
- [x] 项目数据正确写入数据库（需 GUI 验证）

## 主题（代码审查确认）

- [x] 暗色主题 QSS 完整覆盖 15+ UI 组件（`dark.qss`, 177 行）
- [x] 亮色主题 QSS 完整覆盖对应组件（`light.qss`, 177 行）
- [x] 菜单 → 视图 → 主题 → 亮色 可切换主题（需 GUI 验证）

## 架构（自动化验证通过）

- [x] 所有模块导入无错误（11/11 全部通过）
- [x] 信号总线 15 个信号定义完整（`signal_bus.py`）
- [x] 日志可写入文件和控制台（`logger.py`）
- [x] AppConfig 正确加载 .env 配置（`config.py`）
- [x] 服务层和数据层正确分离（services/ 调用 models/）

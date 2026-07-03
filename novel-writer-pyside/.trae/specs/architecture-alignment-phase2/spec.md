# 架构对齐 Phase 2 Spec

## Why

上一轮架构对齐补齐了 3 个缺失模块（EditorService、AIService、core/tracking/、core/plugins/），但仍有 4 处结构性偏离：`core/writing/` 和 `core/project/` 为空壳、配置管理未按文档设计实现、`core/methods/` 路径与实际不符。

## What Changes

1. 填充 `core/writing/`：从 `services/chapter_service.py` 提取章节/分卷核心逻辑至 `core/writing/engine.py`
2. 填充 `core/project/`：从 `services/project_service.py` 提取项目 CRUD 核心逻辑至 `core/project/manager.py`
3. 配置管理对齐：扩展 `app/config.py` 中的 `AppConfig`，增加 `load/save/update` 方法和 `config.json` 持久化
4. 路径对齐：将 `core/ai/writing_methods/` 中的 6 个方法类 + advisor/converter 迁移至 `core/methods/`，保留向后兼容 stub

**不在此范围**：
- 之前的已对齐部分（EditorService、AIService、tracking、plugins）
- 已标记的架构差异（双库、QThread、编辑器类名等）

## Impact
- Affected specs: `002_系统架构设计.md` 第 3.1、3.2 节
- Affected code: `services/chapter_service.py`、`services/project_service.py`、`app/config.py`、`core/project/manager.py`、`core/methods/`、`core/ai/writing_methods/`

## ADDED Requirements

### Requirement: WritingEngine 写作引擎
系统 SHALL 提供 `WritingEngine` 类封装章节管理和大纲引擎核心逻辑。

#### Scenario: 章节管理提取
- **WHEN** 创建/更新/删除章节或分卷
- **THEN** `WritingEngine` 处理核心逻辑，`ChapterService` 委托给 `WritingEngine`

#### Scenario: 大纲引擎提取
- **WHEN** `services/chapter_service.py` 涉及大纲结构操作
- **THEN** 核心逻辑移至 `core/writing/` 中

### Requirement: ProjectManager 项目管理增强
系统 SHALL 将项目 CRUD 核心逻辑从 `services/project_service.py` 提取至 `core/project/manager.py`。

#### Scenario: 项目 CRUD 提取
- **WHEN** 创建/打开/归档/删除项目
- **THEN** `ProjectManager` 处理核心逻辑，`ProjectService` 委托给 `ProjectManager`

### Requirement: AppConfig 配置管理
系统 SHALL 在 `app/config.py` 中提供完整的 `AppConfig` 类，支持 `config.json` 持久化。

#### Scenario: 配置加载与保存
- **WHEN** 应用启动
- **THEN** `AppConfig.load()` 从 `config.json` 加载配置
- **AND** 运行时通过 `save()` 持久化

### Requirement: core/methods/ 路径对齐
系统 SHALL 将 `core/ai/writing_methods/` 中的方法实现迁移至 `core/methods/`。

#### Scenario: 方法导入
- **WHEN** 导入写作方法
- **THEN** 从 `core.methods` 导入，而非 `core.ai.writing_methods`
- **AND** 旧路径保留 stub 文件向后兼容

## MODIFIED Requirements
### Requirement: 现有服务类调整
`services/chapter_service.py`、`services/project_service.py` 中的业务逻辑拆分为两层：`services/` 保留服务层包装，`core/writing/`、`core/project/` 保留核心逻辑。

## REMOVED Requirements
### Requirement: 旧的 core/ai/writing_methods/ 路径
**Reason**: 方法实现移至 `core/methods/` 以匹配文档
**Migration**: 旧路径保留 `from core.methods import *` 的 stub 文件，不破坏现有导入

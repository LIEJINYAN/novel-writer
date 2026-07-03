# 提示词模板系统对齐 Spec

## Why

提示词模板系统路径为 `core/ai/prompts/`，设计文档要求 `core/ai/prompt_templates/`。基类为 ABC + Jinja2，文档要求 `@dataclass` + `str.replace` + `build_messages()` API。模板内容（constitution、write、specify 等）为简化版，未按文档扩充。

## What Changes

1. 目录改名：`core/ai/prompts/` → `core/ai/prompt_templates/`
2. 基类 `base.py` 重写为 `@dataclass`，含 `AIConfig` 数据类、`PromptTemplate` 数据类、`render(**kwargs)` + `build_messages(**kwargs)` API
3. 所有模板文件按文档重建，扩充提示词内容
4. 新增 3 个缺失模板：clarify（澄清决策点）、plan（技术方案）、tasks（任务分解）
5. 新增 `anti_ai.py`（反 AI 检测常量，文档 8.1 节）
6. 新增 `presets.py`（预设配置方案，文档 5.2 节）
7. 更新 4 个服务文件调用方式：`render(context) → build_messages(**kwargs)`

**不在此范围**：
- 数据库会话管理（上下文构建器的数据加载）
- AI 提供商实现
- 错误处理/重试机制

## Impact
- Affected specs: `004_AI提示词系统设计.md` 第 3-5、8 节
- Affected code: `core/ai/prompts/` → `core/ai/prompt_templates/`（重写全部），`core/ai/writing_service.py`、`core/ai/editing_service.py`、`core/ai/analysis_service.py`、`services/consistency_service.py`（更新调用）

## ADDED Requirements

### Requirement: 目录路径对齐
系统 SHALL 将提示词模板从 `core/ai/prompts/` 迁移至 `core/ai/prompt_templates/`。

#### Scenario: 导入路径更新
- **WHEN** 导入模板
- **THEN** 从 `core.ai.prompt_templates` 导入
- **AND** 旧路径 `core.ai.prompts` 不再可用

### Requirement: 基类 API 对齐
系统 SHALL 使用 `@dataclass PromptTemplate` 替代 ABC + Jinja2。

#### Scenario: 构建消息
- **WHEN** `build_messages(field1=val1, field2=val2)` 被调用
- **THEN** 返回 `[{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]` 格式的消息列表

### Requirement: 新增 clarify/plan/tasks 模板
系统 SHALL 提供 3 个新模板：clarify（澄清决策点）、plan（制定技术方案）、tasks（分解执行任务）。

#### Scenario: 七步方法论完整
- **WHEN** 查看所有写作模板
- **THEN** 看到 constitution → specify → clarify → plan → tasks → write → analyze 完整 7 步

## MODIFIED Requirements
### Requirement: 模板内容扩充
constitution、write、specify、polish、continue_write、dialogue、analyze 模板的提示词内容按 `004_AI提示词系统设计.md` 第 3 节扩充。

## REMOVED Requirements
### Requirement: 旧 prompts 目录及 Jinja2 渲染
**Reason**: 路径和 API 与设计文档不一致
**Migration**: 所有文件迁移至 `prompt_templates/`，基类改用 `str.replace` 渲染

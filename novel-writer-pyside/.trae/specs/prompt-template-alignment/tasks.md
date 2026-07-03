# Tasks

## [x] Task 1: 重写 base.py 基类
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 添加 `AIConfig` 数据类（temperature/max_tokens/top_p/frequency_penalty/presence_penalty/stop）
  - 从 `core.ai.base` 复用或新定义
  - `PromptTemplate` 改为 `@dataclass`，含 `name`/`description`/`system_prompt`/`user_prompt_template`/`default_config` 字段
  - `render(**kwargs)` 使用 `str.replace` 渲染
  - `build_messages(**kwargs)` 返回 `[{"role":"system","content":"..."}, {"role":"user","content":"..."}]`
- **Acceptance**: `PromptTemplate(name="test", description="test").build_messages(foo="bar")` 返回正确的消息列表

## [x] Task 2: 重写所有模板文件并扩充内容
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `writing.py`：constitution/specify/clarify/plan/tasks/write 6 个模板（clarify/plan/tasks 为新加）
  - `editing.py`：polish/continue_write/rewrite/dialogue 4 个模板
  - `analysis.py`：analyze 1 个模板
  - `experts.py`：plot_expert/character_expert/world_expert/style_expert/plot_check/consistency_check/character_check 7 个模板
  - 所有提示词内容按设计文档第 3 节扩充
- **Acceptance**: 模板内容与文档基本一致，18 个模板均可正常使用

## [x] Task 3: 添加 anti_ai.py + presets.py
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - `anti_ai.py`：`ANTI_AI_SYSTEM` 常量（排版规则、对话规则、AI 高频词黑名单、具象化替换表）
  - `presets.py`：`CREATIVE_CONFIG`/`EDITING_CONFIG`/`ANALYSIS_CONFIG`/`DIALOGUE_CONFIG`/`OUTLINE_CONFIG` 5 个预设 + `CREATIVE_ENHANCEMENT` 常量
- **Acceptance**: `from core.ai.prompt_templates.anti_ai import ANTI_AI_SYSTEM` 正常

## [x] Task 4: 更新 registry.py 注册全部模板
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 在新路径下创建 `registry.py`，注册全部 18 个模板
  - `get_template(name)` / `list_templates()` 函数
- **Acceptance**: 18 个模板全部注册成功

## [x] Task 5: 目录改名 + 更新服务文件
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 删除旧目录 `core/ai/prompts/`
  - 新目录 `core/ai/prompt_templates/` 就位
  - 更新 `core/ai/writing_service.py`：导入路径 + `render(context)` → `build_messages(**context)`
  - 更新 `core/ai/editing_service.py`：同上
  - 更新 `core/ai/analysis_service.py`：同上
  - 更新 `services/consistency_service.py`：同上
- **Acceptance**: 4 个服务文件均从新路径导入，`build_messages()` 调用正常

## [x] Task 6: 全面验证
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 验证 18 个模板全部注册
  - 验证 4 个服务文件导入
  - 验证旧路径已删除
  - 验证 anti_ai.py 和 presets.py 存在
- **Acceptance**: 所有验证通过

# Task Dependencies
- [Task 2] 依赖 [Task 1]
- [Task 4] 依赖 [Task 2], [Task 3]
- [Task 5] 依赖 [Task 4]
- [Task 6] 依赖 [Task 5]

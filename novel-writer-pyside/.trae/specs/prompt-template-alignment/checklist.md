# 提示词模板系统对齐 - 检查清单

- [x] Task 1: `base.py` 基类重写为 `@dataclass`，含 `AIConfig`、`render(**kwargs)`、`build_messages(**kwargs)`
- [x] Task 2: `writing.py` 包含 6 个模板（含 clarify/plan/tasks 新增）
- [x] Task 2: `editing.py` 包含 4 个模板，提示词按文档扩充
- [x] Task 2: `analysis.py` 包含 1 个 analyze 模板
- [x] Task 2: `experts.py` 包含 7 个专家模板
- [x] Task 3: `anti_ai.py` 包含 `ANTI_AI_SYSTEM` 常量
- [x] Task 3: `presets.py` 包含 5 个预设配置
- [x] Task 4: `registry.py` 注册全部 18 个模板
- [x] Task 5: 目录 `prompts` → `prompt_templates` 改名完成
- [x] Task 5: 4 个服务文件导入和调用方式更新
- [x] Task 5: 旧路径 `core.ai.prompts` 不可用
- [x] 应用启动正常，无导入错误

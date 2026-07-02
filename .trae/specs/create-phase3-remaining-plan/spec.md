# Phase 3 剩余功能分批次规划

## Why

Phase 3 已完成了 AI 基础设施、核心编辑功能和部分提供商支持，但仍有大量未完成的功能：上下文管理、更多提供商、高级 UI 交互、写作方法系统等。需要将这些剩余工作合理分批次，明确优先级和依赖关系，确保开发有序推进。

## 已完成概览

| 模块 | 已完成的 | 剩余 |
|------|---------|------|
| 4.1 AI 提供商 | OpenAI, DeepSeek, Ollama, Anthropic, Gemini, AI管理器 | 通义千问/豆包 |
| 4.2 提示词系统 | PromptTemplate 基类、写作模板(续写)、编辑模板(润色/重写)、分析模板 | 更多写作模板、分析模板集(plot-check等)、专家模板集、反AI检测规范 |
| 4.3 上下文管理 | **未开始** | ContextBuilder、Token计数器、上下文裁剪 — **全部** |
| 4.4 AI 服务 | AIWorker(流式)、WritingService(续写)、EditingService(润色/重写)、AnalysisService | AI对话服务(已部分通过 AIWorker 实现) |
| 4.5 AI UI | AI面板、AI对话面板、AI续写按钮、AI设置对话框 | AI润色差分对比对话框、创作向导 |
| 4.6 写作方法 | **未开始** | WritingMethod基类、具体方法、方法推荐、方法转换 — **全部** |

## 批次划分

### 第三批：上下文管理 + 通义千问/豆包（高优先级）
- **焦点**：解决 AI 功能的基础设施短板——Token 计数、上下文构建与裁剪
- **补充**：通义千问/豆包适配器
- **为什么先做**：上下文管理是后续所有 AI 功能（特别是长章节写作）的前提

### 第四批：AI 润色差分对比 + 反 AI 检测（中优先级）
- **焦点**：润色功能的前后对比显示、AI 痕迹检测与避免
- **核心交付**：左右对比/高亮差异的润色对话框
- **依赖**：第三批的上下文管理（分析结果需 Token 计数支持）

### 第五批：写作方法系统（中优先级）
- **焦点**：WritingMethod 基类 + 具体方法实现 + 大纲面板深度集成
- **核心交付**：三幕式、英雄之旅、七步法、故事圈等方法
- **特点**：独立模块，不依赖第三/四批

### 第六批：高级提示词模板 + 创作向导（低优先级）
- **焦点**：专家模板集、反 AI 检测模板、创作向导 UI
- **核心交付**：10+ 个高级模板 + 分步式创作向导

## Impact

- 新文件：`core/ai/context/`、`core/ai/providers/tongyi_provider.py`、`core/ai/writing_methods/`、`ui/dialogs/ai_polish_diff_dialog.py`、`ui/dialogs/creation_wizard.py` 等
- 修改文件：各批次涉及已有文件的扩展
- **不破坏**：已完成的功能保持兼容

## Requirements

### FR-1: 第三批 — 上下文管理
- ContextBuilder：从章节/项目/角色/设定中构建 AI 上下文
- TokenCounter：使用 tiktoken 精确计算 token 数
- ContextPruner：按优先级/Token 限制裁剪上下文
- 通义千问适配器：支持 qwen-max、qwen-plus、qwen-turbo
- 豆包适配器：支持 doubao-pro、doubao-lite

### FR-2: 第四批 — 润色差分对比 + 反 AI 检测
- 润色差分对话框：左右两栏或行内高亮显示修改部分
- 反 AI 检测提示词模板：内置 anti-AI 规范
- 检测规范集成到续写/润色/重写流程中

### FR-3: 第五批 — 写作方法系统
- WritingMethod 基类：方法名称、阶段定义、章节映射
- 具体方法：三幕式、英雄之旅、七步法、故事圈、Save the Cat、盲点法
- 方法 → 大纲面板集成：方法阶段与章节树映射
- 方法推荐（MethodAdvisor）：根据项目类型和内容推荐合适方法

### FR-4: 第六批 — 高级模板 + 创作向导
- 专家模板：情节专家、角色专家、世界观专家、风格专家
- 分析模板补充：plot-check、consistency-check、character-check
- 创作向导：分步式对话框（选方法→设定→大纲→开始写作）
- 方法转换：在不同方法间调整章节结构

## Out of Scope
- Phase 4（角色/情节追踪系统）
- Phase 5（打包/发布/性能优化）
- 插件系统

## Acceptance Criteria

### AC-1: 第三批
- TokenCounter 能对任意文本计算 token 数，支持多种模型族
- ContextBuilder 能构建包含章节内容、角色信息的上下文，不出错
- ContextPruner 能在超出限制时正确裁剪
- 通义千问/豆包适配器可连接测试

### AC-2: 第四批
- 润色对话框显示修改前后的文本对比，差异高亮
- 反 AI 检测规范可插入到续写/润色的提示词中

### AC-3: 第五批
- WritingMethod 基类可被子类正确继承
- 至少 3 种具体方法可正常工作
- 方法阶段可映射到大纲面板的章节结构

### AC-4: 第六批
- 所有专家模板可正确渲染
- 创作向导可引导用户完成从选方法到开始写作的流程

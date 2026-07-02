# Phase 3 剩余功能验证检查清单

## 第三批：上下文管理 + 通义千问/豆包

### Token 计数器
- [x] Checkpoint 3.1: `TokenCounter.count()` 返回正确的 token 数
- [x] Checkpoint 3.2: 支持多种模型族映射
- [x] Checkpoint 3.3: 没有 tiktoken 时优雅降级

### 上下文构建器
- [x] Checkpoint 3.4: `ContextBuilder.build_chapter_context()` 正确加载章节+角色信息
- [x] Checkpoint 3.5: `ContextBuilder.build_analysis_context()` 构建分析专用上下文

### 上下文裁剪
- [x] Checkpoint 3.6: `ContextPruner.prune()` 在超出限制时正确裁剪
- [x] Checkpoint 3.7: `ContextPruner.prune_messages()` 保留 system 消息

### 上下文管理器集成
- [x] Checkpoint 3.8: `AIContextManager.get_chapter_context()` 一键获取裁剪后上下文
- [x] Checkpoint 3.9: `AIContextManager.get_chat_context()` 裁剪聊天历史

### 通义千问/豆包适配器
- [x] Checkpoint 3.10: `TongyiProvider` 继承 BaseAIProvider，显示名称 "通义千问"
- [x] Checkpoint 3.11: `DoubaoProvider` 继承 BaseAIProvider，显示名称 "豆包"
- [x] Checkpoint 3.12: 两个提供商注册到 AIManager，共 7 个提供商

---

## 第四批：AI 润色差分对比 + 反 AI 检测

### 润色差分对话框
- [x] Checkpoint 4.1: 对话框左右两栏显示原文和润色后文本
- [x] Checkpoint 4.2: 差异使用颜色高亮（新增/删除/修改）
- [x] Checkpoint 4.3: 左右栏同步滚动
- [x] Checkpoint 4.4: 应用润色/取消/重新润色按钮正常工作

### 主窗口集成
- [x] Checkpoint 4.5: 润色完成后弹出差分对话框，不直接替换
- [x] Checkpoint 4.6: 用户确认应用后替换选中文本

### 反 AI 检测规范
- [x] Checkpoint 4.7: 反 AI 检测规范文本包含词汇多样性、节奏变化、具体细节、个性化表达
- [x] Checkpoint 4.8: 续写/润色/重写模板支持 `{{ anti_ai }}` 变量

---

## 第五批：写作方法系统

### WritingMethod 基类
- [x] Checkpoint 5.1: `WritingMethod` 基类定义了 name/stages/analyze_outline/suggest_chapter
- [x] Checkpoint 5.2: `MethodStage` 数据类包含 name/order/description

### 具体方法实现
- [x] Checkpoint 5.3: 三幕式方法定义了 4 个阶段
- [x] Checkpoint 5.4: 英雄之旅方法定义了 12 个阶段
- [x] Checkpoint 5.5: 七点故事结构定义了 7 个阶段
- [x] Checkpoint 5.6: 每个方法返回正确的兼容类型列表

### 方法推荐器
- [x] Checkpoint 5.7: `MethodAdvisor.recommend()` 返回带评分的推荐列表
- [x] Checkpoint 5.8: 推荐算法考虑了类型兼容性

### 大纲面板集成
- [x] Checkpoint 5.9: 大纲面板显示方法选择器
- [x] Checkpoint 5.10: 选择方法后显示阶段列表
- [x] Checkpoint 5.11: 章节可分配到不同方法阶段
- [x] Checkpoint 5.12: 项目数据存储所选方法

---

## 第六批：高级提示词模板 + 创作向导

### 专家模板
- [x] Checkpoint 6.1: 7 个新模板注册到 PROMPT_REGISTRY（共 11 个）
- [x] Checkpoint 6.2: 每个模板正确渲染 Jinja2 模板

### 分析模板补充
- [x] Checkpoint 6.3: PlotCheckTemplate 注册到 PROMPT_REGISTRY
- [x] Checkpoint 6.4: ConsistencyCheckTemplate 注册到 PROMPT_REGISTRY
- [x] Checkpoint 6.5: CharacterCheckTemplate 注册到 PROMPT_REGISTRY

### 创作向导
- [x] Checkpoint 6.6: 向导有 4 个步骤页面
- [x] Checkpoint 6.7: 第 2 步显示推荐方法
- [x] Checkpoint 6.8: 完成向导后创建新项目
- [x] Checkpoint 6.9: 新项目自动应用所选写作方法

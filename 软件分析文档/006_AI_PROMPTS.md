# AI_PROMPTS

## 1. AI 模型配置与 API 端点

### 1.1 AI 模型概览

本项目是一个 **CLI + AI 助手** 协同创作系统，不直接调用 AI API，而是通过 AI 助手的斜杠命令系统与模型交互。

| 平台 | 模型名称 | 配置位置 | 说明 |
|------|---------|---------|------|
| **Claude Code** | `claude-sonnet-4-5-20250929` | 命令模板 frontmatter | 所有核心命令默认使用此模型 |
| **Cursor** | 内置模型（不可配置） | - | 温度锁定为 0.0 |
| **Gemini CLI** | 内置模型 | `.gemini/settings.json` | 通过配置文件管理 |
| **其他平台** | 各平台内置模型 | 各自配置目录 | Windsurf、Roo Code、Copilot 等 |

### 1.2 模型配置位置

所有命令模板的 frontmatter 中指定模型：

```yaml
---
description: 基于任务清单执行章节写作
model: claude-sonnet-4-5-20250929
allowed-tools: Read(//**), Write(//stories/**/content/**), Bash(ls:*), Bash(find:*), Bash(wc:*), Bash(grep:*), Bash(*)
scripts:
  sh: .specify/scripts/bash/check-writing-state.sh
  ps: .specify/scripts/powershell/check-writing-state.ps1
---
```

### 1.3 外部 API 端点

唯一的实时 API 调用在 stardust-dreams 插件中：

| HTTP 方法 | 路径 | 功能 | 认证方式 |
|-----------|------|------|---------|
| POST | `/api/trpc/form.getSession` | 获取会话信息 | API Key（请求体） |
| POST | `/api/trpc/form.getPrompt` | 获取加密 Prompt | API Key（请求体） |

**基础 URL**：`https://api.stardust-dreams.com`（可通过 `STARDUST_API_URL` 环境变量覆盖）

### 1.4 API 客户端封装

[api-client.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/api-client.js) 中的核心类：

```javascript
export class StardustAPIClient {
  constructor() {
    this.baseUrl = API_BASE;
    this.apiKey = process.env.STARDUST_API_KEY || null;
  }

  async getSession(sessionId) { /* 获取会话 */ }
  async getEncryptedPrompt(sessionId) { /* 获取加密 Prompt */ }
  async request(endpoint, options = {}) { /* 通用请求方法 */ }
}
```

---

## 2. 核心 AI 调用函数与封装类

### 2.1 CLI 命令入口

[cli.ts](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/cli.ts) 定义了所有 CLI 命令，通过 Commander.js 注册：

```typescript
program
  .command('init')
  .argument('[name]', '小说项目名称')
  .option('--ai <type>', '选择 AI 助手')
  .option('--method <type>', '选择写作方法')
  .description('初始化一个新的小说项目')
  .action(async (name, options) => { /* 实现逻辑 */ });
```

### 2.2 提示词模板渲染

CLI 提供两种模板格式渲染：

**Markdown 格式**（Claude/Cursor）：
```typescript
function generateMarkdownCommand(template: string, scriptPath: string): string {
  return template.replace(/{SCRIPT}/g, scriptPath);
}
```

**TOML 格式**（Gemini）：
```typescript
function generateTomlCommand(template: string, scriptPath: string): string {
  const descMatch = template.match(/description:\s*(.+)/);
  const description = descMatch ? descMatch[1].trim() : '命令说明';
  const content = template.replace(/^---[\s\S]*?---\n/, '');
  const processedContent = content.replace(/{SCRIPT}/g, scriptPath);
  return `description = "${escapedDescription}"\n\nprompt = ${JSON.stringify(normalizedContent)}\n`;
}
```

### 2.3 插件管理器

[manager.ts](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/plugins/manager.ts) 负责插件的安装、加载和管理：

```typescript
export class PluginManager {
  constructor(projectRoot: string) { /* 初始化 */ }
  async loadPlugins(): Promise<void> { /* 加载插件 */ }
  async installPlugin(pluginName: string, source?: string): Promise<void> { /* 安装插件 */ }
  async removePlugin(pluginName: string): Promise<void> { /* 移除插件 */ }
}
```

---

## 3. 预设提示词模板分类

### 3.1 模板文件结构

```
templates/
├── commands/                    # 核心命令模板（7个）
│   ├── constitution.md          # 创作宪法
│   ├── specify.md               # 故事规格
│   ├── clarify.md               # 决策澄清
│   ├── plan.md                  # 创作计划
│   ├── tasks.md                 # 任务分解
│   ├── write.md                 # 章节写作
│   └── analyze.md               # 质量分析
├── commands/                    # 追踪命令模板（7个）
│   ├── track.md                 # 综合追踪
│   ├── track-init.md            # 初始化追踪
│   ├── plot-check.md            # 情节检查
│   ├── timeline.md              # 时间线管理
│   ├── relations.md             # 关系追踪
│   ├── world-check.md           # 世界观验证
│   └── checklist.md             # 检查清单
├── commands/                    # 专家命令模板（1个）
│   └── expert.md                # 专家模式
└── writing-constitution-template.md  # 写作宪法模板
```

### 3.2 按功能分类的完整模板列表

#### 七步方法论命令

| 命令 | 功能 | 模板文件 | 核心输出 |
|------|------|---------|---------|
| `/constitution` | 创建创作宪法，定义核心原则 | [constitution.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/constitution.md) | `constitution.md` |
| `/specify` | 定义故事规格（渐进式4层级） | [specify.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/specify.md) | `specification.md` |
| `/clarify` | 澄清关键决策点 | [clarify.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/clarify.md) | 更新故事大纲 |
| `/plan` | 制定创作计划（含情绪曲线设计） | [plan.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/plan.md) | `creative-plan.md` |
| `/tasks` | 分解执行任务 | [tasks.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/tasks.md) | `tasks.md` |
| `/write` | AI 辅助写作章节内容 | [write.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/write.md) | 章节 Markdown 文件 |
| `/analyze` | 综合验证分析（框架/内容/专项） | [analyze.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/analyze.md) | `analysis-report.md` |

#### 追踪管理命令

| 命令 | 功能 | 模板文件 |
|------|------|---------|
| `/track` | 综合追踪与智能分析 | [track.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/track.md) |
| `/track-init` | 初始化追踪文件 | [track-init.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/track-init.md) |
| `/plot-check` | 检查情节一致性 | [plot-check.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/plot-check.md) |
| `/timeline` | 管理故事时间线 | [timeline.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/timeline.md) |
| `/relations` | 追踪角色关系 | [relations.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/relations.md) |
| `/world-check` | 验证世界观设定 | [world-check.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/world-check.md) |
| `/checklist` | 检查清单 | [checklist.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/checklist.md) |

#### 专家模式命令

| 命令 | 功能 | 模板文件 |
|------|------|---------|
| `/expert` | 列出可用专家 | [expert.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/expert.md) |
| `/expert plot` | 剧情结构专家 | [expert.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/expert.md) |
| `/expert character` | 人物塑造专家 | [expert.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/expert.md) |
| `/expert world` | 世界观构建专家 | [expert.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/expert.md) |
| `/expert style` | 风格把控专家 | [expert.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/templates/commands/expert.md) |

---

## 4. 核心提示词模板完整内容

### 4.1 `/write` - 章节写作模板

**核心结构**：

```markdown
---
description: 基于任务清单执行章节写作，自动加载上下文和验证规则
argument-hint: [章节编号或任务ID]
allowed-tools: Read(//**), Write(//stories/**/content/**), Bash(ls:*), Bash(find:*), Bash(wc:*), Bash(grep:*), Bash(*)
model: claude-sonnet-4-5-20250929
scripts:
  sh: .specify/scripts/bash/check-writing-state.sh
  ps: .specify/scripts/powershell/check-writing-state.ps1
---

## 前置检查
1. 运行脚本 `{SCRIPT}` 检查创作状态

### 查询协议（必读顺序）
**查询顺序**：
1. **先查（最高优先级）**：
   - `.specify/memory/constitution.md`（创作宪法）
   - `.specify/memory/style-reference.md`（风格参考）

2. **再查（规格和计划）**：
   - `stories/*/specification.md`（故事规格）
   - `stories/*/creative-plan.md`（创作计划）
   - `stories/*/tasks.md`（当前任务）

3. **再查（状态和数据）**：
   - `spec/tracking/character-state.json`（角色状态）
   - `spec/tracking/relationships.json`（关系网络）
   - `spec/tracking/plot-tracker.json`（情节追踪）
   - `spec/tracking/validation-rules.json`（验证规则）

4. **再查（知识库）**：
   - `spec/knowledge/` 相关文件
   - `stories/*/content/`（前文内容）

5. **再查（写作规范）**：
   - `.specify/memory/personal-voice.md`（个人语料）
   - `spec/knowledge/natural-expression.md`（自然化表达）
   - `spec/knowledge/punctuation-personality.md`（标点个性化）
   - `spec/knowledge/detail-formulas.md`（具象化公式）
   - `spec/presets/anti-ai-detection.md`（反AI检测规范）

6. **条件查询（前三章专用）**：
   - 如果章节编号 ≤ 3，额外查询 `spec/presets/golden-opening.md`（黄金开篇法则）

## 写作执行流程
### 1. 选择写作任务
从 `tasks.md` 中选择状态为 `pending` 的写作任务

### 2. 验证前置条件
- 检查相关依赖任务是否完成
- 验证必要的设定是否就绪
- 确认前序章节是否完成

### 3. 写作前提醒
**基于宪法原则提醒**：核心价值观、质量标准、风格一致性
**基于规格要求提醒**：P0元素、目标读者、内容红线

### 4. 实时辅助模式（可选）
如用户遇到困难，主动提供2-3个行动选项

### 5. 根据计划创作内容
- 开场：吸引读者，承接前文
- 发展：推进情节，深化人物
- 转折：制造冲突或悬念
- 收尾：适当收束，引出下文

### 6. 质量自检
- 宪法合规检查
- 规格符合检查
- 计划执行检查
- 格式规范检查

### 7. 保存和更新
- 将章节内容保存到 `stories/*/content/`
- 更新任务状态为 `completed`
- 记录完成时间和字数
```

### 4.2 `/specify` - 故事规格模板

**渐进式规格层级逻辑**：

```python
input_length = len(user_input)
existing_spec = check_if_exists()

if existing_spec:
    action = "upgrade" or "modify"
elif input_length < 50:
    target_level = 1  # 一句话故事
elif input_length < 300:
    target_level = 2  # 一段话概要
elif input_length < 1000:
    target_level = 3  # 一页纸大纲
else:
    target_level = 4  # 完整规格
```

**Level 4 完整规格结构**：
1. 故事概要（一句话 + 简介 + 主题）
2. 目标定位（读者画像 + 市场定位 + 量化目标）
3. 成功标准（量化指标 + 质量标准 + 读者反馈）
4. 核心需求（P0/P1/P2 分级）
5. 线索管理规格（线索定义 + 节奏规划 + 交汇点 + 伏笔 + 修改矩阵）
6. 约束条件（内容红线 + 创作约束 + 技术约束）
7. 风险评估（创作风险 + 市场风险）
8. 核心决策点（标记 `[需要澄清]`）
9. 验证清单

### 4.3 `/analyze` - 质量分析模板

**智能阶段检测逻辑**：

```json
{
  "analyze_type": "framework|content",
  "chapter_count": 0,
  "has_spec": true,
  "has_plan": true,
  "has_tasks": true,
  "reason": "原因说明"
}
```

**自动判断规则**：
- 章节数 = 0 → **框架分析**
- 章节数 < 3 → **框架分析**（提示可继续写作）
- 章节数 ≥ 3 → **内容分析**

**专项分析模式**（`--focus` 参数）：
- `--focus=opening` → 开篇专项分析（黄金开篇法则）
- `--focus=pacing` → 节奏专项分析（爽点/冲突分布）
- `--focus=character` → 人物专项分析（人物弧光）
- `--focus=foreshadow` → 伏笔专项分析（埋设与回收）
- `--focus=logic` → 逻辑专项分析（逻辑漏洞）
- `--focus=style` → 风格专项分析（文笔一致性）

---

## 5. 上下文管理机制

### 5.1 文件系统上下文存储

项目采用**文件优先**的上下文管理策略，所有上下文数据存储在本地文件中：

| 文件路径 | 内容 | 优先级 | 更新时机 |
|---------|------|--------|---------|
| `.specify/memory/constitution.md` | 创作宪法 | 最高 | `/constitution` |
| `.specify/memory/style-reference.md` | 风格参考 | 高 | `/book-internalize` |
| `stories/*/specification.md` | 故事规格 | 高 | `/specify` |
| `stories/*/creative-plan.md` | 创作计划 | 中 | `/plan` |
| `stories/*/tasks.md` | 任务清单 | 中 | `/tasks` |
| `spec/tracking/character-state.json` | 角色状态 | 中 | 每次写作 |
| `spec/tracking/relationships.json` | 关系网络 | 中 | 每次写作 |
| `spec/tracking/plot-tracker.json` | 情节追踪 | 中 | 每次写作 |
| `spec/knowledge/*.md` | 知识库 | 低 | 初始化/更新 |

### 5.2 上下文注入流程

在 `/write` 命令中，上下文按以下顺序注入：

```
用户输入 → 脚本检查 → 宪法加载 → 规格加载 → 计划加载 → 任务加载
    ↓
追踪数据加载 → 知识库加载 → 写作规范加载 → AI 生成内容 → 保存输出
```

### 5.3 上下文复用机制

**内存缓存**：AI 助手在会话期间自动缓存已读取的文件内容

**增量更新**：
- 角色状态、关系网络、情节追踪在每次写作后更新
- 规格和计划在 `/specify` 和 `/plan` 命令执行时更新
- 知识库文件在初始化或手动更新时修改

---

## 6. 参数配置

### 6.1 温度参数（Temperature）

**核心限制**：CLI 工具（Claude Code、Cursor）锁定低温度（0.0-0.2），无法直接设置

**补偿策略**：通过**创作强化指令**模拟高温效果

```
低温 AI + 强化创作提示 ≈ 高温 AI 输出
```

**创作强化指令核心内容**（已内置在 `/write` 模板中）：

| 维度 | 强化指令 | 效果 |
|------|---------|------|
| 情感表达 | "必须创造情感丰富的内容" | 提升情感深度 |
| 对话自然化 | "拒绝说明式对话，采用真实对话节奏" | 避免机械对话 |
| 场景生动化 | "要求至少3种感官体验" | 增强画面感 |
| 冲突张力 | "制造戏剧张力：动作、微表情、环境烘托" | 避免平铺直叙 |
| 节奏变化 | "长短句交替，快慢节奏切换" | 提升可读性 |

### 6.2 写作参数

| 参数 | 默认值 | 配置位置 | 说明 |
|------|--------|---------|------|
| 章节字数 | 2000-4000字 | `spec/tracking/validation-rules.json` | 每章目标字数范围 |
| 目标总字数 | 由用户指定 | `specification.md` | 故事整体目标字数 |
| 更新频率 | 由用户指定 | `specification.md` | 日更/周更/月更 |
| 章节间隔 | 无限制 | - | 用户自定义 |

### 6.3 其他参数

由于项目通过 CLI 工具调用 AI，以下参数**不可配置**：

| 参数 | 状态 | 说明 |
|------|------|------|
| `max_tokens` | 不可配置 | 由 AI 助手自动管理 |
| `top_p` | 不可配置 | 由 AI 助手自动管理 |
| `frequency_penalty` | 不可配置 | 由 AI 助手自动管理 |
| `presence_penalty` | 不可配置 | 由 AI 助手自动管理 |

---

## 7. 调用示例

### 7.1 CLI 命令调用示例

**初始化项目**：
```bash
novel init my-story --ai claude --method hero-journey
```

**输出**：
```
╔═══════════════════════════════════════╗
║     📚  Novel Writer  📝              ║
║     AI 驱动的中文小说创作工具        ║
╚═══════════════════════════════════════╝

  v0.8.9

✓ 小说项目 "my-story" 创建成功！

接下来:
─────────────────────────────
  1. cd my-story - 进入项目目录
  2. 在 Claude Code 中打开项目
  3. 使用以下斜杠命令开始创作:
     /constitution - 创建创作宪法
     /specify      - 定义故事规格
     ...
```

### 7.2 AI 斜杠命令调用示例

**创建创作宪法**：
```
/constitution 类型=奇幻，目标读者=成人，预计20万字，强调角色成长和世界观深度
```

**AI 响应**：
```markdown
# 小说创作宪法

## 元数据
- 版本：1.0.0
- 创建日期：2025-10-01
- 作者：匿名作者
- 作品：通用

## 第一章：核心价值观
### 原则1：真实性优先
**声明**：角色行为必须符合性格设定
**理由**：读者信任的基础
**执行**：每次决策前检查性格一致性

...
```

**写作章节**：
```
/write chapter=1 words=5000
```

**AI 响应**：
```markdown
# 第一章：初入江湖

天刚蒙蒙亮，林萧就被一阵急促的敲门声惊醒。

"少爷，老爷请您过去。"

他揉了揉惺忪的睡眼，看了一眼窗外。晨曦透过窗棂洒在斑驳的墙壁上，空气中弥漫着淡淡的松针气息。

...

> ✅ 章节写作完成
> - 已保存：stories/my-story/content/chapter-001.md
> - 实际字数：4852字
> - 字数要求：2000-4000字
> - 字数状态：✅ 符合要求
```

### 7.3 外部 API 调用示例

**获取加密 Prompt**（stardust-dreams 插件内部）：

```javascript
const client = new StardustAPIClient();
client.setApiKey('your_api_key');

const encryptedData = await client.getEncryptedPrompt('session_abc123');

console.log(encryptedData);
// {
//   sessionId: 'session_abc123',
//   formId: 'form_xyz789',
//   encryptedPrompt: 'base64_encoded_string',
//   iv: 'base64_encoded_iv',
//   authTag: 'base64_encoded_auth_tag',
//   sessionKey: 'base64_encoded_key',
//   expiresAt: '2024-01-01T11:00:00Z'
// }
```

---

## 8. 错误处理与重试机制

### 8.1 CLI 错误处理

**退出码**：
| 码 | 说明 |
|----|------|
| 0 | 成功 |
| 1 | 一般错误 |

**常见错误场景**：
```typescript
// 项目已存在
if (await fs.pathExists(projectPath)) {
  spinner.fail(`项目目录 "${name}" 已存在`);
  process.exit(1);
}

// 非项目目录
if (error.message === 'NOT_IN_PROJECT') {
  console.log(chalk.red('❌ 当前目录不是 novel-writer 项目'));
  process.exit(1);
}

// 插件未找到
if (!await fs.pathExists(builtinPluginPath)) {
  console.log(chalk.red(`❌ 插件 ${name} 未找到`));
  process.exit(1);
}
```

### 8.2 外部 API 错误处理

[api-client.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/api-client.js) 中的错误处理：

```javascript
async request(endpoint, options = {}) {
  try {
    const response = await fetch(url, fetchOptions);
    const data = await response.json();

    // 速率限制处理
    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      throw new Error(`请求过于频繁，请 ${retryAfter || '60'} 秒后重试`);
    }

    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error(`网络请求失败: ${error}`);
  }
}

async getSession(sessionId) {
  const response = await this.request('/api/trpc/form.getSession', { ... });
  
  if (!response?.result?.data?.success) {
    throw new Error(`会话 ${sessionId} 不存在或已过期`);
  }
  
  return response.result.data.data;
}
```

**错误码处理**：
| 状态码 | 说明 | 处理方式 |
|--------|------|---------|
| 400 | 参数错误 | 检查请求参数 |
| 401 | 认证失败 | 验证 API Key |
| 404 | 资源不存在 | 验证会话 ID |
| 429 | 速率限制 | 等待后重试（Retry-After 头） |
| 500 | 服务器错误 | 联系支持 |

### 8.3 重试机制

**当前实现**：
- 无自动重试机制
- 速率限制错误提示用户手动重试
- 网络错误直接抛出异常

**建议改进**（未来版本）：
- 添加指数退避重试（最多3次）
- 添加请求超时配置
- 添加断点续传支持

---

## 9. 提示词动态拼接逻辑

### 9.1 模板变量替换

**`{SCRIPT}` 变量**：替换为对应的脚本路径

```typescript
function generateMarkdownCommand(template: string, scriptPath: string): string {
  return template.replace(/{SCRIPT}/g, scriptPath);
}
```

**`$ARGUMENTS` 变量**：替换为用户输入的参数

```markdown
用户输入：$ARGUMENTS
```

### 9.2 插件钩子

**插件增强区**：在模板中预留插件扩展点

```markdown
<!-- PLUGIN_HOOK: genre-knowledge-write -->
<!-- 插件增强区：风格应用
     如果你安装了 genre-knowledge 插件，请在此处插入风格应用增强提示词
     参考：plugins/genre-knowledge/README.md
-->
```

### 9.3 条件加载逻辑

**黄金开篇法则条件加载**（`/plan` 和 `/write` 命令）：

```bash
# 检查是否存在黄金开篇法则文件
test -f spec/presets/golden-opening.md && echo "found" || echo "not-found"
```

**逻辑**：
- 如果存在且章节编号 ≤ 3 → 加载并应用黄金开篇法则
- 如果不存在 → 跳过，继续正常流程

**节奏配置条件加载**：

```bash
test -f spec/presets/rhythm-config.json && echo "found" || echo "not-found"
```

**逻辑**：
- 如果存在（通过 `/book-internalize` 生成）→ 应用对标作品的节奏参数
- 如果不存在 → 使用默认节奏规划

### 9.4 渐进式规格升级逻辑

```python
# 伪代码：规格层级判断
input_length = len(user_input)
existing_spec = check_if_exists()

if existing_spec:
    # 已有规格，询问升级或修改
    level = get_current_level(existing_spec)
    if user_wants_upgrade:
        new_level = min(level + 1, 4)
        upgrade_to(new_level)
    else:
        modify_spec()
else:
    # 新规格，根据输入长度判断
    if input_length < 50:
        create_level_1()
    elif input_length < 300:
        create_level_2()
    elif input_length < 1000:
        create_level_3()
    else:
        create_level_4()
```

---

## 10. 反AI检测机制

### 10.1 核心规范

[anti-ai-detection.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/spec/presets/anti-ai-detection.md) 定义了完整的反AI检测规则：

**核心原则**：
- ✅ 30-50% 单句成段
- ✅ 每段 50-100 字
- ✅ 简洁克制描写
- ✅ 短句节奏（15-25字）
- ✅ 口语化对话
- ✅ 标点个性化

**AI高频词黑名单**：
- ❌ 弥漫着、唯一的、直到、不禁、顿时
- ❌ 摇摇欲坠、空气凝固、话音未落、猛地
- ❌ 宛如、仿佛、犹如、心中暗想

### 10.2 具象化替换策略

将抽象表达替换为具体细节：

| 抽象表达 | 具体替换 |
|---------|---------|
| "最近" | "上周三下午" |
| "很多人" | "至少有5个朋友" |
| "很贵" | "一顿饭花了三百块" |
| "很远" | "开车要两小时" |
| "房间很乱" | "地上堆着三天没洗的衣服" |

### 10.3 写作规范注入

反AI检测规范在 `/write` 命令中自动加载：

```markdown
4. **再查（写作规范）**：
   - `.specify/memory/personal-voice.md`（个人语料）
   - `spec/knowledge/natural-expression.md`（自然化表达）
   - `spec/knowledge/punctuation-personality.md`（标点个性化）
   - `spec/knowledge/detail-formulas.md`（具象化公式）
   - `spec/presets/anti-ai-detection.md`（反AI检测规范）
```

---

## 11. 总结

### 11.1 AI 交互架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      Novel Writer 系统                         │
├─────────────────────────────────────────────────────────────────┤
│  CLI 命令层                                                     │
│  ├── init（初始化）                                              │
│  ├── check（环境检查）                                            │
│  ├── plugins（插件管理）                                          │
│  └── upgrade（升级）                                              │
├─────────────────────────────────────────────────────────────────┤
│  AI 斜杠命令层                                                   │
│  ├── 七步方法论（constitution → specify → clarify → plan        │
│  │              → tasks → write → analyze）                       │
│  ├── 追踪管理（track, plot-check, timeline, relations, world-check）│
│  └── 专家模式（expert plot/character/world/style）                │
├─────────────────────────────────────────────────────────────────┤
│  提示词模板层                                                   │
│  ├── 核心命令模板（15个）                                         │
│  ├── 插件命令模板（25+个）                                       │
│  └── 写作规范（anti-ai-detection, golden-opening等）              │
├─────────────────────────────────────────────────────────────────┤
│  AI 助手层                                                       │
│  ├── Claude Code（claude-sonnet-4-5-20250929）                   │
│  ├── Cursor（内置模型）                                          │
│  ├── Gemini CLI（内置模型）                                       │
│  └── 其他平台（Windsurf, Roo Code, Copilot等）                    │
├─────────────────────────────────────────────────────────────────┤
│  外部 API 层                                                     │
│  └── stardust-dreams（星尘织梦 API）                              │
└─────────────────────────────────────────────────────────────────┘
```

### 11.2 关键特点

| 特点 | 说明 |
|------|------|
| **无自建服务器** | 通过 AI 助手的斜杠命令系统交互 |
| **文件优先** | 所有上下文存储在本地文件中 |
| **模板驱动** | 提示词通过 Markdown/TOML 文件定义 |
| **低温补偿** | 通过创作强化指令模拟高温效果 |
| **反AI检测** | 内置完整的去AI味写作规范 |
| **插件扩展** | 支持第三方插件添加新命令 |

### 11.3 提示词数量统计

| 类别 | 数量 | 文件位置 |
|------|------|---------|
| 核心命令模板 | 15 | `templates/commands/` |
| 插件命令模板 | 25+ | `plugins/*/commands/` |
| 写作规范 | 6 | `spec/presets/` + `spec/knowledge/` |
| 方法预设 | 6 | `spec/presets/*/` |
| **总计** | **50+** | - |
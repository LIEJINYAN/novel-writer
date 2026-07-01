# DATABASE SCHEMA

## 1. 数据存储说明

> **重要说明**：本项目**不使用传统数据库**（如 MySQL、PostgreSQL、MongoDB），也**没有 ORM** 和**迁移工具**。所有数据以 **JSON/YAML/Markdown 文件**形式存储在本地文件系统中。

**设计理念**：
- **文件即数据库**：每个 JSON 文件相当于一张"数据表"
- **无需数据库服务**：开箱即用，零配置
- **版本友好**：便于 Git 版本控制和协作
- **手动可编辑**：用户可直接修改文件

---

## 2. 数据文件模型总览

| 文件路径 | 模型名称 | 用途说明 |
|----------|----------|----------|
| `.specify/config.json` | **项目配置** | 小说项目的基本配置（名称、AI类型、写作方法） |
| `spec/config.json` | **系统配置** | 项目级全局配置（可用方法、功能开关、偏好设置） |
| `spec/tracking/plot-tracker.json` | **情节追踪** | 主线/支线情节发展、伏笔、冲突、检查点 |
| `spec/tracking/character-state.json` | **角色状态** | 主角/配角状态、成长弧线、出场记录、一致性检查 |
| `spec/tracking/relationships.json` | **关系追踪** | 角色间关系、派系、关系矩阵、冲突 |
| `spec/tracking/timeline.json` | **时间线** | 故事时间、事件、并行事件、时间逻辑约束 |
| `spec/tracking/validation-rules.json` | **验证规则** | 角色一致性验证规则、自动修复配置、常见错误 |
| `spec/knowledge/character-profiles.md` | **角色档案** | 角色详细设定（Markdown 格式） |
| `spec/knowledge/world-setting.md` | **世界观** | 世界观规则设定（Markdown 格式） |

---

## 3. 数据文件模型详细定义

### 3.1 项目配置（.specify/config.json）

**用途**：存储单个小说项目的基本配置

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `name` | string | - | 小说项目名称 |
| `type` | string | "novel" | 项目类型（枚举：novel） |
| `ai` | string | "claude" | 默认 AI 助手类型 |
| `method` | string | "three-act" | 当前使用的写作方法 |
| `created` | string | - | 创建时间（ISO 8601） |
| `version` | string | "0.8.9" | 项目配置版本号 |
| `hybridScheme` | object/null | null | 混合方法配置（使用混合方法时） |

**`ai` 字段可选值**（枚举）：
- `claude` - Claude Code
- `cursor` - Cursor
- `gemini` - Gemini CLI
- `windsurf` - Windsurf
- `roocode` - Roo Code

**`method` 字段可选值**（枚举）：
- `three-act` - 三幕结构
- `hero-journey` - 英雄之旅
- `story-circle` - 故事圈
- `seven-point` - 七点结构
- `pixar-formula` - 皮克斯公式
- `hybrid` - 混合方法

---

### 3.2 系统配置（spec/config.json）

**用途**：存储项目级全局配置和偏好设置

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `version` | string | "0.4.0" | 配置版本号 |
| `project.name` | string | "Novel Writer" | 项目名称 |
| `project.type` | string | "novel" | 项目类型 |
| `project.language` | string | "zh-CN" | 语言代码 |
| `method.current` | string | "three-act" | 当前方法 |
| `method.available` | string[] | - | 可用方法列表 |
| `method.mixMode` | boolean | false | 是否启用混合模式 |
| `features.tracking.enabled` | boolean | true | 是否启用追踪 |
| `features.tracking.autoSave` | boolean | true | 是否自动保存 |
| `features.tracking.files` | string[] | - | 追踪文件列表 |
| `features.ai.defaultAssistant` | string | "claude" | 默认 AI 助手 |
| `features.ai.temperature` | number | 0.7 | AI 温度参数 |
| `features.ai.maxTokens` | number | 4000 | AI 最大 token 数 |
| `features.templates.customizable` | boolean | true | 是否允许自定义模板 |
| `features.templates.inheritFromPreset` | boolean | true | 是否继承预设 |
| `preferences.chapterLength.min` | number | 3000 | 章节最小字数 |
| `preferences.chapterLength.max` | number | 5000 | 章节最大字数 |
| `preferences.chapterLength.target` | number | 4000 | 章节目标字数 |
| `preferences.updateSchedule` | string | "weekly" | 更新频率 |
| `preferences.backupEnabled` | boolean | true | 是否启用备份 |

---

### 3.3 情节追踪（spec/tracking/plot-tracker.json）

**用途**：追踪主线和支线情节的发展、伏笔、冲突和检查点

#### 顶层字段

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `novel` | string | "[小说名称]" | 小说名称（关联键） |
| `lastUpdated` | string | "" | 最后更新时间 |

#### `currentState` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `chapter` | number | 1 | 当前章节号 |
| `volume` | number | 1 | 当前卷号 |
| `mainPlotStage` | string | "开端" | 当前主线阶段 |
| `location` | string | "[当前地点]" | 当前场景地点 |
| `timepoint` | string | "[故事时间]" | 当前故事时间点 |

#### `plotlines.main` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `name` | string | "[主线名称]" | 主线名称 |
| `description` | string | "[主线描述]" | 主线描述 |
| `status` | string | "active" | 状态（枚举：active/complete/paused） |
| `currentNode` | string | "[当前节点]" | 当前节点 |
| `completedNodes` | string[] | [] | 已完成节点 |
| `upcomingNodes` | string[] | [] | 即将到来的节点 |

#### `plotlines.plannedClimax` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `chapter` | number/null | null | 高潮章节号 |
| `description` | string | "" | 高潮描述 |

#### `foreshadowing` 数组（伏笔）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `id` | string | "foreshadow-001" | 伏笔唯一标识 |
| `content` | string | "[伏笔内容]" | 伏笔内容描述 |
| `planted.chapter` | number/null | null | 埋设章节 |
| `planted.description` | string | "" | 埋设描述 |
| `hints` | string[] | [] | 提示线索 |
| `plannedReveal.chapter` | number/null | null | 计划揭示章节 |
| `plannedReveal.description` | string | "" | 揭示描述 |
| `status` | string | "active" | 状态（枚举：active/revealed/dropped） |
| `importance` | string | "high" | 重要性（枚举：high/medium/low） |

#### `conflicts` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `active` | array | [] | 活跃冲突列表 |
| `resolved` | array | [] | 已解决冲突列表 |
| `upcoming` | array | [] | 即将出现的冲突列表 |

---

### 3.4 角色状态（spec/tracking/character-state.json）

**用途**：追踪主角和配角的状态、成长弧线、出场记录和一致性

#### 顶层字段

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `novel` | string | "[小说名称]" | 小说名称（关联键） |
| `lastUpdated` | string | "" | 最后更新时间 |

#### `protagonist` 对象（主角）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `name` | string | "[主角名]" | 主角名称 |

#### `protagonist.currentStatus` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `alive` | boolean | true | 是否存活 |
| `health` | string | "良好" | 健康状态 |
| `mentalState` | string | "正常" | 心理状态 |
| `location` | string | "[当前位置]" | 当前位置 |
| `chapter` | number | 1 | 最后出现章节 |
| `age` | number/null | null | 当前年龄 |
| `position` | string | "[身份/职位]" | 当前身份/职位 |
| `possessions` | string[] | [] | 持有物品 |
| `skills` | string[] | [] | 掌握技能 |
| `knowledge` | string[] | [] | 知识储备 |

#### `protagonist.development` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `arc` | string | "[成长弧线描述]" | 成长弧线描述 |
| `milestones` | array | [] | 里程碑列表 |
| `currentPhase` | string | "起点" | 当前阶段（枚举：起点/发展/转折/高潮/完成） |
| `nextGoal` | string | "" | 下一个目标 |

#### `supportingCharacters` 对象（配角）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `[配角名].role` | string | "[角色功能]" | 角色功能定位 |
| `[配角名].importance` | string | "high\|medium\|low" | 重要性（枚举：high/medium/low） |
| `[配角名].status.alive` | boolean | true | 是否存活 |
| `[配角名].status.lastSeen.chapter` | number/null | null | 最后出现章节 |
| `[配角名].status.lastSeen.location` | string | "" | 最后出现地点 |
| `[配角名].status.currentLocation` | string | "unknown" | 当前位置 |
| `[配角名].status.occupation` | string | "" | 职业 |
| `[配角名].arc.planned` | string | "" | 计划弧线 |
| `[配角名].arc.current` | string | "" | 当前进展 |
| `[配角名].secrets` | string[] | [] | 秘密列表 |
| `[配角名].motivations` | string[] | [] | 动机列表 |

#### `appearanceTracking` 数组（出场记录）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `chapter` | number | 1 | 章节号 |
| `appearances[].character` | string | "[角色名]" | 角色名称 |
| `appearances[].role` | string | "主要\|次要\|背景" | 出场角色类型 |
| `appearances[].significance` | string | "" | 出场意义 |

---

### 3.5 关系追踪（spec/tracking/relationships.json）

**用途**：追踪角色间关系、派系、关系矩阵和冲突演变

#### 顶层字段

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `novel` | string | "[小说名称]" | 小说名称（关联键） |
| `lastUpdated` | string | "" | 最后更新时间 |

#### `characters` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `[角色名].relationships.allies` | string[] | [] | 盟友列表 |
| `[角色名].relationships.enemies` | string[] | [] | 敌人列表 |
| `[角色名].relationships.romantic` | string[] | [] | 恋爱关系列表 |
| `[角色名].relationships.family` | string[] | [] | 家族关系列表 |
| `[角色名].relationships.mentors` | string[] | [] | 导师列表 |
| `[角色名].relationships.neutral` | string[] | [] | 中立关系列表 |
| `[角色名].relationships.unknown` | string[] | [] | 未知关系列表 |

#### `characters[].dynamicRelations` 数组

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `character` | string | "[角色名]" | 关联角色 |
| `initial` | string | "陌生人" | 初始关系 |
| `current` | string | "朋友" | 当前关系 |
| `trajectory` | string | "positive" | 发展轨迹（枚举：positive/negative/stable） |
| `keyEvents` | string[] | [] | 关键事件列表 |

#### `factions` 对象（派系）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `[派系名].description` | string | "" | 派系描述 |
| `[派系名].leader` | string | "" | 领导者 |
| `[派系名].members` | string[] | [] | 成员列表 |
| `[派系名].goals` | string[] | [] | 目标列表 |
| `[派系名].alliedWith` | string[] | [] | 盟友派系 |
| `[派系名].opposedTo` | string[] | [] | 敌对派系 |
| `[派系名].status` | string | "active" | 状态（枚举：active/dormant/dissolved） |

#### `history` 数组（关系变化历史）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `chapter` | number | 1 | 发生章节 |
| `changes[].type` | string | "new" | 变化类型（枚举：new/change/end） |
| `changes[].characters` | string[] | ["A", "B"] | 涉及角色 |
| `changes[].relation` | string | "初次相遇" | 关系描述 |
| `changes[].impact` | string | "low" | 影响程度（枚举：low/medium/high） |

---

### 3.6 时间线（spec/tracking/timeline.json）

**用途**：追踪故事时间、事件、并行事件和时间逻辑约束

#### 顶层字段

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `novel` | string | "[小说名称]" | 小说名称（关联键） |
| `lastUpdated` | string | "" | 最后更新时间 |

#### `storyTime` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `start` | string | "[故事开始时间]" | 故事开始时间 |
| `current` | string | "[当前故事时间]" | 当前故事时间 |
| `end` | string | "[预计结束时间]" | 预计结束时间 |

#### `events` 数组

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `chapter` | number | 1 | 发生章节 |
| `date` | string | "[故事内时间]" | 故事内日期 |
| `event` | string | "[事件描述]" | 事件描述 |
| `duration` | string | "[持续时间]" | 持续时间 |
| `participants` | string[] | [] | 参与者列表 |

#### `timeLogic` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `travelTimes.routes` | object | {} | 地点间旅行时间映射 |
| `constraints[]` | array | [] | 时间约束规则 |

---

### 3.7 验证规则（spec/tracking/validation-rules.json）

**用途**：定义角色一致性验证规则和自动修复配置

#### 顶层字段

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `version` | string | "1.0" | 规则版本 |
| `description` | string | - | 规则描述 |

#### `characters.protagonist` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `name` | string | "[主角名]" | 主角名称 |
| `aliases` | string[] | [] | 昵称/别名 |
| `forbidden` | string[] | [] | 禁止使用的称呼 |
| `traits` | string[] | [] | 核心特征 |

#### `validation_tasks` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `character_consistency.enabled` | boolean | true | 是否启用角色一致性检查 |
| `character_consistency.checks` | string[] | [] | 检查项（name_consistency/trait_consistency/behavior_consistency） |
| `relationship_validation.enabled` | boolean | true | 是否启用关系验证 |
| `relationship_validation.checks` | string[] | [] | 检查项（address_accuracy/relationship_development/interaction_logic） |
| `world_rules.enabled` | boolean | true | 是否启用世界观规则检查 |
| `world_rules.checks` | string[] | [] | 检查项（power_system/geography/timeline） |

#### `auto_fix` 对象（自动修复）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `character_names.enabled` | boolean | true | 是否启用角色名称自动修正 |
| `character_names.confidence_threshold` | number | 0.9 | 置信度阈值 |
| `addresses.enabled` | boolean | true | 是否启用称呼自动修正 |
| `addresses.confidence_threshold` | number | 0.85 | 置信度阈值 |
| `simple_typos.enabled` | boolean | true | 是否启用简单拼写修正 |
| `complex_issues.enabled` | boolean | false | 是否启用复杂问题自动修复 |

#### `validation_levels` 对象

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `quick.checks` | string[] | [] | 快速验证检查项 |
| `standard.checks` | string[] | [] | 标准验证检查项 |
| `deep.checks` | string[] | ["all"] | 深度验证检查项 |

---

## 4. 数据文件关联关系

### 4.1 Mermaid ER 图

```mermaid
erDiagram
    PROJECT_CONFIG ||--o{ PLOT_TRACKER : "novel"
    PROJECT_CONFIG ||--o{ CHARACTER_STATE : "novel"
    PROJECT_CONFIG ||--o{ RELATIONSHIPS : "novel"
    PROJECT_CONFIG ||--o{ TIMELINE : "novel"
    PROJECT_CONFIG ||--o{ VALIDATION_RULES : "novel"
    
    SYSTEM_CONFIG ||--o{ PROJECT_CONFIG : "method"
    
    CHARACTER_STATE ||--o{ RELATIONSHIPS : "protagonist.name"
    CHARACTER_STATE ||--o{ RELATIONSHIPS : "supportingCharacters"
    
    PLOT_TRACKER ||--o{ TIMELINE : "currentState.chapter"
    PLOT_TRACKER ||--o{ CHARACTER_STATE : "currentState.location"
    
    VALIDATION_RULES ||--o{ CHARACTER_STATE : "characters.protagonist.name"
    VALIDATION_RULES ||--o{ RELATIONSHIPS : "relationships"
    
    PROJECT_CONFIG {
        string name PK
        string type
        string ai
        string method
        string created
        string version
    }
    
    SYSTEM_CONFIG {
        string version
        string project.name
        string method.current
        string method.available[]
        boolean features.tracking.enabled
        string features.ai.defaultAssistant
    }
    
    PLOT_TRACKER {
        string novel FK
        object currentState
        object plotlines
        array foreshadowing
        object conflicts
    }
    
    CHARACTER_STATE {
        string novel FK
        object protagonist
        object supportingCharacters
        array appearanceTracking
        object consistency
    }
    
    RELATIONSHIPS {
        string novel FK
        object characters
        object factions
        array history
    }
    
    TIMELINE {
        string novel FK
        object storyTime
        array events
        object timeLogic
    }
    
    VALIDATION_RULES {
        string version
        object characters
        object relationships
        object validation_tasks
        object auto_fix
    }
```

### 4.2 关联关系说明

| 源文件 | 目标文件 | 关联字段 | 关系类型 |
|--------|----------|----------|----------|
| `PROJECT_CONFIG` | `PLOT_TRACKER` | `name` ↔ `novel` | 1:N |
| `PROJECT_CONFIG` | `CHARACTER_STATE` | `name` ↔ `novel` | 1:N |
| `PROJECT_CONFIG` | `RELATIONSHIPS` | `name` ↔ `novel` | 1:N |
| `PROJECT_CONFIG` | `TIMELINE` | `name` ↔ `novel` | 1:N |
| `PROJECT_CONFIG` | `VALIDATION_RULES` | `name` ↔ `characters.protagonist.name` | 1:N |
| `SYSTEM_CONFIG` | `PROJECT_CONFIG` | `method.available` → `method` | 1:N |
| `CHARACTER_STATE` | `RELATIONSHIPS` | `protagonist.name` → `characters[角色名]` | 1:N |
| `PLOT_TRACKER` | `TIMELINE` | `currentState.chapter` → `events[].chapter` | 关联 |
| `VALIDATION_RULES` | `CHARACTER_STATE` | `characters.protagonist` → `protagonist` | 验证 |

---

## 5. 索引与约束

> **说明**：本项目使用文件存储，没有传统数据库的索引概念。但通过以下方式实现类似功能：

### 5.1 唯一性约束

| 文件 | 字段 | 说明 |
|------|------|------|
| `PLOT_TRACKER` | `foreshadowing[].id` | 伏笔 ID 全局唯一（格式：`foreshadow-XXX`） |
| `CHARACTER_STATE` | `supportingCharacters[配角名]` | 配角名称唯一 |
| `RELATIONSHIPS` | `factions[派系名]` | 派系名称唯一 |

### 5.2 外键约束（逻辑层面）

| 源字段 | 目标字段 | 验证方式 |
|--------|----------|----------|
| `PLOT_TRACKER.novel` | `PROJECT_CONFIG.name` | 写作脚本检查 |
| `CHARACTER_STATE.novel` | `PROJECT_CONFIG.name` | 写作脚本检查 |
| `CHARACTER_STATE.protagonist.name` | `VALIDATION_RULES.characters.protagonist.name` | 验证规则检查 |

### 5.3 枚举约束

| 文件 | 字段 | 可选值 |
|------|------|--------|
| `PROJECT_CONFIG` | `ai` | claude, cursor, gemini, windsurf, roocode |
| `PROJECT_CONFIG` | `method` | three-act, hero-journey, story-circle, seven-point, pixar-formula, hybrid |
| `PLOT_TRACKER` | `plotlines.main.status` | active, complete, paused |
| `PLOT_TRACKER` | `foreshadowing[].status` | active, revealed, dropped |
| `PLOT_TRACKER` | `foreshadowing[].importance` | high, medium, low |
| `CHARACTER_STATE` | `protagonist.currentPhase` | 起点, 发展, 转折, 高潮, 完成 |
| `CHARACTER_STATE` | `supportingCharacters[].importance` | high, medium, low |
| `RELATIONSHIPS` | `characters[].dynamicRelations[].trajectory` | positive, negative, stable |
| `RELATIONSHIPS` | `factions[].status` | active, dormant, dissolved |
| `RELATIONSHIPS` | `history[].changes[].impact` | low, medium, high |

---

## 6. 数据迁移

> **重要说明**：本项目**没有迁移工具**。配置文件版本升级通过以下方式处理：

### 6.1 版本升级机制

| 场景 | 处理方式 |
|------|----------|
| 新增字段 | 写作脚本自动检测并添加默认值 |
| 删除字段 | 保留旧字段，写作脚本忽略 |
| 字段重命名 | 脚本兼容新旧字段名 |
| 结构变更 | 通过 `upgrade` CLI 命令执行 |

### 6.2 升级命令

```bash
# 升级项目配置文件到最新版本
node dist/cli.js upgrade
```

### 6.3 版本兼容性

| 配置版本 | 兼容说明 |
|----------|----------|
| `< 0.8.0` | 需要手动更新 `method` 字段 |
| `0.8.x` | 支持混合方法（`hybridScheme` 字段） |
| `>= 0.9.0` | 新增验证规则支持 |

---

## 7. 数据文件操作示例

### 7.1 读取配置

```typescript
// src/utils/project.ts
const configPath = path.join(projectRoot, '.specify', 'config.json');
const config = await fs.readJson(configPath);
```

### 7.2 更新追踪文件

```typescript
// 更新情节追踪
const plotTracker = await fs.readJson('spec/tracking/plot-tracker.json');
plotTracker.currentState.chapter = 5;
plotTracker.lastUpdated = new Date().toISOString();
await fs.writeJson('spec/tracking/plot-tracker.json', plotTracker, { spaces: 2 });
```

### 7.3 验证数据一致性

```typescript
// 使用 validation-rules 验证角色名称
const rules = await fs.readJson('spec/tracking/validation-rules.json');
if (rules.characters.protagonist.forbidden.includes(inputName)) {
  throw new Error(`禁止使用称呼: ${inputName}`);
}
```

---

## 8. 总结

| 项目 | 说明 |
|------|------|
| **数据库类型** | 文件系统（JSON/YAML/Markdown） |
| **ORM** | 不适用 |
| **迁移工具** | 不适用（使用 upgrade 命令） |
| **索引** | 逻辑层面的唯一性约束 |
| **外键** | 逻辑层面的关联检查 |
| **备份** | Git 版本控制 + 手动备份 |

**核心设计优势**：
1. **零配置启动**：无需安装数据库服务
2. **版本友好**：便于 Git 协作和历史回溯
3. **人工可编辑**：用户可直接修改文件
4. **跨平台兼容**：所有文件格式平台无关
# Backup Guide

> **注意**：本项目是一个 CLI 工具，所有数据均存储在本地文件系统中，不使用传统数据库。以下内容包含通用模板，请根据实际情况补充。

---

## 1. 需要备份的内容列表

### 1.1 项目根目录下的持久化数据

#### 🔴 高优先级（不可再生，核心用户数据）

| 路径 | 说明 | 文件类型 | 备份必要性 |
|------|------|---------|-----------|
| `stories/` | 生成的小说章节内容 | Markdown | **必须备份** |
| `spec/tracking/` | 追踪数据（人物状态、情节、关系、时间线） | JSON | **必须备份** |
| `spec/knowledge/` | 知识库（人物档案、世界设定等） | Markdown/JSON | **必须备份** |
| `.specify/memory/` | 写作记忆（个人文风、写作宪法） | Markdown | **必须备份** |
| `.specify/config.json` | 项目核心配置 | JSON | **必须备份** |
| `spec/config.json` | 规范配置 | JSON | **必须备份** |

#### 🟡 中优先级（可部分再生，但建议备份）

| 路径 | 说明 | 文件类型 | 备份必要性 |
|------|------|---------|-----------|
| `.claude/commands/` | Claude AI 命令文件 | Markdown | 建议备份 |
| `.cursor/commands/` | Cursor AI 命令文件 | Markdown | 建议备份 |
| `.gemini/commands/` | Gemini AI 命令文件 | TOML | 建议备份 |
| `.specify/experts/` | 专家模式配置 | Markdown | 建议备份 |
| `spec/presets/` | 自定义预设写作方法 | Markdown/YAML | 建议备份 |
| `backup/` | 自动备份目录 | 完整目录 | 建议备份 |

#### 🟢 低优先级（可完全再生）

| 路径 | 说明 | 文件类型 | 备份必要性 |
|------|------|---------|-----------|
| `.specify/scripts/` | 脚本文件 | Shell/PowerShell | 可通过 `novel upgrade` 恢复 |
| `.specify/templates/` | 模板文件 | Markdown/JSON | 可通过 `novel upgrade` 恢复 |

### 1.2 用户主目录下的全局数据

| 路径 | 说明 | 文件类型 | 备份必要性 |
|------|------|---------|-----------|
| `~/.novel/stardust/auth.enc` | 星尘织梦插件加密认证信息 | 加密文件 | **必须备份** |
| `~/.novel/stardust/config.json` | 星尘织梦插件配置 | JSON | 建议备份 |

> **重要提示**：`auth.enc` 使用设备特征密钥加密（基于主机名、用户名、操作系统等），在不同设备上无法解密。备份后仅能在同一设备上恢复。

### 1.3 环境配置文件

| 路径 | 说明 | 备份必要性 |
|------|------|-----------|
| `.env` | 环境变量配置（API Key 等） | **必须备份** |
| `.env.local` | 本地环境变量 | **必须备份** |

---

## 2. 推荐的备份命令

### 2.1 使用 `novel upgrade` 内置备份（推荐）

项目已内置备份机制，在执行升级时会自动创建备份：

```bash
# 升级时自动创建备份到 backup/<timestamp>/ 目录
novel upgrade --ai claude
```

**备份内容**（由 [cli.ts](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/cli.ts#L1181-L1249) 中的 `createBackup()` 函数实现）：
- AI 命令目录（`.claude/commands/` 等）
- `.specify/scripts/`
- `.specify/templates/`
- `.specify/memory/`
- `BACKUP_INFO.json`（备份元数据）

> **⚠️ 重要警告**：内置备份**不包含**以下核心用户数据：
> - `stories/`（生成的小说内容）
> - `spec/tracking/`（追踪数据）
> - `spec/knowledge/`（知识库）
> 
> 这些目录需要通过手动备份或 Git 版本控制来保护。

### 2.2 Linux/macOS 手动备份命令

#### 完整项目备份（tar 打包）

```bash
# 创建完整项目备份（排除 node_modules 和临时文件）
tar -czvf novel-writer-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  --exclude='node_modules' \
  --exclude='dist' \
  --exclude='.git' \
  --exclude='*.log' \
  --exclude='.vscode' \
  --exclude='.DS_Store' \
  .
```

#### 仅备份核心用户数据

```bash
# 仅备份不可再生的核心数据
tar -czvf novel-writer-core-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  stories/ \
  spec/tracking/ \
  spec/knowledge/ \
  spec/config.json \
  .specify/memory/ \
  .specify/config.json \
  .claude/commands/ \
  .cursor/commands/ \
  .gemini/commands/
```

#### 备份全局配置

```bash
# 备份星尘织梦插件认证信息
tar -czvf stardust-config-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  ~/.novel/stardust/

# 备份环境变量文件
cp .env ~/backup/novel-writer/.env.backup-$(date +%Y%m%d)
```

### 2.3 Windows PowerShell 手动备份命令

#### 完整项目备份（7zip 打包）

```powershell
# 安装 7zip 后使用
& "C:\Program Files\7-Zip\7z.exe" a -tzip `
  novel-writer-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').zip `
  . `
  -xr!node_modules `
  -xr!dist `
  -xr!.git `
  -xr!*.log `
  -xr!.vscode
```

#### 仅备份核心用户数据

```powershell
# 创建核心数据备份目录
$backupDir = "novel-writer-core-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Force -Path $backupDir

# 复制核心数据
Copy-Item -Recurse -Force stories "$backupDir\"
Copy-Item -Recurse -Force spec\tracking "$backupDir\spec\"
Copy-Item -Recurse -Force spec\knowledge "$backupDir\spec\"
Copy-Item -Force spec\config.json "$backupDir\spec\"
Copy-Item -Recurse -Force .specify\memory "$backupDir\.specify\"
Copy-Item -Force .specify\config.json "$backupDir\.specify\"

# 压缩
& "C:\Program Files\7-Zip\7z.exe" a -tzip "$backupDir.zip" $backupDir
Remove-Item -Recurse $backupDir
```

---

## 3. 建议的备份频率

### 3.1 按操作频率

| 操作类型 | 建议备份频率 | 说明 |
|---------|-------------|------|
| 日常写作 | 每次完成后手动备份 | 使用内置升级命令或手动打包 |
| 重大修改 | 操作前强制备份 | 如：修改写作方法、升级项目版本 |
| 定期备份 | 每周一次 | 使用定时任务自动执行 |

### 3.2 定时任务配置示例

#### Linux/macOS crontab

```bash
# 编辑 crontab
crontab -e

# 添加每周日凌晨 2 点自动备份
0 2 * * 0 cd /path/to/your/novel/project && \
  tar -czvf ~/backup/novel-weekly-$(date +%Y%m%d).tar.gz \
  --exclude='node_modules' --exclude='dist' --exclude='.git' .
```

#### Windows 任务计划程序

创建批处理脚本 `backup-novel.bat`：

```batch
@echo off
setlocal

set "PROJECT_DIR=请根据你的环境填写"
set "BACKUP_DIR=请根据你的环境填写"
set "TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%-%time:~0,2%%time:~3,2%%time:~6,2%"

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

"C:\Program Files\7-Zip\7z.exe" a -tzip ^
  "%BACKUP_DIR%\novel-writer-backup-%TIMESTAMP%.zip" ^
  "%PROJECT_DIR%" ^
  -xr!node_modules ^
  -xr!dist ^
  -xr!.git

endlocal
```

然后在任务计划程序中创建定时任务执行此脚本。

---

## 4. 恢复步骤

### 4.1 从 `novel upgrade` 自动备份恢复

```bash
# 1. 查看可用备份
ls backup/

# 2. 选择要恢复的备份版本
# 例如：backup/2025-09-29T14-08-04

# 3. 恢复 AI 命令目录
cp -r backup/2025-09-29T14-08-04/.claude/commands/ .claude/commands/

# 4. 恢复脚本
cp -r backup/2025-09-29T14-08-04/.specify/scripts/ .specify/scripts/

# 5. 恢复模板
cp -r backup/2025-09-29T14-08-04/.specify/templates/ .specify/templates/

# 6. 恢复记忆
cp -r backup/2025-09-29T14-08-04/.specify/memory/ .specify/memory/
```

### 4.2 从 tar/zip 备份完整恢复

#### Linux/macOS

```bash
# 1. 解压备份文件
tar -xzvf novel-writer-backup-20250929-140804.tar.gz

# 2. 进入解压目录
cd novel-writer-backup-20250929-140804

# 3. 重新安装依赖
npm install --ignore-scripts

# 4. 重新构建
npm run build
npm run build:commands
```

#### Windows PowerShell

```powershell
# 1. 解压备份文件
& "C:\Program Files\7-Zip\7z.exe" x novel-writer-backup-20250929-140804.zip

# 2. 进入解压目录
cd novel-writer-backup-20250929-140804

# 3. 重新安装依赖
npm install --ignore-scripts

# 4. 重新构建
npm run build
npm run build:commands
```

### 4.3 恢复全局配置（星尘织梦插件）

```bash
# 1. 解压全局配置备份
tar -xzvf stardust-config-backup-20250929-140804.tar.gz

# 2. 恢复到用户主目录
cp -r .novel/stardust/ ~/.novel/stardust/
```

### 4.4 恢复环境变量

```bash
# 恢复 .env 文件
cp ~/backup/novel-writer/.env.backup-20250929 .env
```

---

## 5. 可选的云同步方案

### 5.1 使用 rclone 同步到云端存储

```bash
# 安装 rclone（根据操作系统选择安装方式）
# https://rclone.org/downloads/

# 配置云端存储（如 Google Drive、OneDrive、阿里云等）
rclone config

# 同步核心数据到云端
rclone sync -P \
  /path/to/your/novel/project/stories \
  remote:novel-writer/stories

# 同步追踪数据
rclone sync -P \
  /path/to/your/novel/project/spec/tracking \
  remote:novel-writer/tracking

# 同步知识库
rclone sync -P \
  /path/to/your/novel/project/spec/knowledge \
  remote:novel-writer/knowledge
```

### 5.2 使用 rsync 同步到远程服务器

```bash
# 同步到远程服务器
rsync -av --delete \
  --exclude='node_modules' \
  --exclude='dist' \
  --exclude='.git' \
  /path/to/your/novel/project/ \
  user@remote-server:/path/to/backup/novel-writer/
```

### 5.3 使用 Git 版本控制

> **注意**：项目的 `.gitignore` 并未排除核心数据目录（`stories/`、`spec/tracking/`、`spec/knowledge/`、`.specify/memory/`），这些目录**已被 Git 追踪**。因此 Git 是一种有效的备份方案。

```bash
# 查看当前状态
git status

# 提交所有更改
git add .
git commit -m "备份核心写作数据"

# 推送到远程仓库
git push origin main
```

**已排除的目录**（无需备份）：
- `node_modules/` - 依赖包，可重新安装
- `dist/` - 构建产物，可重新构建
- `.env*` - 环境变量，包含敏感信息
- `.claude/`, `.codex/` - AI 工具配置
- IDE/OS 临时文件

---

## 6. 备份验证与测试

### 6.1 验证备份完整性

```bash
# Linux/macOS
tar -tzf novel-writer-backup-20250929-140804.tar.gz | head -20

# Windows PowerShell
& "C:\Program Files\7-Zip\7z.exe" l novel-writer-backup-20250929-140804.zip
```

### 6.2 测试恢复流程

> **强烈建议**：定期测试备份恢复流程，确保备份文件有效。

```bash
# 1. 创建测试目录
mkdir ~/test-recovery
cd ~/test-recovery

# 2. 解压备份
tar -xzvf ~/backup/novel-writer-backup-20250929-140804.tar.gz

# 3. 验证项目结构
ls -la
ls -la stories/
ls -la spec/tracking/

# 4. 验证配置文件
cat .specify/config.json
cat spec/config.json

# 5. 尝试初始化（验证数据完整性）
node dist/cli.js check
```

---

## 7. 注意事项

### 7.1 敏感信息保护

- **API Key**：`.env` 文件包含敏感的 API Key，备份时注意存储安全
- **加密认证**：`~/.novel/stardust/auth.enc` 使用设备特征加密，跨设备恢复需要重新认证
- **权限设置**：确保备份文件权限正确（建议仅当前用户可读写）

### 7.2 备份存储建议

| 存储方式 | 优点 | 缺点 | 适用场景 |
|---------|------|------|---------|
| 本地硬盘 | 速度快、成本低 | 单点故障风险 | 日常备份 |
| 外部硬盘 | 物理隔离、安全性高 | 需要手动操作 | 定期全量备份 |
| 云端存储 | 自动同步、异地备份 | 需要网络、有成本 | 重要数据长期备份 |
| Git 仓库 | 版本历史、协作方便 | 隐私风险、容量限制 | 非敏感数据 |

### 7.3 建议的备份策略

1. **日常备份**：每次写作完成后使用 `novel upgrade` 或手动打包核心数据
2. **每周备份**：使用定时任务创建完整项目备份
3. **月度备份**：将备份文件复制到外部硬盘或云端存储
4. **异地备份**：至少保留一份备份在不同地理位置

---

## 8. 紧急恢复检查表

当数据丢失或损坏时，按以下步骤操作：

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 停止写入 | 立即停止任何写入操作，避免覆盖数据 |
| 2 | 检查备份 | 查看 `backup/` 目录是否有可用备份 |
| 3 | 选择备份 | 根据时间戳选择最近的有效备份 |
| 4 | 恢复数据 | 按照第 4 节的恢复步骤执行 |
| 5 | 验证恢复 | 检查文件是否完整、配置是否正确 |
| 6 | 测试功能 | 运行 `novel check` 和简单命令验证 |
| 7 | 重新备份 | 恢复成功后立即创建新的备份 |

---

> ⚠️ **重要提醒**：建议手动测试备份恢复流程，确保备份文件可正常恢复。备份只有在成功恢复时才有意义。
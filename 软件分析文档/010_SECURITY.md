# Security Guide

> **注意**：本项目是一个 CLI 工具，不包含 Web 服务端组件，攻击面相对较小。但仍需注意以下安全风险。

---

## 1. 已识别的安全风险

### 1.1 高风险：模板注入风险

**位置**：[template-engine.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/template-engine.js)

**风险描述**：
- `evaluateCondition()` 方法实现了一个简单的表达式求值器，支持比较操作符和逻辑操作符
- `getValueByPath()` 方法允许通过点号访问嵌套属性，甚至支持数组索引
- 如果 Prompt 模板内容可由用户控制，攻击者可以构造恶意条件表达式或访问任意属性

**相关代码**：

```javascript
// evaluateCondition - 支持多种操作符
evaluateCondition(condition, parameters) {
  const operators = {
    '==': (a, b) => a == b,
    '===': (a, b) => a === b,
    '>': (a, b) => a > b,
    '<': (a, b) => a < b,
    '&&': (a, b) => a && b,
    '||': (a, b) => a || b
  };
  
  // 复杂条件（包含操作符）
  for (const [op, fn] of Object.entries(operators)) {
    if (condition.includes(op)) {
      const parts = condition.split(op).map(p => p.trim());
      if (parts.length === 2) {
        const left = this.getValueByPath(parameters, parts[0]) || parts[0];
        const right = this.getValueByPath(parameters, parts[1]) || parts[1];
        return fn(left, right);
      }
    }
  }
}

// getValueByPath - 支持嵌套属性访问和数组索引
getValueByPath(object, path) {
  const parts = path.split('.');
  let current = object;
  
  for (const part of parts) {
    // 支持数组索引
    const arrayMatch = part.match(/^(\w+)\[(\d+)\]$/);
    if (arrayMatch) {
      current = current[arrayMatch[1]];
      if (Array.isArray(current)) {
        current = current[parseInt(arrayMatch[2], 10)];
      }
    } else {
      current = current[part];
    }
  }
  return current;
}
```

**建议修复方法**：
1. 限制条件表达式中允许使用的变量名，只允许预定义的白名单变量
2. 对用户输入的参数进行严格的类型和格式验证
3. 在处理循环和条件时，限制嵌套深度
4. 考虑使用沙箱化的表达式求值库（如 `expr-eval`）替代自定义实现

---

### 1.2 中风险：固定盐值问题

**位置**：[secure-storage.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/secure-storage.js#L214-L226)

**风险描述**：
- `getDeviceKey()` 方法使用硬编码的盐值 `'stardust-dreams-2024'`
- 设备密钥基于主机名、用户名、操作系统和固定盐值生成
- 如果攻击者获取了目标设备的基本信息，就可以推导出相同的设备密钥

**相关代码**：

```javascript
getDeviceKey() {
  const deviceInfo = [
    os.hostname(),           // 主机名
    os.userInfo().username,   // 用户名
    os.platform(),           // 操作系统
    os.arch(),              // 架构
    'stardust-dreams-2024'  // 固定盐值 ⚠️
  ].join(':');

  return crypto.createHash('sha256').update(deviceInfo).digest();
}
```

**建议修复方法**：
1. 使用每个安装实例唯一的随机盐值，存储在本地配置文件中
2. 在首次运行时生成随机盐值：`crypto.randomBytes(32).toString('hex')`
3. 将随机盐值与设备信息结合使用，提高密钥推导难度

---

### 1.3 中风险：错误信息泄漏

**位置**：[cli.ts](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/cli.ts#L596)

**风险描述**：
- `console.error(error)` 会输出完整的错误对象，包括堆栈跟踪
- 错误信息可能包含文件路径、API 响应、环境变量值等敏感信息
- 在 DEBUG 模式下，debug 日志可能输出更多内部信息

**相关代码**：

```typescript
} catch (error) {
  spinner.fail(chalk.red('项目初始化失败'));
  console.error(error);  // ⚠️ 输出完整错误对象
  process.exit(1);
}
```

**建议修复方法**：
1. 只输出错误消息，不输出完整错误对象：`console.error(chalk.red(error.message))`
2. 在生产环境中禁止输出堆栈跟踪
3. 将详细错误信息记录到安全的日志文件中，而非直接输出到控制台
4. 对敏感信息进行脱敏处理

---

### 1.4 低风险：字符串安全清理无效

**位置**：[decryptor.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/decryptor.js#L112-L134)、[prompt-manager.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/prompt-manager.js#L134-L156)

**风险描述**：
- JavaScript 中无法真正覆写字符串内存
- `secureClear()` 方法虽然尝试清理敏感数据，但对字符串只能释放引用，无法擦除内存中的实际内容
- 解密后的 Prompt 内容在垃圾回收前仍然存在于内存中

**相关代码**：

```javascript
secureClear(data) {
  if (!data) return;
  
  try {
    if (typeof data === 'string') {
      // 对于字符串，无法真正覆写，但可以释放引用 ⚠️
      data = null;
    } else if (Buffer.isBuffer(data)) {
      // 对于 Buffer，可以填充零
      data.fill(0);
      data = null;
    }
  } catch (e) {
    // 忽略清理错误
  }
}
```

**建议修复方法**：
1. 使用 Buffer 存储敏感数据，而非字符串
2. 对 Buffer 数据使用 `fill(0)` 进行覆写
3. 缩短敏感数据在内存中的停留时间，尽快使用并释放
4. 考虑使用 `node-security` 等安全内存管理库

---

### 1.5 低风险：输入验证不足

**位置**：[api-client.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/api-client.js)

**风险描述**：
- `sessionId` 和 `apiKey` 参数直接传递给 API 请求，没有进行长度和格式验证
- 虽然当前项目是 CLI 工具，输入主要来自用户，但缺乏验证仍可能导致意外行为

**相关代码**：

```javascript
async getSession(sessionId) {
  const response = await this.request('/api/trpc/form.getSession', {
    method: 'POST',
    body: {
      json: { sessionId }  // ⚠️ 未验证 sessionId
    }
  });
}

async getEncryptedPrompt(sessionId) {
  const response = await this.request('/api/trpc/form.getPrompt', {
    method: 'POST',
    body: {
      json: {
        sessionId,
        apiKey: this.apiKey  // ⚠️ 未验证 apiKey
      }
    }
  });
}
```

**建议修复方法**：
1. 添加参数格式验证（如 sessionId 应为 UUID 格式）
2. 添加参数长度限制
3. 对 API Key 进行格式检查（如长度、字符集）

---

## 2. 正面安全实践

### 2.1 无硬编码凭证

项目中所有 API Key 和敏感配置都通过环境变量获取，没有硬编码的密钥。

```javascript
// api-client.js
const API_BASE = process.env.STARDUST_API_URL || 'https://api.stardust-dreams.com';

export class StardustAPIClient {
  constructor() {
    this.baseUrl = API_BASE;
    this.apiKey = process.env.STARDUST_API_KEY || null;
  }
}
```

### 2.2 HTTPS 默认配置

所有 API 请求默认使用 HTTPS，通信过程加密传输。

```javascript
const API_BASE = process.env.STARDUST_API_URL || 'https://api.stardust-dreams.com';
```

### 2.3 .env 文件已加入 .gitignore

环境变量文件已正确排除在版本控制之外：

```gitignore
# .gitignore
.env
.env.local
.env.production
```

### 2.4 AES-256-GCM 加密

使用安全的 AES-256-GCM 算法，包含随机 IV 和认证标签：

```javascript
// decryptor.js
this.algorithm = 'aes-256-gcm';
this.ivLength = 16;
this.tagLength = 16;

const iv = Buffer.from(encryptedData.iv, 'hex');
const authTag = Buffer.from(encryptedData.authTag, 'hex');
const decipher = crypto.createDecipheriv(this.algorithm, key, iv);
decipher.setAuthTag(authTag);
```

### 2.5 Prompt 仅在内存中处理

解密后的 Prompt 内容仅在内存中使用，永不持久化到磁盘：

```javascript
// prompt-manager.js
async usePrompt(sessionId, apiKey = null) {
  let decryptedPrompt = null;
  
  try {
    // 获取加密的 Prompt
    const encryptedData = await apiClient.getEncryptedPrompt(sessionId);
    
    // 内存中解密
    decryptedPrompt = await this.decryptInMemory(
      { encrypted: encryptedData.encryptedPrompt, iv: encryptedData.iv, authTag: encryptedData.authTag },
      encryptedData.sessionKey
    );
    
    return { prompt: decryptedPrompt };
    
  } finally {
    // 强制清理内存中的敏感数据
    this.clearSensitiveData(decryptedPrompt);
  }
}
```

---

## 3. 环境变量管理

### 3.1 正确使用 .env 文件

```bash
# 创建 .env 文件
cat > .env << 'EOF'
# 星尘织梦 API 密钥
STARDUST_API_KEY=your_api_key_here

# API 地址（可选，默认为官方地址）
STARDUST_API_URL=https://api.stardust-dreams.com

# 调试模式（生产环境设为 false）
DEBUG=false
EOF
```

### 3.2 .gitignore 配置

确保以下文件已加入 `.gitignore`：

```gitignore
# 环境变量文件
.env
.env.local
.env.production
.env.*.local

# 敏感配置
config.local.js
config.local.ts

# 日志文件
*.log
npm-debug.log*
```

### 3.3 环境变量读取最佳实践

```typescript
// 使用 dotenv 加载环境变量（如果项目已安装）
import dotenv from 'dotenv';
dotenv.config();

// 获取环境变量时提供默认值和类型转换
const apiKey = process.env.STARDUST_API_KEY || '';
const apiUrl = process.env.STARDUST_API_URL || 'https://api.stardust-dreams.com';
const debugMode = process.env.DEBUG === 'true';

// 在启动时验证必要的环境变量
if (!apiKey) {
  console.error('错误: STARDUST_API_KEY 环境变量未设置');
  process.exit(1);
}
```

---

## 4. API Key 轮换策略

### 4.1 定期轮换建议

| 频率 | 适用场景 |
|------|---------|
| 每月 | 开发环境 API Key |
| 每季度 | 生产环境 API Key（低风险） |
| 每月 | 生产环境 API Key（高风险） |
| 立即 | 怀疑密钥泄露时 |

### 4.2 轮换步骤

```bash
# 1. 在 API 提供商平台生成新的 API Key
# 2. 更新 .env 文件
STARDUST_API_KEY=new_api_key_here

# 3. 验证新密钥是否生效
node -e "const client = require('./plugins/stardust-dreams/lib/api-client.js').apiClient; client.setApiKey('new_key'); console.log('密钥已更新');"

# 4. 在 API 提供商平台禁用旧密钥
# 5. 记录轮换日志（可选）
echo "$(date) - API Key 已轮换" >> security-log.txt
```

### 4.3 轮换自动化（可选）

```bash
#!/bin/bash
# api-key-rotation.sh

# 备份当前密钥
BACKUP_FILE="api-key-backup-$(date +%Y%m%d).txt"
echo "STARDUST_API_KEY=$(cat .env | grep STARDUST_API_KEY | cut -d= -f2)" > "$BACKUP_FILE"

# 生成新密钥（示例：实际应从 API 提供商获取）
# NEW_KEY=$(curl -s https://api.provider.com/generate-key)

# 更新 .env 文件
# sed -i "s/STARDUST_API_KEY=.*/STARDUST_API_KEY=$NEW_KEY/" .env

echo "API Key 轮换完成，旧密钥已备份到 $BACKUP_FILE"
```

---

## 5. 推荐的安全工具

### 5.1 代码安全扫描

| 工具 | 用途 | 安装命令 |
|------|------|---------|
| **git-secrets** | 防止密钥提交到 Git | `brew install git-secrets` |
| **detect-secrets** | 检测代码中的敏感信息 | `pip install detect-secrets` |
| **ESLint + eslint-plugin-security** | JavaScript 安全规则检查 | `npm install eslint eslint-plugin-security` |
| **npm audit** | 检测依赖包漏洞 | `npm audit` |

### 5.2 git-secrets 使用配置

```bash
# 安装 git-secrets
brew install git-secrets

# 在项目中初始化
git secrets --install
git secrets --register-aws
git secrets --add 'STARDUST_API_KEY'
git secrets --add 'api_key'
git secrets --add 'password'

# 扫描历史提交
git secrets --scan-history

# 扫描当前目录
git secrets --scan
```

### 5.3 detect-secrets 使用配置

```bash
# 安装 detect-secrets
pip install detect-secrets

# 初始化检测配置
detect-secrets init

# 扫描项目
detect-secrets scan > .secrets.baseline

# 审核检测结果
detect-secrets audit .secrets.baseline
```

### 5.4 ESLint 安全规则

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['security'],
  rules: {
    'security/detect-buffer-noassert': 'error',
    'security/detect-child-process': 'warn',
    'security/detect-disable-mustache-escape': 'error',
    'security/detect-eval-with-expression': 'error',
    'security/detect-new-func': 'error',
    'security/detect-no-csrf-before-method-override': 'error',
    'security/detect-non-literal-fs-filename': 'error',
    'security/detect-non-literal-regexp': 'warn',
    'security/detect-non-literal-require': 'error',
    'security/detect-object-injection': 'warn',
    'security/detect-possible-timing-attacks': 'warn',
    'security/detect-pseudoRandomBytes': 'error',
    'security/detect-unsafe-regex': 'warn',
  }
};
```

---

## 6. 安全最佳实践清单

### 6.1 开发阶段

- [ ] 使用环境变量存储所有敏感配置
- [ ] 确保 `.env` 文件已加入 `.gitignore`
- [ ] 对用户输入进行严格验证和清理
- [ ] 使用安全的加密算法（AES-256-GCM）
- [ ] 避免在日志中记录敏感信息
- [ ] 使用参数化查询（如果使用数据库）
- [ ] 定期运行依赖漏洞扫描（`npm audit`）

### 6.2 部署阶段

- [ ] 最小化运行权限，不要使用 root 用户
- [ ] 配置防火墙规则，限制网络访问
- [ ] 启用 HTTPS，强制加密通信
- [ ] 设置合理的超时和速率限制
- [ ] 定期轮换 API Key 和密码
- [ ] 备份加密密钥和配置文件

### 6.3 运维阶段

- [ ] 监控异常日志和安全事件
- [ ] 定期进行安全审计
- [ ] 及时更新依赖包，修复已知漏洞
- [ ] 建立应急响应流程
- [ ] 定期测试备份恢复流程

---

## 7. 安全风险评估总结

| 风险类型 | 严重程度 | 当前状态 | 建议优先级 |
|---------|---------|---------|-----------|
| 模板注入 | 🔴 高 | 存在 | 立即修复 |
| 固定盐值 | 🟡 中 | 存在 | 计划修复 |
| 错误信息泄漏 | 🟡 中 | 存在 | 计划修复 |
| 字符串清理无效 | 🟢 低 | 存在 | 低优先级 |
| 输入验证不足 | 🟢 低 | 存在 | 低优先级 |

> **总体评估**：本项目作为 CLI 工具，攻击面较小。主要风险集中在模板引擎的表达式求值和加密密钥生成方面。建议优先修复模板注入风险，并在后续版本中改进加密方案。

> ⚠️ **重要提醒**：建议定期进行安全审计，并在生产环境部署前进行全面的安全测试。
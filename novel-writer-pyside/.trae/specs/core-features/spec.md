# 核心功能补齐 Spec

## Why

路线图 Phase 3 的创作向导和 Phase 4 的 CredentialVault 安全存储未实现。创作向导可引导用户完成七步创作流程，CredentialVault 可加密存储 API Key 避免明文泄露。

## What Changes

1. **创作向导** — 向导式对话框，引导用户依次完成七步：宪法→规格→澄清→计划→任务→写作→分析
2. **CredentialVault** — API Key 加密存储，使用 `cryptography.fernet` + PBKDF2 派生密钥，替代当前明文存储

## Impact
- Affected code: `ui/dialogs/creative_wizard.py`（新建）、`services/ai_service.py`、`ui/dialogs/ai_settings_dialog.py`、`core/security/vault.py`（新建）

## ADDED Requirements

### Requirement: 七步创作向导
系统 SHALL 提供向导式对话框，引导用户完成七步创作流程。

#### Scenario: 完整向导流程
- **WHEN** 用户点击菜单 "写作 → 创作宪法"
- **THEN** 弹出向导对话框，第一步：创作宪法
- **WHEN** 用户填写并点击"下一步"
- **THEN** 调用 AI 生成宪法，完成后进入下一步
- **WHEN** 用户在向导中到达"AI 续写"步骤
- **THEN** 打开编辑器并触发续写

### Requirement: CredentialVault
系统 SHALL 提供加密存储 API Key 的凭证保险库。

#### Scenario: 存储 API Key
- **WHEN** 用户在 AI 设置对话框中输入 API Key 并保存
- **THEN** 使用 CredentialVault 加密存储到本地文件
- **WHEN** AI 调用需要 API Key
- **THEN** 解密读取，内存中使用后立即清理

## MODIFIED Requirements
- `ui/dialogs/ai_settings_dialog.py` 保存 API Key 时调用 `CredentialVault` 而非明文存储
- `core/ai/manager.py` 读取 API Key 时调用 `CredentialVault.get_api_key()` 解密

## REMOVED Requirements
无

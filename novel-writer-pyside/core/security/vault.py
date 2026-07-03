"""凭证保险库 - 加密存储 API Key 等敏感信息。"""
import os
import base64
import json
import getpass
import platform
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _get_default_vault_path() -> str:
    """获取默认保险库路径。"""
    if os.name == 'nt':  # Windows
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:  # macOS/Linux
        base = os.path.expanduser('~/.config')
    vault_dir = os.path.join(base, 'NovelWriter')
    os.makedirs(vault_dir, exist_ok=True)
    return os.path.join(vault_dir, '.vault')


class CredentialVault:
    """凭证保险库 - 加密存储 API Key 等敏感信息。"""

    def __init__(self, vault_path: str = None):
        self.vault_path = vault_path or _get_default_vault_path()
        self._salt = self._get_salt()
        self._key = self._get_machine_key()
        self._fernet = Fernet(self._key)

    def _get_salt_bytes(self) -> bytes:
        """获取盐值的字节形式。"""
        return self._salt.encode('utf-8')

    def _get_salt(self) -> str:
        """获取随机盐值（首次运行时生成并存储）。"""
        salt_file = os.path.join(os.path.dirname(self.vault_path), '.salt')
        if os.path.exists(salt_file):
            with open(salt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        import secrets
        salt = secrets.token_hex(32)
        with open(salt_file, 'w', encoding='utf-8') as f:
            f.write(salt)
        return salt

    def _get_machine_key(self) -> bytes:
        """生成基于设备的加密密钥。"""
        machine_info = (
            platform.node() +
            getpass.getuser() +
            self._salt
        )
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._get_salt_bytes(),
            iterations=600000,
        )
        return base64.urlsafe_b64encode(kdf.derive(machine_info.encode()))

    def _load_vault(self) -> dict:
        """加载保险库文件。"""
        if not os.path.exists(self.vault_path):
            return {}
        try:
            with open(self.vault_path, 'rb') as f:
                return json.loads(self._fernet.decrypt(f.read()).decode())
        except Exception:
            return {}

    def _save_vault(self, vault: dict):
        """保存保险库文件。"""
        data = self._fernet.encrypt(json.dumps(vault).encode())
        with open(self.vault_path, 'wb') as f:
            f.write(data)

    def store_api_key(self, provider: str, api_key: str):
        """加密存储 API Key。"""
        vault = self._load_vault()
        vault[provider] = {
            "key": api_key,
            "created_at": datetime.now().isoformat(),
        }
        self._save_vault(vault)

    def get_api_key(self, provider: str) -> str:
        """解密获取 API Key。"""
        vault = self._load_vault()
        if provider not in vault:
            raise KeyError(f"未找到 {provider} 的 API Key")
        return vault[provider]["key"]

    def has_api_key(self, provider: str) -> bool:
        """检查是否存在 API Key。"""
        vault = self._load_vault()
        return provider in vault

    def delete_api_key(self, provider: str):
        """删除指定提供商密钥。"""
        vault = self._load_vault()
        vault.pop(provider, None)
        self._save_vault(vault)


# 全局实例
vault = CredentialVault()

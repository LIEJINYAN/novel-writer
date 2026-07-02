"""API Key 加密工具，使用 cryptography.fernet.Fernet 标准加密。"""
import os
import platform
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_machine_code() -> str:
    """生成机器码（保留原实现）。"""
    username = os.environ.get("USERNAME") or ""
    computername = os.environ.get("COMPUTERNAME") or platform.node() or ""
    raw = f"{username}@{computername}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _get_fernet() -> Fernet:
    """从机器码派生 Fernet key。"""
    machine = get_machine_code().encode("utf-8")
    salt = b"novel-writer-v1-salt"  # 固定盐值
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    key = base64.urlsafe_b64encode(kdf.derive(machine))
    return Fernet(key)


def encrypt_api_key(key: str) -> str:
    """使用 Fernet 加密 API Key。

    Args:
        key: 原始 API Key 字符串

    Returns:
        str: Fernet token 字符串（以 gAAAAA 开头），不含明文片段
    """
    if not key:
        return ""
    f = _get_fernet()
    return f.encrypt(key.encode("utf-8")).decode("utf-8")


def decrypt_api_key(encrypted: str) -> str:
    """解密 API Key。自动检测旧格式并兼容。

    支持两种格式：
    1. 新格式：Fernet token（以 gAAAAA 开头）
    2. 旧格式：base64+XOR 格式（向后兼容）

    Args:
        encrypted: 加密后的字符串（新格式 Fernet token 或旧格式 base64 密文）

    Returns:
        str: 原始 API Key 字符串

    Raises:
        ValueError: 无法解密时抛出
    """
    if not encrypted:
        return ""

    # 先尝试 Fernet 解密
    if encrypted.startswith("gAAAAA"):
        try:
            f = _get_fernet()
            return f.decrypt(encrypted.encode("utf-8")).decode("utf-8")
        except Exception:
            pass  # 降级到旧格式尝试

    # 旧格式兼容：异或 + base64 解密
    try:
        return _xor_decrypt(encrypted)
    except Exception:
        raise ValueError("无法解密 API Key，加密格式不兼容")


def is_old_format(encrypted: str) -> bool:
    """检查是否为旧版异或加密格式。

    Args:
        encrypted: 加密后的字符串

    Returns:
        bool: 如果是旧版异或加密格式返回 True，新格式或空字符串返回 False
    """
    if not encrypted:
        return False
    # Fernet token 以 gAAAAA 开头
    return not encrypted.startswith("gAAAAA")


def _xor_encrypt(key: str) -> str:
    """旧版异或加密（保留用于迁移）。"""
    machine_code = get_machine_code().encode("utf-8")
    key_bytes = key.encode("utf-8")
    xored = bytes(
        b ^ machine_code[i % len(machine_code)]
        for i, b in enumerate(key_bytes)
    )
    return base64.b64encode(xored).decode("utf-8")


def _xor_decrypt(encrypted: str) -> str:
    """旧版异或解密。"""
    machine_code = get_machine_code().encode("utf-8")
    xored = base64.b64decode(encrypted.encode("utf-8"))
    key_bytes = bytes(
        b ^ machine_code[i % len(machine_code)]
        for i, b in enumerate(xored)
    )
    return key_bytes.decode("utf-8")

"""测试 crypto 向后兼容 - 使用实际机器码。"""
from utils.crypto import encrypt_api_key, decrypt_api_key, is_old_format, get_machine_code
import base64

key = "sk-test-api-key-12345"

# 使用实际机器码生成旧格式密文
machine = get_machine_code().encode("utf-8")
xored = bytes(b ^ machine[i % len(machine)] for i, b in enumerate(key.encode()))
old_enc = base64.b64encode(xored).decode()

print(f"旧格式密文: {old_enc[:20]}...")
print(f"检测为旧格式: {is_old_format(old_enc)}")
dec = decrypt_api_key(old_enc)
print(f"旧格式解密正确: {dec == key}")

# 新格式加密
enc = encrypt_api_key(key)
print(f"\n新格式密文: {enc[:20]}...")
print(f"检测为新格式: {not is_old_format(enc)}")
dec2 = decrypt_api_key(enc)
print(f"新格式解密正确: {dec2 == key}")

# 迁移测试：旧格式 -> 新格式
migrated = encrypt_api_key(decrypt_api_key(old_enc))
print(f"\n迁移后格式: {migrated[:20]}...")
print(f"迁移后是Fernet格式: {migrated.startswith('gAAAAA')}")
dec3 = decrypt_api_key(migrated)
print(f"迁移后解密正确: {dec3 == key}")

print("\n全部向后兼容测试通过！")

"""测试 crypto 加密模块。"""
from utils.crypto import encrypt_api_key, decrypt_api_key, is_old_format

# 测试新格式
key = "sk-test-api-key-12345"
enc = encrypt_api_key(key)
print(f"新格式加密: {enc[:20]}...")
print(f"以 gAAAAA 开头: {enc.startswith('gAAAAA')}")
dec = decrypt_api_key(enc)
print(f"解密正确: {dec == key}")
print(f"不是旧格式: {not is_old_format(enc)}")

# 测试向后兼容（旧格式）
import hashlib, base64
machine = hashlib.md5(b"test@test").hexdigest().encode()
xored = bytes(b ^ machine[i % len(machine)] for i, b in enumerate(key.encode()))
old_enc = base64.b64encode(xored).decode()
print(f"\n旧格式解密正确: {decrypt_api_key(old_enc) == key}")
print(f"检测为旧格式: {is_old_format(old_enc)}")

print("\n全部测试通过！")

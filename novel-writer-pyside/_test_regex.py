"""验证参数解析正则的正确性。"""
import re

pattern = r'(\w+)\s*=\s*"([^"]*)"|(\w+)\s*=\s*(\d+\.?\d*)|(\w+)\s*=\s*(true|false)|(\w+)\s*=\s*(\w+)'

cases = [
    'name="hello"',     # 字符串
    'count=42',          # 整数
    'ratio=3.14',        # 浮点
    'enabled=true',      # 布尔
    'disabled=false',    # 布尔
    'mode=simple',       # 无引号字符串
]

print("=== 验证从左到右的 | 分支优先级 ===")
for c in cases:
    pm = re.search(pattern, c)
    if pm.group(1):
        print(f"[BRANCH-1 字符串] {pm.group(1)} = '{pm.group(2)}'")
    elif pm.group(3):
        raw = pm.group(4)
        val = float(raw) if "." in raw else int(raw)
        print(f"[BRANCH-2 数字]   {pm.group(3)} = {val} ({type(val).__name__})")
    elif pm.group(5):
        val = pm.group(6).lower() == "true"
        print(f"[BRANCH-3 布尔]   {pm.group(5)} = {val} ({type(val).__name__})")
    elif pm.group(7):
        print(f"[BRANCH-4 通用]   {pm.group(7)} = '{pm.group(8)}'")
    else:
        print(f"[NO MATCH] {c}")

print()

# 验证歧义：检查 true/false/42 是否会被 BRANCH-4 错误捕获
ambiguous_cases = ['enabled=false', 'count=42', 'x=True']
print("=== 验证歧义（True 大小写） ===")
for c in ambiguous_cases:
    pm = re.search(pattern, c)
    if pm.group(5):
        val = pm.group(6).lower() == "true"
        print(f"[BRANCH-3 布尔]   {pm.group(5)} = {val}")
    elif pm.group(7):
        print(f"[BRANCH-4 通用]   {pm.group(7)} = '{pm.group(8)}'  ← 会被当作字符串!")
    else:
        print(f"[OTHER BRANCH] {c}")

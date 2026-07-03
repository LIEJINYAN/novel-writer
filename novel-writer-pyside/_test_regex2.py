"""验证 case-insensitive bool 匹配修复。"""
import re

bool_pattern = r'[Tt][Rr][Uu][Ee]|[Ff][Aa][Ll][Ss][Ee]'
pattern = rf'(\w+)\s*=\s*"([^"]*)"|(\w+)\s*=\s*(\d+\.?\d*)|(\w+)\s*=\s*({bool_pattern})|(\w+)\s*=\s*(\w+)'

cases = ['x=True', 'x=FALSE', 'x=true', 'x=False', 'x=42', 'x=3.14', 'x="hello"', 'x=abc']
all_ok = True
for c in cases:
    p = re.search(pattern, c)
    if p.group(1):
        label = f"string  {p.group(1)}='{p.group(2)}'"
    elif p.group(3):
        raw = p.group(4)
        val = float(raw) if "." in raw else int(raw)
        label = f"number  {p.group(3)}={val}"
    elif p.group(5):
        val = p.group(6).lower() == "true"
        label = f"bool    {p.group(5)}={val}"
    elif p.group(7):
        label = f"generic {p.group(7)}='{p.group(8)}'"
    else:
        label = "NO MATCH"
        all_ok = False
    print(f"  {c:15s} → {label}")

# 验证 True/FALSE 应该走 bool 而非 generic
for c in ['x=True', 'x=FALSE']:
    p = re.search(pattern, c)
    assert p.group(5) is not None, f"{c} 应该被 BRANCH-3 捕获！"

print("\nALL OK")

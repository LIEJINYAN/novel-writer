"""导入公共工具方法 — 分割逻辑、自然排序等。"""

import re


def split_full_book(file_path: str) -> list[dict]:
    """读取文件内容，按章节标记拆分为多个段落。

    优先尝试三种拆分模式：
    a. ``## 第X章`` / ``# 第X节`` 格式
    b. ``=== 第X章 ===`` 格式
    c. 三个以上换行符拆分（最后手段）

    返回::

        [{"title": "...", "content": "...", "word_count": N}, ...]
    """
    from pathlib import Path
    path = Path(file_path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 模式 a：Markdown 标题格式
    pattern_a = r"#{1,2}\s*第[一二三四五六七八九十百千万\d]+[章节]"
    matches_a = list(re.finditer(pattern_a, content, re.MULTILINE))
    if matches_a:
        return _build_segments(content, matches_a)

    # 模式 b：=== 格式
    pattern_b = r"===\s*第[\d]+章\s*==="
    matches_b = list(re.finditer(pattern_b, content, re.MULTILINE))
    if matches_b:
        return _build_segments(content, matches_b)

    # 模式 c：三个以上换行符
    parts = re.split(r"\n{3,}", content)
    segments = []
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        segments.append({
            "title": f"第{i + 1}章",
            "content": part,
            "word_count": sum(1 for c in part if not c.isspace()),
        })
    return segments


def _build_segments(content: str, matches: list) -> list[dict]:
    """根据正则匹配结果构建段落列表。

    自动清理导出残留的 HTML 标签（<div>、</div>、卷标等）。
    """
    segments = []

    for i, match in enumerate(matches):
        heading = match.group().strip()
        title = re.sub(r"^#+\s*", "", heading).strip()

        heading_end = match.end()
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[heading_end:next_start].strip()

        # 清理导出格式中残留的 HTML 标签
        body = re.sub(r'<div\b[^>]*>', '', body)
        body = re.sub(r'</div>', '', body)
        body = body.strip()

        segments.append({
            "title": title,
            "content": body,
            "word_count": sum(1 for c in body if not c.isspace()),
        })

    return segments


def split_text(content: str) -> list[dict]:
    """对纯文本内容（非文件）进行章节分割。

    适用于已经从 PDF/EPUB 等提取出的文本，逻辑同 split_full_book 的模式 a → b → c。
    """
    # 模式 a：Markdown 标题格式
    pattern_a = r"#{1,2}\s*第[一二三四五六七八九十百千万\d]+[章节]"
    matches_a = list(re.finditer(pattern_a, content, re.MULTILINE))
    if matches_a:
        return _build_segments(content, matches_a)

    # 模式 b：=== 格式
    pattern_b = r"===\s*第[\d]+章\s*==="
    matches_b = list(re.finditer(pattern_b, content, re.MULTILINE))
    if matches_b:
        return _build_segments(content, matches_b)

    # 模式 c：三个以上换行符
    parts = re.split(r"\n{3,}", content)
    segments = []
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        segments.append({
            "title": f"第{i + 1}章",
            "content": part,
            "word_count": sum(1 for c in part if not c.isspace()),
        })
    return segments


def natural_sort_key(s: str) -> list:
    """将字符串拆分为字母/数字块，用于自然排序。

    >>> natural_sort_key("10-chapter")
    [10, "-chapter"]
    >>> natural_sort_key("2-chapter")
    [2, "-chapter"]
    """
    parts = re.split(r"(\d+)", s)
    result = []
    for part in parts:
        if part.isdigit():
            result.append(int(part))
        else:
            result.append(part.lower())
    return result

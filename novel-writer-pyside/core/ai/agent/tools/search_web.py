"""联网搜索工具。"""
import requests
from core.ai.agent.tool_registry import Tool

definition = {
    "name": "search_web",
    "description": "联网搜索互联网信息，返回搜索结果标题、链接和摘要。当用户需要实时信息、设定参考或写作素材时使用",
    "category": "network",
    "icon": "🌐",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词"},
        },
        "required": ["query"],
    },
}


def search_web_handler(query: str, **kwargs) -> dict:
    """执行搜索。"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return {"success": False, "message": f"搜索失败: HTTP {resp.status_code}", "data": None}

        import re
        results = []
        for item in re.findall(
            r'<a rel="nofollow" href="(.*?)".*?class="result__a">(.*?)</a>.*?class="result__snippet">(.*?)</a>',
            resp.text,
            re.DOTALL,
        ):
            title = re.sub(r'<[^>]+>', "", item[1]).strip()
            snippet = re.sub(r'<[^>]+>', "", item[2]).strip()
            results.append({"title": title, "url": item[0], "snippet": snippet})
            if len(results) >= 5:
                break

        return {"success": True, "message": f"找到 {len(results)} 条结果", "data": results}
    except Exception as e:
        return {"success": False, "message": f"搜索出错: {e}", "data": None}


search_web_handler.definition = definition

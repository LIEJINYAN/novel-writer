"""HTML 预览工具。"""
import os
import tempfile
import webbrowser
from core.ai.agent.tool_registry import Tool

definition = {
    "name": "preview_html",
    "description": "将 HTML 内容在浏览器中预览。生成章节预览、格式化排版时使用",
    "category": "system",
    "icon": "👁️",
    "parameters": {
        "type": "object",
        "properties": {
            "html_content": {"type": "string", "description": "要预览的完整 HTML 内容"},
        },
        "required": ["html_content"],
    },
}


def preview_html_handler(html_content: str, **kwargs) -> dict:
    """预览 HTML。"""
    try:
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8")
        tmp.write(html_content)
        tmp.close()
        webbrowser.open(f"file://{tmp.name}")
        return {"success": True, "message": "已在浏览器打开预览", "data": {"file_path": tmp.name}}
    except Exception as e:
        return {"success": False, "message": f"预览失败: {e}", "data": None}


preview_html_handler.definition = definition

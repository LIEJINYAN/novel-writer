"""分析章节工具。"""

from core.ai.agent.tool_registry import Tool

definition = {
    "name": "analyze_chapter",
    "description": "对小说章节进行 AI 质量分析，返回情节/角色/文风的评分和改进建议",
    "category": "read",
    "icon": "📊",
    "parameters": {
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "章节全文"},
            "genre": {"type": "string", "description": "小说类型（如玄幻/都市/言情）", "default": ""},
        },
        "required": ["content"],
    },
}


def analyze_chapter_handler(content: str, genre: str = "", **kwargs) -> dict:
    """分析章节。"""
    try:
        from core.ai.analysis_service import analysis_service
        worker = analysis_service.analyze_chapter(content, genre)
        return {
            "success": True,
            "message": "已开始分析",
            "data": {"worker": worker, "content_preview": content[:100]},
        }
    except Exception as e:
        return {"success": False, "message": f"分析失败: {e}", "data": None}


analyze_chapter_handler.definition = definition

"""润色文本工具。"""

from core.ai.agent.tool_registry import Tool

definition = {
    "name": "polish_text",
    "description": "对指定文本进行 AI 润色（优化表达、修正语病），返回润色后文本",
    "category": "edit",
    "icon": "✨",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "要润色的原文"},
            "style": {"type": "string", "description": "润色风格（简洁/优美/正式/口语化）", "default": "简洁"},
        },
        "required": ["text"],
    },
}


def polish_text_handler(text: str, style: str = "简洁", **kwargs) -> dict:
    """润色文本。"""
    try:
        from core.ai.editing_service import editing_service
        worker = editing_service.polish(text, style)
        return {
            "success": True,
            "message": "已准备润色",
            "data": {"worker": worker, "original": text, "style": style},
        }
    except Exception as e:
        return {"success": False, "message": f"润色失败: {e}", "data": None}


polish_text_handler.definition = definition

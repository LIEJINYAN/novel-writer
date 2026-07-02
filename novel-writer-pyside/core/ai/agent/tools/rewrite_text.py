"""重写文本工具。"""

from core.ai.agent.tool_registry import Tool

definition = {
    "name": "rewrite_text",
    "description": "对指定文本进行 AI 重写（扩写/缩写/改视角/改人称），返回重写后文本",
    "category": "edit",
    "icon": "🔄",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "要重写的原文"},
            "direction": {"type": "string", "description": "改写方向（扩写/缩写/改视角/改人称）", "default": "扩写"},
        },
        "required": ["text"],
    },
}


def rewrite_text_handler(text: str, direction: str = "扩写", **kwargs) -> dict:
    """重写文本。"""
    try:
        from core.ai.editing_service import editing_service
        worker = editing_service.rewrite(text, direction)
        return {
            "success": True,
            "message": "已准备重写",
            "data": {"worker": worker, "original": text, "direction": direction},
        }
    except Exception as e:
        return {"success": False, "message": f"重写失败: {e}", "data": None}


rewrite_text_handler.definition = definition

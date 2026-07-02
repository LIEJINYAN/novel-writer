"""续写工具。"""

from core.ai.agent.tool_registry import Tool

definition = {
    "name": "continue_write",
    "description": "对指定章节进行 AI 续写，生成后续内容并写入编辑器",
    "category": "edit",
    "icon": "✍️",
    "parameters": {
        "type": "object",
        "properties": {
            "chapter_id": {"type": "integer", "description": "要续写的章节 ID"},
            "project_id": {"type": "integer", "description": "项目 ID"},
        },
        "required": ["chapter_id", "project_id"],
    },
}


def continue_write_handler(chapter_id: int, project_id: int, **kwargs) -> dict:
    """续写章节。"""
    try:
        from core.ai.writing_service import writing_service
        worker = writing_service.continue_write(chapter_id, project_id)
        # 注意：这里只触发续写，实际流式输出在 worker 中
        # 返回 worker 供 UI 层消费
        return {
            "success": True,
            "message": f"已开始续写章节 {chapter_id}",
            "data": {"worker": worker, "chapter_id": chapter_id},
        }
    except Exception as e:
        return {"success": False, "message": f"续写失败: {e}", "data": None}


continue_write_handler.definition = definition

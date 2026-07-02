"""读取章节工具。"""

from core.ai.agent.tool_registry import Tool

definition = {
    "name": "read_chapter",
    "description": "按章节 ID 读取小说章节的全文内容，返回章节标题和文本",
    "category": "read",
    "icon": "📖",
    "parameters": {
        "type": "object",
        "properties": {
            "chapter_id": {"type": "integer", "description": "章节 ID（数字）"},
        },
        "required": ["chapter_id"],
    },
}


def read_chapter_handler(chapter_id: int, **kwargs) -> dict:
    """读取章节内容。"""
    try:
        from models import db_manager, Chapter
        session = db_manager.get_session()
        try:
            chapter = session.query(Chapter).filter_by(id=chapter_id).first()
            if not chapter:
                return {"success": False, "message": f"章节 {chapter_id} 不存在", "data": None}
            return {
                "success": True,
                "message": f"已读取章节: {chapter.title}",
                "data": {
                    "id": chapter.id,
                    "title": chapter.title or "",
                    "content": chapter.content or "",
                    "word_count": chapter.word_count or 0,
                },
            }
        finally:
            session.close()
    except Exception as e:
        return {"success": False, "message": f"读取失败: {e}", "data": None}


read_chapter_handler.definition = definition

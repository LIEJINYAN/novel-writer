"""列出章节工具。"""
from core.ai.agent.tool_registry import Tool

definition = {
    "name": "list_chapters",
    "description": "列出指定项目下的所有章节，返回 ID、标题、字数和顺序号。在需要了解项目结构时使用",
    "category": "read",
    "icon": "📋",
    "parameters": {
        "type": "object",
        "properties": {
            "project_id": {"type": "integer", "description": "项目 ID"},
        },
        "required": ["project_id"],
    },
}


def list_chapters_handler(project_id: int, **kwargs) -> dict:
    """列出章节。"""
    try:
        from models import db_manager, Chapter
        session = db_manager.get_session()
        try:
            chapters = session.query(Chapter).filter_by(project_id=project_id).order_by(Chapter.order).all()
            data = [
                {"id": ch.id, "title": ch.title or "", "word_count": ch.word_count or 0, "order": ch.order or 0}
                for ch in chapters
            ]
            return {"success": True, "message": f"共 {len(data)} 章", "data": data}
        finally:
            session.close()
    except Exception as e:
        return {"success": False, "message": f"查询失败: {e}", "data": None}


list_chapters_handler.definition = definition

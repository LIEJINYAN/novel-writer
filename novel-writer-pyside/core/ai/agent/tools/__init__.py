"""Agent 工具实现。"""
from .read_chapter import read_chapter_handler
from .continue_write import continue_write_handler
from .polish_text import polish_text_handler
from .rewrite_text import rewrite_text_handler
from .analyze_chapter import analyze_chapter_handler
from .search_web import search_web_handler
from .list_chapters import list_chapters_handler
from .preview_html import preview_html_handler

__all__ = [
    "read_chapter_handler", "continue_write_handler",
    "polish_text_handler", "rewrite_text_handler",
    "analyze_chapter_handler",
    "search_web_handler", "list_chapters_handler", "preview_html_handler",
]

# 自动注册
_handlers = {
    "read_chapter": read_chapter_handler,
    "continue_write": continue_write_handler,
    "polish_text": polish_text_handler,
    "rewrite_text": rewrite_text_handler,
    "analyze_chapter": analyze_chapter_handler,
    "search_web": search_web_handler,
    "list_chapters": list_chapters_handler,
    "preview_html": preview_html_handler,
}


def register_all():
    """注册所有工具到全局 registry。"""
    from core.ai.agent.tool_registry import tool_registry, Tool
    for name, h in _handlers.items():
        tool_registry.register(Tool(handler=h, **h.definition))

"""全局信号总线 - 模块间通信。"""
from PySide6.QtCore import QObject, Signal

class SignalBus(QObject):
    """全局信号总线。"""
    
    # 项目信号
    project_opened = Signal(int)           # (project_id)
    project_closed = Signal()
    project_created = Signal(int)          # (project_id)
    
    # 章节信号
    chapter_created = Signal(int)          # (chapter_id)
    chapter_deleted = Signal(int)          # (chapter_id)
    chapter_saved = Signal(int)            # (chapter_id)
    chapter_switched = Signal(int)         # (chapter_id)
    content_changed = Signal(int)          # (chapter_id)
    
    # AI 信号
    ai_generation_started = Signal(str)    # (operation_type)
    ai_generation_finished = Signal(str)   # (operation_type)
    ai_chunk_received = Signal(str)        # (text_chunk)
    ai_error = Signal(str, str)            # (error_type, message)
    
    # 状态信号
    status_message = Signal(str)           # (message)
    word_count_updated = Signal(int)       # (total_count)
    theme_changed = Signal(str)            # (theme_name)
    
    # 面板信号
    sidebar_toggled = Signal(bool)         # (visible)


signal_bus = SignalBus()

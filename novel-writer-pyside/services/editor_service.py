"""编辑器服务 - 管理编辑器状态、自动保存、撤销重做配置。"""
from typing import Optional, Any
from PySide6.QtCore import QTimer, QObject, Signal
from services.app_config_service import app_config_service
from utils.logger import logger


class EditorService(QObject):
    """编辑器服务 - 管理编辑器状态、自动保存、撤销重做配置。"""

    chapter_saved = Signal(int)       # 章节保存后发射，参数为 chapter_id
    autosave_completed = Signal(int)  # 自动保存完成，参数为保存数量
    content_changed = Signal(int)          # 内容变更 (chapter_id)
    word_count_changed = Signal(int, int)  # 字数变更 (chapter_id, word_count)
    chapter_opened = Signal(int)           # 章节打开 (chapter_id)
    chapter_closed = Signal(int)           # 章节关闭 (chapter_id)

    def __init__(self, chapter_service, editor_tabs):
        super().__init__()
        self._chapter_service = chapter_service
        self._editor_tabs = editor_tabs  # QTabWidget 引用
        self._open_chapters: dict[int, tuple[int, Any]] = {}
        self._autosave_timer = QTimer()
        self._current_chapter_id: Optional[int] = None

        # 自动保存定时器
        self._autosave_timer.timeout.connect(self.autosave)

    # ========== 编辑器注册/反注册 ==========

    def register_editor(self, chapter_id: int, container, tab_index: int) -> None:
        """注册编辑器到追踪字典。"""
        self._open_chapters[chapter_id] = (tab_index, container)
        self.chapter_opened.emit(chapter_id)

    def unregister_editor(self, chapter_id: int) -> None:
        """取消注册编辑器。"""
        self._open_chapters.pop(chapter_id, None)
        self.chapter_closed.emit(chapter_id)

    def get_editor(self, chapter_id: int):
        """获取指定章节的编辑器控件。"""
        if chapter_id not in self._open_chapters:
            return None
        _, container = self._open_chapters[chapter_id]
        return container.editor if hasattr(container, 'editor') else container

    def get_current_editor(self):
        """获取当前标签页的编辑器。"""
        current_index = self._editor_tabs.currentIndex()
        if current_index < 0:
            return None
        for chapter_id, (tab_idx, container) in self._open_chapters.items():
            if tab_idx == current_index:
                return container.editor if hasattr(container, 'editor') else container
        return None

    def get_current_container(self):
        """获取当前标签页的容器。"""
        current_index = self._editor_tabs.currentIndex()
        if current_index < 0:
            return None
        for chapter_id, (tab_idx, container) in self._open_chapters.items():
            if tab_idx == current_index:
                return container
        return None

    def get_open_chapters(self) -> dict:
        """获取所有打开的章节映射（只读视图）。"""
        return self._open_chapters

    def is_open(self, chapter_id: int) -> bool:
        """检查章节是否已打开。"""
        return chapter_id in self._open_chapters

    def is_modified(self, chapter_id: int) -> bool:
        """检查章节是否有未保存的更改。"""
        if chapter_id not in self._open_chapters:
            return False
        _, container = self._open_chapters[chapter_id]
        editor = container.editor if hasattr(container, 'editor') else container
        return editor.is_modified()

    def get_tab_index(self, chapter_id: int) -> Optional[int]:
        """获取指定章节的标签页索引。"""
        if chapter_id not in self._open_chapters:
            return None
        return self._open_chapters[chapter_id][0]

    def update_tab_index(self, chapter_id: int, new_index: int) -> None:
        """更新标签页索引（标签页关闭后调整）。"""
        if chapter_id in self._open_chapters:
            container = self._open_chapters[chapter_id][1]
            self._open_chapters[chapter_id] = (new_index, container)

    # ========== 当前章节 ID 管理 ==========

    def set_current_chapter_id(self, chapter_id: Optional[int]) -> None:
        """设置当前章节 ID。"""
        self._current_chapter_id = chapter_id

    def get_current_chapter_id(self) -> Optional[int]:
        """获取当前章节 ID。"""
        return self._current_chapter_id

    # ========== 保存操作 ==========

    def save_chapter(self, chapter_id: int) -> bool:
        """保存指定章节。返回是否实际执行了保存。"""
        if chapter_id not in self._open_chapters:
            return False

        tab_index, container = self._open_chapters[chapter_id]
        editor = container.editor if hasattr(container, 'editor') else container

        if not editor.is_modified():
            return False

        content = editor.get_content()
        try:
            self._chapter_service.update_chapter_content(chapter_id, content)
            editor.set_modified(False)

            # 更新标签页标题（移除 * 标记）
            tab_text = self._editor_tabs.tabText(tab_index)
            if tab_text.endswith("*"):
                self._editor_tabs.setTabText(tab_index, tab_text[:-1])

            self.chapter_saved.emit(chapter_id)
            word_count = editor.count_words()
            self.content_changed.emit(chapter_id)
            self.word_count_changed.emit(chapter_id, word_count)
            return True
        except Exception as e:
            logger.error(f"保存章节失败: {e}")
            raise

    def save_current(self) -> bool:
        """保存当前章节。返回是否实际执行了保存。"""
        current_index = self._editor_tabs.currentIndex()
        if current_index < 0:
            return False

        for chapter_id, (tab_idx, _) in self._open_chapters.items():
            if tab_idx == current_index:
                return self.save_chapter(chapter_id)
        return False

    def save_all(self) -> int:
        """保存所有已修改的章节。返回保存数量。"""
        saved_count = 0
        for chapter_id in list(self._open_chapters.keys()):
            if self.is_modified(chapter_id):
                try:
                    if self.save_chapter(chapter_id):
                        saved_count += 1
                except Exception as e:
                    logger.error(f"保存章节 {chapter_id} 失败: {e}")
        return saved_count

    def autosave(self) -> None:
        """自动保存所有已修改的章节。"""
        saved_count = 0
        for chapter_id in list(self._open_chapters.keys()):
            _, container = self._open_chapters[chapter_id]
            editor = container.editor if hasattr(container, 'editor') else container
            if editor.is_modified():
                try:
                    self.save_chapter(chapter_id)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"自动保存章节 {chapter_id} 失败: {e}")

        if saved_count > 0:
            self.autosave_completed.emit(saved_count)

    # ========== 自动保存间隔 ==========

    def reload_autosave_interval(self) -> None:
        """从 app_config 表读取自动保存间隔并重启定时器。"""
        interval = app_config_service.get_int("auto_save_interval", 30)
        self._autosave_timer.setInterval(interval * 1000)
        self._autosave_timer.start()

    # ========== 撤销栈深度 ==========

    def apply_undo_depth(self, editor) -> None:
        """对单个编辑器应用撤销栈深度设置。"""
        depth = app_config_service.get_int("undo_stack_depth", 100)
        editor.document().setMaximumBlockCount(depth)

    def apply_undo_depth_to_all(self) -> None:
        """对所有打开的编辑器应用撤销栈深度设置。"""
        depth = app_config_service.get_int("undo_stack_depth", 100)
        for chapter_id, (_, container) in self._open_chapters.items():
            editor = container.editor if hasattr(container, 'editor') else container
            editor.document().setMaximumBlockCount(depth)

    # ========== 关闭操作 ==========

    def close_all_editors(self) -> list[int]:
        """清除所有编辑器追踪记录，返回已打开的章节 ID 列表。"""
        chapter_ids = list(self._open_chapters.keys())
        self._open_chapters.clear()
        return chapter_ids

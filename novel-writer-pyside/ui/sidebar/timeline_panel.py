"""时间线面板。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QMenu, QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
from services.timeline_service import timeline_service
from utils.signal_bus import signal_bus
from ui.dialogs.timeline_event_dialog import TimelineEventDialog


class TimelinePanel(QWidget):
    """侧边栏时间线事件列表。"""

    project_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("timeline_panel")
        self._project_id = None
        self._events: list[dict] = []
        self._init_ui()
        signal_bus.project_opened.connect(self._on_project_opened)
        signal_bus.project_closed.connect(self._on_project_closed)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        top_layout = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("搜索事件...")
        self._search_input.textChanged.connect(self._on_search)
        top_layout.addWidget(self._search_input)

        self._add_btn = QPushButton("+ 新建")
        self._add_btn.clicked.connect(self._on_add)
        top_layout.addWidget(self._add_btn)
        layout.addLayout(top_layout)

        self._event_list = QListWidget()
        self._event_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._event_list.customContextMenuRequested.connect(self._on_context_menu)
        self._event_list.itemDoubleClicked.connect(self._on_edit)
        self._event_list.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self._event_list)

    def _on_project_opened(self, project_id: int):
        """信号：项目打开。"""
        self._project_id = project_id
        self._load_events()

    def _on_project_closed(self):
        """信号：项目关闭。"""
        self._project_id = None
        self._event_list.clear()
        self._events = []

    def clear(self):
        """清空面板数据（兼容 main_window 直接调用）。"""
        self._project_id = None
        self._event_list.clear()
        self._events = []

    def _load_events(self, search: str = ""):
        """加载事件列表。"""
        self._event_list.clear()
        if not self._project_id:
            return
        self._events = timeline_service.list(self._project_id, search=search)

        # 重要性颜色
        colors = {
            "核心": QColor("#E74C3C"),  # 红
            "重要": QColor("#3498DB"),  # 蓝
            "次要": QColor("#95A5A6"),  # 灰
        }

        for ev in self._events:
            chapter_info = f" 第{ev['chapter_title']}" if ev["chapter_title"] else ""
            date_info = f" — {ev['story_date']}" if ev["story_date"] else ""
            display = f"{ev['event_name']}{chapter_info}{date_info}"

            item = QListWidgetItem(display)
            item.setData(256, ev["id"])

            color = colors.get(ev["importance"], QColor("#95A5A6"))
            dot = "●"
            item.setText(f"{dot} {display}")
            item.setForeground(color)

            self._event_list.addItem(item)

    def _on_search(self, text: str):
        """搜索事件。"""
        self._load_events(search=text.strip())

    def _on_add(self):
        """新建事件。"""
        if not self._project_id:
            return
        dialog = TimelineEventDialog(self._project_id, parent=self)
        if dialog.exec():
            self._load_events(search=self._search_input.text().strip())

    def _on_edit(self, item):
        """编辑事件。"""
        if not self._project_id:
            return
        event_id = item.data(256)
        dialog = TimelineEventDialog(self._project_id, event_id=event_id, parent=self)
        if dialog.exec():
            self._load_events(search=self._search_input.text().strip())

    def _on_context_menu(self, pos):
        """右键菜单。"""
        item = self._event_list.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        edit_action = menu.addAction("编辑")
        delete_action = menu.addAction("删除")

        # 多选时显示"批量删除"
        selected = self._event_list.selectedItems()
        if len(selected) > 1:
            batch_delete_action = menu.addAction(f"批量删除 ({len(selected)})")

        action = menu.exec(self._event_list.mapToGlobal(pos))

        if action == edit_action:
            self._on_edit(item)
        elif action == delete_action:
            self._delete_event(item)
        elif len(selected) > 1 and action == batch_delete_action:
            self._batch_delete(selected)

    def _delete_event(self, item):
        """删除事件。"""
        event_id = item.data(256)
        reply = QMessageBox.question(
            self, "确认删除", f"确定删除事件「{item.text()}」？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            timeline_service.delete(event_id)
            self._load_events(search=self._search_input.text().strip())

    def _batch_delete(self, items):
        """批量删除事件。"""
        reply = QMessageBox.question(
            self, "确认删除", f"确定删除 {len(items)} 个事件？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        ids = [item.data(256) for item in items]
        timeline_service.batch_delete(ids)
        self._load_events(search=self._search_input.text().strip())

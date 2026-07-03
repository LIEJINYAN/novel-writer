"""时间线面板。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QMenu, QMessageBox, QScrollArea, QToolTip,
)
from PySide6.QtCore import Qt, Signal, QRect, QPoint, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from services.timeline_service import timeline_service
from utils.signal_bus import signal_bus
from ui.dialogs.timeline_event_dialog import TimelineEventDialog


class TimelineWidget(QWidget):
    """水平时间轴视图。"""

    event_clicked = Signal(int)        # 单击节点
    event_double_clicked = Signal(int)  # 双击节点编辑
    event_context_menu = Signal(int, object)  # 右键菜单（event_id, global_pos）

    def __init__(self, parent=None):
        super().__init__(parent)
        self._events: list[dict] = []
        self.setMinimumHeight(200)

    def set_events(self, events: list[dict]):
        """设置事件数据并刷新绘制。"""
        self._events = events
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        # 水平轴线
        painter.setPen(QPen(QColor("#7c7cff"), 3))
        painter.drawLine(50, h // 2, w - 50, h // 2)

        if not self._events:
            painter.drawText(QRect(0, h // 2 - 20, w, 40), Qt.AlignCenter, "暂无时间线事件")
            painter.end()
            return

        # 计算间距
        spacing = max(100, (w - 100) // max(len(self._events), 1))
        start_x = 50

        for i, evt in enumerate(self._events):
            x = start_x + i * spacing
            name = evt.get('name', '') or evt.get('event_name', '') or f"事件{i + 1}"
            chapter = evt.get('chapter_id', '')

            # 节点圆圈
            painter.setBrush(QBrush(QColor("#7c7cff")))
            painter.setPen(QPen(QColor("#9c8cf0"), 2))
            painter.drawEllipse(QPoint(x, h // 2), 8, 8)

            # 标签（上方）
            painter.setPen(QColor("#e0e0e8"))
            painter.setFont(QFont("Microsoft YaHei", 9))
            painter.drawText(QRect(x - 60, h // 2 - 80, 120, 30), Qt.AlignCenter, name)

            # 章节信息（下方）
            if chapter:
                painter.setPen(QColor("#a0a0b8"))
                painter.setFont(QFont("Microsoft YaHei", 8))
                painter.drawText(QRect(x - 60, h // 2 + 16, 120, 20), Qt.AlignCenter, f"第{chapter}章")

    def _hit_test(self, pos_x: float) -> int:
        """返回点击位置对应的事件索引，未命中返回 -1。"""
        if not self._events:
            return -1
        w = self.width()
        spacing = max(100, (w - 100) // max(len(self._events), 1))
        h = self.height() // 2
        for i in range(len(self._events)):
            x = 50 + i * spacing
            if (pos_x - x) ** 2 + (self._last_mouse_y - h) ** 2 <= 100:
                return i
        return -1

    def mousePressEvent(self, event):
        """检测点击事件：左键显示提示，右键弹出菜单。"""
        self._last_mouse_y = event.position().y()
        idx = self._hit_test(event.position().x())
        if idx < 0 or idx >= len(self._events):
            super().mousePressEvent(event)
            return

        evt = self._events[idx]
        eid = evt.get('id')
        if event.button() == Qt.RightButton:
            self.event_context_menu.emit(eid, event.globalPosition().toPoint())
        elif event.button() == Qt.LeftButton:
            desc = evt.get('description', '') or '无详情'
            name = evt.get('name', '') or evt.get('event_name', '') or ''
            QToolTip.showText(event.globalPosition().toPoint(), f"{name}: {desc}")
            self.event_clicked.emit(eid)

    def mouseDoubleClickEvent(self, event):
        """双击编辑事件。"""
        idx = self._hit_test(event.position().x())
        if idx < 0 or idx >= len(self._events):
            super().mouseDoubleClickEvent(event)
            return
        eid = self._events[idx].get('id')
        self.event_double_clicked.emit(eid)


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

        # 水平时间轴
        self._timeline = TimelineWidget()
        self._timeline.event_clicked.connect(self._on_event_clicked)
        self._timeline.event_double_clicked.connect(self._on_event_double_clicked)
        self._timeline.event_context_menu.connect(self._on_event_context_menu)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._timeline)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(scroll)

    def _on_project_opened(self, project_id: int):
        """信号：项目打开。"""
        self._project_id = project_id
        self._load_events()

    def _on_project_closed(self):
        """信号：项目关闭。"""
        self._project_id = None
        self._timeline.set_events([])
        self._events = []

    def clear(self):
        """清空面板数据（兼容 main_window 直接调用）。"""
        self._project_id = None
        self._timeline.set_events([])
        self._events = []

    def _load_events(self, search: str = ""):
        """加载事件列表。"""
        if not self._project_id:
            self._timeline.set_events([])
            self._events = []
            return
        self._events = timeline_service.list(self._project_id, search=search)
        self._timeline.set_events(self._events)

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

    def _on_event_clicked(self, event_id: int):
        """单击事件节点（目前仅提示，可扩展为选中高亮）。"""
        pass

    def _on_event_double_clicked(self, event_id: int):
        """双击事件节点：打开编辑对话框。"""
        if not self._project_id:
            return
        dialog = TimelineEventDialog(self._project_id, event_id=event_id, parent=self)
        if dialog.exec():
            self._load_events(search=self._search_input.text().strip())

    def _on_event_context_menu(self, event_id: int, global_pos: QPoint):
        """右键事件节点：显示上下文菜单。"""
        menu = QMenu(self)
        edit_action = menu.addAction("编辑")
        delete_action = menu.addAction("删除")
        action = menu.exec(global_pos)

        if action == edit_action:
            dialog = TimelineEventDialog(self._project_id, event_id=event_id, parent=self)
            if dialog.exec():
                self._load_events(search=self._search_input.text().strip())
        elif action == delete_action:
            self._delete_event(event_id)

    def _delete_event(self, event_id: int):
        """删除事件。"""
        # 找到事件名称用于确认提示
        name = ""
        for ev in self._events:
            if ev.get('id') == event_id:
                name = ev.get('name', '') or ev.get('event_name', '') or ""
                break
        reply = QMessageBox.question(
            self, "确认删除", f"确定删除事件「{name}」？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            timeline_service.delete(event_id)
            self._load_events(search=self._search_input.text().strip())

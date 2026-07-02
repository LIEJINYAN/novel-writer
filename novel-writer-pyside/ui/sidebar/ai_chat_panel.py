"""AI 对话面板 - 侧边栏自由对话。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QTextEdit, QFrame, QSizePolicy, QApplication,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal, QTimer
from core.ai.base import Message, AIProviderError
from core.ai.chat_service import chat_service


class MessageBubble(QFrame):
    """单条消息气泡。"""

    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_bubble_user" if is_user else "chat_bubble_ai")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        self._label = QLabel(text)
        self._label.setWordWrap(True)
        self._label.setOpenExternalLinks(False)
        self._label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        layout.addWidget(self._label)

        # 用户消息右对齐，AI 消息左对齐
        if is_user:
            self._label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:
            self._label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)


class AIChatPanel(QWidget):
    """AI 对话面板。"""

    clear_requested = Signal()  # 清空对话

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ai_chat_panel")
        self._current_ai_bubble = None  # 当前正在生成的 AI 气泡
        self._session_id: str = ""  # 当前会话 ID
        self._stream_buffer: list[str] = []  # 流式缓冲区
        self._stream_gen = None
        self._stream_timer = None
        self._init_ui()
        # 自动创建第一个会话
        self._on_new_session()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 标题 + 会话切换
        title_layout = QHBoxLayout()
        title = QLabel("AI 对话")
        title.setObjectName("chat_panel_title")
        title_layout.addWidget(title)

        self._session_combo = QComboBox()
        self._session_combo.setObjectName("chat_session_combo")
        self._session_combo.setMinimumWidth(140)
        self._session_combo.currentIndexChanged.connect(self._on_session_switched)
        title_layout.addWidget(self._session_combo)
        layout.addLayout(title_layout)

        # 消息列表区域（滚动）
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setObjectName("chat_scroll")

        self._msg_container = QWidget()
        self._msg_container.setObjectName("chat_msg_container")
        self._msg_layout = QVBoxLayout(self._msg_container)
        self._msg_layout.setAlignment(Qt.AlignTop)
        self._msg_layout.setSpacing(8)
        self._msg_layout.addStretch()

        self._scroll.setWidget(self._msg_container)
        layout.addWidget(self._scroll, 1)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self._clear_btn = QPushButton("清空对话")
        self._clear_btn.setObjectName("chat_clear_btn")
        self._clear_btn.clicked.connect(self._on_clear)
        btn_layout.addWidget(self._clear_btn)

        self._new_session_btn = QPushButton("新建会话")
        self._new_session_btn.setObjectName("chat_new_session_btn")
        self._new_session_btn.clicked.connect(self._on_new_session)
        btn_layout.addWidget(self._new_session_btn)

        btn_layout.addStretch()

        self._copy_btn = QPushButton("复制全部")
        self._copy_btn.setObjectName("chat_copy_btn")
        self._copy_btn.clicked.connect(self._on_copy_all)
        btn_layout.addWidget(self._copy_btn)
        layout.addLayout(btn_layout)

        # 输入区域
        self._input = QTextEdit()
        self._input.setObjectName("chat_input")
        self._input.setPlaceholderText("输入消息...（Enter 发送，Shift+Enter 换行）")
        self._input.setMaximumHeight(80)
        self._input.setAcceptRichText(False)
        layout.addWidget(self._input)

        # 发送按钮
        send_layout = QHBoxLayout()
        self._send_btn = QPushButton("发送")
        self._send_btn.setObjectName("chat_send_btn")
        self._send_btn.clicked.connect(self._on_send)
        send_layout.addStretch()
        send_layout.addWidget(self._send_btn)
        layout.addLayout(send_layout)

    def _add_bubble(self, text: str, is_user: bool = False):
        """添加消息气泡。"""
        bubble = MessageBubble(text, is_user)
        # 插入到 stretch 之前
        self._msg_layout.insertWidget(self._msg_layout.count() - 1, bubble)
        # 自动滚动到底部
        QTimer.singleShot(50, self._scroll_to_bottom)
        return bubble

    def _scroll_to_bottom(self):
        scrollbar = self._scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_send(self):
        """发送消息。"""
        text = self._input.toPlainText().strip()
        if not text:
            return

        # 确保有会话
        if not self._session_id:
            self._session_id = chat_service.create_session()
            self._session_combo.addItem(f"会话 {self._session_combo.count() + 1}", self._session_id)
            self._session_combo.setCurrentIndex(self._session_combo.count() - 1)

        # 添加用户消息气泡
        self._add_bubble(text, is_user=True)
        self._input.clear()

        # 创建 AI 回复气泡（占位）
        self._current_ai_bubble = self._add_bubble("", is_user=False)

        # 调用 AI
        self._send_btn.setEnabled(False)
        self._send_btn.setText("生成中...")
        self._start_ai_chat(text)

    def _start_ai_chat(self, content: str = ""):
        """启动 AI 对话（使用 ChatService）。"""
        self._send_btn.setEnabled(False)
        self._send_btn.setText("生成中...")
        self._stream_buffer = []

        # 调用 ChatService 获取流式生成器
        self._stream_gen = chat_service.send_message(self._session_id, content)

        # 使用 QTimer 在事件循环中处理 Generator
        self._stream_timer = QTimer()
        self._stream_timer.timeout.connect(self._process_stream)
        self._stream_timer.start(50)

    def _process_stream(self):
        """处理流式输出。"""
        try:
            for _ in range(5):
                chunk = next(self._stream_gen)
                if chunk:
                    self._stream_buffer.append(chunk)
                    if self._current_ai_bubble:
                        current = self._current_ai_bubble._label.text()
                        self._current_ai_bubble._label.setText(current + chunk)
            self._scroll_to_bottom()
        except StopIteration:
            self._stream_timer.stop()
            self._current_ai_bubble = None
            self._reset_send_btn()
            # 更新 combo 显示（会话有消息了）
            self._update_session_label()
        except Exception as e:
            self._stream_timer.stop()
            self._update_current_bubble(f"\n[错误: {e}]")
            self._current_ai_bubble = None
            self._reset_send_btn()

    def _update_current_bubble(self, text: str):
        """更新当前 AI 气泡内容。"""
        if self._current_ai_bubble:
            current = self._current_ai_bubble._label.text()
            self._current_ai_bubble._label.setText(current + text)

    def _append_to_current_bubble(self, text: str):
        """追加到当前 AI 气泡。"""
        if self._current_ai_bubble:
            current = self._current_ai_bubble._label.text()
            self._current_ai_bubble._label.setText(current + text)

    def _reset_send_btn(self):
        self._send_btn.setEnabled(True)
        self._send_btn.setText("发送")

    def _on_clear(self):
        """清空当前会话。"""
        if self._session_id:
            chat_service.clear_history(self._session_id)
        # 移除所有气泡
        while self._msg_layout.count() > 1:
            item = self._msg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._current_ai_bubble = None
        self.clear_requested.emit()

    def _on_new_session(self):
        """新建会话。"""
        session_id = chat_service.create_session()
        label = f"会话 {self._session_combo.count() + 1}"
        self._session_combo.addItem(label, session_id)
        self._session_combo.setCurrentIndex(self._session_combo.count() - 1)

    def _on_session_switched(self, index: int):
        """切换会话。"""
        if index < 0:
            return
        session_id = self._session_combo.itemData(index)
        if not session_id or session_id == self._session_id:
            return

        # 清理旧会话的 UI
        while self._msg_layout.count() > 1:
            item = self._msg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._current_ai_bubble = None
        self._session_id = session_id

        # 加载新会话的历史消息
        self._load_session_history()

    def _load_session_history(self):
        """加载当前会话的历史消息到 UI。"""
        if not self._session_id:
            return
        history = chat_service.get_history(self._session_id)
        for msg in history:
            self._add_bubble(msg.content, is_user=(msg.role == "user"))

    def _update_session_label(self):
        """更新会话标签（标记有消息）。"""
        history = chat_service.get_history(self._session_id)
        msg_count = len(history)
        idx = self._session_combo.currentIndex()
        if idx >= 0 and msg_count > 0:
            current_text = self._session_combo.itemText(idx)
            base = current_text.split(" (")[0] if " (" in current_text else current_text
            self._session_combo.setItemText(idx, f"{base} ({msg_count//2}条)")

    def _on_copy_all(self):
        """复制全部对话。"""
        if not self._session_id:
            return
        history = chat_service.get_history(self._session_id)
        lines = []
        for msg in history:
            prefix = "你: " if msg.role == "user" else "AI: "
            lines.append(prefix + msg.content)
        text = "\n\n".join(lines)
        if text:
            QApplication.clipboard().setText(text)

    def keyPressEvent(self, event):
        """Enter 发送，Shift+Enter 换行。"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self._on_send()
        else:
            super().keyPressEvent(event)

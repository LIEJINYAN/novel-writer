"""底部 AI 对话浮动面板 - 简化版对话界面。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt, Signal, QTimer


class MessageBubble(QFrame):
    """单条消息气泡（复用简化版）。"""
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_bubble_user" if is_user else "chat_bubble_ai")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        self._label = QLabel(text)
        self._label.setWordWrap(True)
        self._label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self._label)


class AIChatWidget(QWidget):
    """底部 AI 对话面板组件。"""

    send_message = Signal(str)  # 用户发送消息

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        # 消息区
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setMinimumHeight(100)
        self._msg_container = QWidget()
        self._msg_layout = QVBoxLayout(self._msg_container)
        self._msg_layout.setAlignment(Qt.AlignTop)
        self._msg_layout.setSpacing(4)
        self._msg_layout.addStretch()
        self._scroll.setWidget(self._msg_container)
        layout.addWidget(self._scroll, 1)
        
        # 输入区
        input_layout = QHBoxLayout()
        self._input = QTextEdit()
        self._input.setPlaceholderText("输入消息...（Enter 发送）")
        self._input.setMaximumHeight(40)
        self._input.setAcceptRichText(False)
        input_layout.addWidget(self._input, 1)
        
        self._send_btn = QPushButton("发送")
        self._send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self._send_btn)
        layout.addLayout(input_layout)
    
    def _on_send(self):
        text = self._input.toPlainText().strip()
        if text:
            self.add_message(text, is_user=True)
            self.send_message.emit(text)
            self._input.clear()
    
    def add_message(self, text: str, is_user: bool = False):
        """添加消息气泡。"""
        bubble = MessageBubble(text, is_user)
        self._msg_layout.insertWidget(self._msg_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        scrollbar = self._scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def set_generating(self, generating: bool):
        self._send_btn.setEnabled(not generating)

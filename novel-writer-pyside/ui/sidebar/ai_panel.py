"""AI 面板 - Chat/Agent 双模式。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLabel, QPushButton,
    QFrame, QScrollArea, QTextEdit,
    QRadioButton,
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtWidgets import QSlider
from core.ai.base import Message


class StreamWorker(QThread):
    """流式工作线程 - 消费 Generator 并通过信号发送事件。"""

    chunk_received = Signal(str)
    tool_call_occurred = Signal(str, dict)
    tool_result_occurred = Signal(str, bool)
    finished = Signal()
    error = Signal(str)

    def __init__(self, generator, parent=None):
        super().__init__(parent)
        self._gen = generator
        self._cancelled = False

    def run(self):
        try:
            for event in self._gen:
                if self._cancelled:
                    return
                if event.event_type == "text" and event.data:
                    self.chunk_received.emit(event.data)
                elif event.event_type == "tool_call":
                    self.tool_call_occurred.emit(
                        event.data["name"], event.data.get("params", {})
                    )
                elif event.event_type == "tool_result":
                    self.tool_result_occurred.emit(
                        event.data["name"], event.data["success"]
                    )
                elif event.event_type == "error":
                    self.error.emit(str(event.data))
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        """停止生成。"""
        self._cancelled = True


class MessageBubble(QFrame):
    """单条消息气泡。"""

    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_bubble_user" if is_user else "chat_bubble_ai")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        self._label = QLabel(text)
        self._label.setWordWrap(True)
        self._label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        layout.addWidget(self._label)
        if is_user:
            self._label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:
            self._label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)


class AIPanel(QWidget):
    """AI 面板 - Chat/Agent 双模式。"""

    # 信号
    continue_write_requested = Signal(int)
    cancel_requested = Signal()
    settings_requested = Signal()
    provider_changed = Signal(str)
    polish_requested = Signal()
    rewrite_requested = Signal()
    analyze_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ai_panel")
        self._is_generating = False
        self._current_mode = "chat"  # "chat" | "agent"
        self._chat_history: list = []  # 对话历史
        # 流式状态
        self._current_ai_bubble = None
        self._stream_gen = None
        self._stream_worker = None
        self._init_ui()
        self.update_providers()
        # 自动创建对话会话移除，改用 AgentExecutor

    def _init_ui(self):
        """初始化 UI 布局。"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 标题行 + 模式切换
        title_layout = QHBoxLayout()
        title = QLabel("AI 助手")
        title.setObjectName("ai_panel_title")
        title_layout.addWidget(title)
        title_layout.addStretch()

        self._mode_chat = QRadioButton("Chat")
        self._mode_agent = QRadioButton("Agent")
        self._mode_chat.setChecked(True)
        self._mode_chat.toggled.connect(
            lambda checked: self._on_mode_changed("chat") if checked else None
        )
        self._mode_agent.toggled.connect(
            lambda checked: self._on_mode_changed("agent") if checked else None
        )

        # QSS 做成按钮样式
        _radio_style = """
            QRadioButton {
                padding: 4px 12px;
                border: 1px solid #3a3b5e;
                border-radius: 4px;
                background: #2a2b3e;
            }
            QRadioButton:checked {
                background: #4a6cf7;
                border-color: #4a6cf7;
                color: white;
            }
        """
        self._mode_chat.setStyleSheet(_radio_style)
        self._mode_agent.setStyleSheet(_radio_style)

        title_layout.addWidget(self._mode_chat)
        title_layout.addWidget(self._mode_agent)
        layout.addLayout(title_layout)

        # 模型选择行
        provider_layout = QHBoxLayout()
        provider_label = QLabel("模型:")
        self._provider_combo = QComboBox()
        self._provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self._provider_combo, 1)
        self._settings_btn = QPushButton("⚙")
        self._settings_btn.setFixedWidth(32)
        self._settings_btn.clicked.connect(self.settings_requested.emit)
        provider_layout.addWidget(self._settings_btn)
        layout.addLayout(provider_layout)

        # 对话消息区
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setObjectName("chat_scroll")

        self._msg_container = QWidget()
        self._msg_container.setObjectName("chat_msg_container")
        self._msg_layout = QVBoxLayout(self._msg_container)
        self._msg_layout.setAlignment(Qt.AlignTop)
        self._msg_layout.setSpacing(6)
        self._msg_layout.addStretch()

        self._scroll.setWidget(self._msg_container)
        layout.addWidget(self._scroll, 1)

        # 温度滑块（窄条）
        temp_row = QHBoxLayout()
        temp_row.setSpacing(4)
        temp_label = QLabel("温度")
        temp_label.setObjectName("ai_temp_label")
        temp_label.setFixedWidth(28)
        temp_label.setStyleSheet("font-size: 9px; color: #565f89;")
        temp_row.addWidget(temp_label)

        self._temp_slider = QSlider(Qt.Horizontal)
        self._temp_slider.setRange(0, 200)
        self._temp_slider.setValue(80)
        self._temp_slider.setMaximumHeight(14)
        self._temp_slider.valueChanged.connect(self._on_temp_changed)
        temp_row.addWidget(self._temp_slider, 1)

        self._temp_value_label = QLabel("0.8")
        self._temp_value_label.setFixedWidth(22)
        self._temp_value_label.setStyleSheet("font-size: 9px; color: #565f89;")
        temp_row.addWidget(self._temp_value_label)

        layout.addLayout(temp_row)

        # 续写操作行：续写按钮 + 字数选择
        continue_row = QHBoxLayout()
        continue_row.setSpacing(6)
        self._continue_btn = QPushButton("续写")
        self._continue_btn.setObjectName("ai_continue_btn")
        self._continue_btn.clicked.connect(self._on_continue_clicked)
        continue_row.addWidget(self._continue_btn)

        wc_label = QLabel("续写字数：")
        wc_label.setObjectName("ai_word_count_label")
        continue_row.addWidget(wc_label)

        self._word_count_combo = QComboBox()
        self._word_count_combo.setEditable(True)
        self._word_count_combo.addItems(["500", "1000", "1500", "2000"])
        self._word_count_combo.setCurrentText("2000")
        self._word_count_combo.setFixedWidth(100)
        continue_row.addWidget(self._word_count_combo)

        continue_row.addStretch()
        layout.addLayout(continue_row)

        # 输入行
        self._input = QTextEdit()
        self._input.setObjectName("chat_input")
        self._input.setPlaceholderText("输入消息...（Enter 发送，Shift+Enter 换行）")
        self._input.setMaximumHeight(50)
        self._input.setAcceptRichText(False)
        layout.addWidget(self._input)

        send_layout = QHBoxLayout()
        self._send_btn = QPushButton("发送")
        self._send_btn.setObjectName("chat_send_btn")
        self._send_btn.clicked.connect(self._on_send)
        send_layout.addStretch()
        send_layout.addWidget(self._send_btn)
        layout.addLayout(send_layout)

        # 状态指示
        self._status_indicator = QLabel("")
        self._status_indicator.setObjectName("ai_status_indicator")
        self._status_indicator.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_indicator)

    # ===== 模式切换 =====

    def _on_mode_changed(self, mode: str):
        if mode == self._current_mode:
            return
        # 停止正在进行的流式输出
        if self._stream_worker and self._stream_worker.isRunning():
            self._stream_worker.stop()
            self._stream_worker.wait(1000)
        self._current_ai_bubble = None
        self._stream_gen = None
        self._stream_worker = None

        self._current_mode = mode
        self._clear_bubbles()
        self.set_status("")
        # 切换输入框提示
        if mode == "agent":
            self._input.setPlaceholderText(
                "输入指令，如「帮我续写第三章」..."
            )
        else:
            self._input.setPlaceholderText(
                "输入消息...（Enter 发送，Shift+Enter 换行）"
            )

    # ===== 发送消息 =====

    def _on_send(self):
        text = self._input.toPlainText().strip()
        if not text:
            return

        self._add_bubble(text, is_user=True)
        self._input.clear()

        if self._current_mode == "chat":
            self._send_chat(text)
        else:
            self._send_agent(text)

    def _send_chat(self, text: str):
        """Chat 模式：使用 AgentExecutor（仅 read 工具）。"""
        from core.ai.agent.agent_executor import AgentExecutor
        from core.ai.manager import ai_manager

        try:
            config = ai_manager._create_config_from_active()
            provider = config.provider
            executor = AgentExecutor(provider, config)

            self._current_ai_bubble = self._add_bubble("", is_user=False)
            self._send_btn.setEnabled(False)

            gen = executor.execute(
                text, getattr(self, '_chat_history', None),
                tool_categories=["read"]
            )
            self._stream_gen = gen
            self._stream_worker = StreamWorker(gen)
            self._stream_worker.chunk_received.connect(self._on_stream_chunk)
            self._stream_worker.tool_call_occurred.connect(self._on_stream_tool_call)
            self._stream_worker.tool_result_occurred.connect(self._on_stream_tool_result)
            self._stream_worker.finished.connect(self._on_stream_finished)
            self._stream_worker.error.connect(self._on_stream_error)
            self._stream_worker.start()
        except Exception as e:
            if self._current_ai_bubble:
                self._current_ai_bubble._label.setText(f"[错误: {e}]")
            self._current_ai_bubble = None
            self._send_btn.setEnabled(True)

    def _send_agent(self, text: str):
        """Agent 模式：使用 AgentExecutor。"""
        from core.ai.agent.agent_executor import AgentExecutor
        from core.ai.manager import ai_manager

        try:
            provider = ai_manager.get_active_provider()
            config = ai_manager._create_config_from_active()
            if provider is None:
                raise RuntimeError("未配置 AI 提供商")

            executor = AgentExecutor(provider, config)

            # 记录用户消息到聊天历史
            self._chat_history.append(Message(role="user", content=text))
            if len(self._chat_history) > 40:
                self._chat_history = self._chat_history[-40:]

            self._current_ai_bubble = self._add_bubble("", is_user=False)
            self._send_btn.setEnabled(False)

            gen = executor.execute(
                text, self._chat_history if self._chat_history else None
            )
            self._stream_gen = gen
            self._stream_worker = StreamWorker(gen)
            self._stream_worker.chunk_received.connect(self._on_stream_chunk)
            self._stream_worker.tool_call_occurred.connect(self._on_stream_tool_call)
            self._stream_worker.tool_result_occurred.connect(self._on_stream_tool_result)
            self._stream_worker.finished.connect(self._on_stream_finished)
            self._stream_worker.error.connect(self._on_stream_error)
            self._stream_worker.start()
        except Exception as e:
            self._add_bubble(f"[错误: {e}]", is_user=False)
            self._send_btn.setEnabled(True)

    def _on_continue_clicked(self):
        """续写按钮点击处理。"""
        wc_text = self._word_count_combo.currentText().strip()
        try:
            word_count = int(wc_text)
        except ValueError:
            word_count = 2000
        self.continue_write_requested.emit(word_count)

    # ===== 流式输出回调 =====

    def _on_stream_chunk(self, chunk: str):
        """流式文本块处理。"""
        if self._current_ai_bubble:
            current = self._current_ai_bubble._label.text()
            self._current_ai_bubble._label.setText(current + chunk)
        self._scroll_to_bottom()

    def _on_stream_tool_call(self, name: str, params: dict):
        """工具调用事件处理。"""
        self._show_tool_card(name, params)

    def _on_stream_tool_result(self, name: str, success: bool):
        """工具结果事件处理。"""
        self._update_tool_card(name, success)

    def _on_stream_finished(self):
        """流式输出完成。"""
        if self._current_ai_bubble:
            full_text = self._current_ai_bubble._label.text()
            self._chat_history.append(
                Message(role="assistant", content=full_text)
            )
            if len(self._chat_history) > 40:
                self._chat_history = self._chat_history[-40:]
        self._current_ai_bubble = None
        self._send_btn.setEnabled(True)
        self._stream_worker = None

    def _on_stream_error(self, error_msg: str):
        """流式输出出错。"""
        if self._current_ai_bubble:
            current = self._current_ai_bubble._label.text()
            self._current_ai_bubble._label.setText(
                current + f"\n[错误: {error_msg}]"
            )
        self._current_ai_bubble = None
        self._send_btn.setEnabled(True)
        self._stream_worker = None

    # ===== 工具卡片 =====

    def _show_tool_card(self, tool_name: str, params: dict):
        """在消息区显示工具调用卡片。"""
        from core.ai.agent.tool_registry import tool_registry
        tool = tool_registry.get(tool_name)
        icon = tool.icon if tool else "🔧"

        card = QFrame()
        card.setObjectName("agent_tool_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 4, 8, 4)

        header = QLabel(f"{icon} {tool_name}")
        header.setObjectName("agent_tool_card_header")
        card_layout.addWidget(header)

        # 保存卡片引用用于更新状态
        card._status_label = QLabel("⏳ 执行中...")
        card._status_label.setObjectName("agent_tool_card_status")
        card_layout.addWidget(card._status_label)

        self._msg_layout.insertWidget(self._msg_layout.count() - 1, card)

    def _update_tool_card(self, tool_name: str, success: bool):
        """更新工具卡片状态。"""
        for i in range(self._msg_layout.count()):
            w = self._msg_layout.itemAt(i).widget()
            if w and isinstance(w, QFrame) and hasattr(w, '_status_label'):
                header = w.findChild(QLabel, "agent_tool_card_header")
                if header and tool_name in header.text():
                    status = "✅ 已完成" if success else "❌ 失败"
                    w._status_label.setText(status)
                    break

    # ===== 气泡管理 =====

    def _add_bubble(self, text: str, is_user: bool = False):
        bubble = MessageBubble(text, is_user)
        self._msg_layout.insertWidget(self._msg_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)
        return bubble

    def _clear_bubbles(self):
        """清空消息区所有气泡和工具卡片。"""
        while self._msg_layout.count() > 1:
            item = self._msg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._current_ai_bubble = None

    def _scroll_to_bottom(self):
        scrollbar = self._scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # ===== 公共方法（保留原签名） =====

    def update_providers(self):
        from core.ai.manager import ai_manager
        self._provider_combo.blockSignals(True)
        self._provider_combo.clear()
        providers = ai_manager.list_providers()
        active_index = -1
        combo_idx = 0
        for p in providers:
            if p["is_configured"]:
                active_mark = "★ " if p["is_active"] else ""
                label = f"{active_mark}{p['display_name']} - {p['model']}"
                self._provider_combo.addItem(label, p["name"])
                if p["is_active"]:
                    active_index = combo_idx
                combo_idx += 1
        if self._provider_combo.count() == 0:
            self._send_btn.setEnabled(False)
            self.set_status("请先配置 AI 提供商")
        else:
            self._send_btn.setEnabled(True)
            self.set_status("")
            if active_index >= 0:
                self._provider_combo.setCurrentIndex(active_index)
        self._provider_combo.blockSignals(False)

    def set_generating(self, is_generating: bool):
        self._is_generating = is_generating
        if not is_generating and self._stream_worker is not None:
            self._stream_worker.stop()

    def set_status(self, text: str):
        self._status_indicator.setText(text)

    def _on_temp_changed(self, value: int):
        temp = value / 100.0
        self._temp_value_label.setText(f"{temp:.1f}")

    def get_temperature(self) -> float:
        if hasattr(self, '_temp_slider'):
            return self._temp_slider.value() / 100.0
        return 0.8

    def get_selected_provider(self) -> str:
        return self._provider_combo.currentData() or ""

    def get_word_count(self) -> int:
        """获取当前选择的续写字数。"""
        wc_text = self._word_count_combo.currentText().strip()
        try:
            return int(wc_text)
        except ValueError:
            return 2000

    def add_system_message(self, text: str):
        """在对话区添加系统消息。"""
        self._add_bubble(text, is_user=False)

    def _on_provider_changed(self):
        data = self._provider_combo.currentData()
        if data:
            self.provider_changed.emit(data)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self._on_send()
        else:
            super().keyPressEvent(event)

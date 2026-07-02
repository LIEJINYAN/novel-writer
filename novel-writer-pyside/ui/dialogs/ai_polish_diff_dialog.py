"""AI 润色差分对比对话框。"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QPushButton, QLabel, QSplitter, QWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor, QColor, QTextCharFormat, QSyntaxHighlighter
import difflib


class DiffHighlighter(QSyntaxHighlighter):
    """差分高亮器 - 标记新增/删除/修改的文本。"""

    def __init__(self, parent, opcodes, text):
        super().__init__(parent)
        self._highlight_lines = {}
        self._process_opcodes(opcodes, text)

    def _process_opcodes(self, opcodes, text):
        lines = text.split('\n')
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                continue
            for line_idx in range(i1, i2):
                if line_idx < len(lines):
                    self._highlight_lines[line_idx] = tag

    def highlightBlock(self, text):
        block_number = self.currentBlock().blockNumber()
        tag = self._highlight_lines.get(block_number)
        if not tag:
            return

        fmt = QTextCharFormat()
        if tag == 'insert':
            fmt.setBackground(QColor('#e6ffed'))  # 浅绿
            fmt.setForeground(QColor('#22863a'))
        elif tag == 'delete':
            fmt.setBackground(QColor('#ffeef0'))  # 浅红
            fmt.setForeground(QColor('#cb2431'))
        elif tag == 'replace':
            fmt.setBackground(QColor('#fff8c5'))  # 浅黄
            fmt.setForeground(QColor('#b08800'))

        self.setFormat(0, len(text), fmt)


class AIPolishDiffDialog(QDialog):
    """润色差分对比对话框。"""

    apply_polish = Signal(str)  # 应用润色，传递润色后文本
    retry_polish = Signal()     # 重新润色

    def __init__(self, original_text: str, polished_text: str, parent=None):
        super().__init__(parent)
        self._original = original_text
        self._polished = polished_text
        self.setWindowTitle("AI 润色对比")
        self.setMinimumSize(800, 500)
        self._init_ui()
        self._show_diff()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 统计信息
        stats = self._compute_stats()
        self._stats_label = QLabel(stats)
        self._stats_label.setStyleSheet("font-size: 12px; color: #666; padding: 4px 0;")
        layout.addWidget(self._stats_label)

        # 左右分栏
        splitter = QSplitter(Qt.Horizontal)

        # 左栏：原文
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("原文"))
        self._original_edit = QPlainTextEdit()
        self._original_edit.setPlainText(self._original)
        self._original_edit.setReadOnly(True)
        left_layout.addWidget(self._original_edit)
        splitter.addWidget(left_widget)

        # 右栏：润色后
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(QLabel("润色后"))
        self._polished_edit = QPlainTextEdit()
        self._polished_edit.setPlainText(self._polished)
        self._polished_edit.setReadOnly(True)
        right_layout.addWidget(self._polished_edit)
        splitter.addWidget(right_widget)

        layout.addWidget(splitter, 1)

        # 底部按钮
        btn_layout = QHBoxLayout()
        self._apply_btn = QPushButton("✓ 应用润色")
        self._apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(self._apply_btn)

        self._retry_btn = QPushButton("↻ 重新润色")
        self._retry_btn.clicked.connect(self._on_retry)
        btn_layout.addWidget(self._retry_btn)

        btn_layout.addStretch()

        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self._cancel_btn)

        layout.addLayout(btn_layout)

    def _compute_stats(self) -> str:
        """计算修改统计。"""
        orig_lines = self._original.split('\n')
        polished_lines = self._polished.split('\n')
        matcher = difflib.SequenceMatcher(None, self._original, self._polished)

        changes = 0
        added = 0
        removed = 0
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue
            changes += 1
            if tag == 'insert':
                added += len(self._polished[j1:j2])
            elif tag == 'delete':
                removed += len(self._original[i1:i2])
            elif tag == 'replace':
                added += len(self._polished[j1:j2])
                removed += len(self._original[i1:i2])

        return (
            f"原文: {len(self._original)} 字 | "
            f"润色后: {len(self._polished)} 字 | "
            f"修改 {changes} 处 | "
            f"新增 {added} 字 / 删除 {removed} 字"
        )

    def _show_diff(self):
        """显示差分对比。"""
        matcher = difflib.SequenceMatcher(None, self._original, self._polished)
        opcodes = matcher.get_opcodes()

        # 为原文高亮删除/替换部分
        self._orig_highlighter = DiffHighlighter(
            self._original_edit.document(), opcodes, self._original
        )
        # 为润色后文本高亮新增/替换部分
        # 需要反转 opcodes
        reversed_opcodes = []
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                reversed_opcodes.append(('equal', j1, j2, i1, i2))
            elif tag == 'insert':
                reversed_opcodes.append(('delete', j1, j2, i1, i2))
            elif tag == 'delete':
                reversed_opcodes.append(('insert', j1, j2, i1, i2))
            elif tag == 'replace':
                reversed_opcodes.append(('replace', j1, j2, i1, i2))

        self._polished_highlighter = DiffHighlighter(
            self._polished_edit.document(), reversed_opcodes, self._polished
        )

    def _on_apply(self):
        """应用润色。"""
        self.apply_polish.emit(self._polished)
        self.accept()

    def _on_retry(self):
        """重新润色。"""
        self.retry_polish.emit()
        self.reject()

"""章节编辑器组件。"""
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import (
    QFont,
    QTextCursor,
    QTextBlockFormat,
    QTextOption,
    QPainter,
    QColor,
    QTextFormat,
)
from utils.signal_bus import signal_bus
from ui.styles.style_manager import style_manager

# 首行缩进：用两个全角空格模拟，因为 QPlainTextEdit 不渲染 setTextIndent
INDENT_STR = "\u3000\u3000"


class EditorWidget(QPlainTextEdit):
    content_changed = Signal()
    ai_continue_requested = Signal()  # 右键菜单 -> AI 续写
    ai_polish_requested = Signal()    # 右键菜单 -> AI 润色
    ai_rewrite_requested = Signal()   # 右键菜单 -> AI 重写
    ai_analyze_requested = Signal()   # 右键菜单 -> AI 分析

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("editor_widget")
        self._modified = False
        self._setting_content = False
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setInterval(200)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._on_debounce_timeout)
        self._init_ui()
        self._init_connections()

    def _init_ui(self):
        from PySide6.QtGui import QFontDatabase
        font_families = ["Source Han Serif SC", "Noto Serif CJK SC", "SimSun", "Songti SC"]
        available_families = QFontDatabase.families()
        family = "SimSun"
        for f in font_families:
            if f in available_families:
                family = f
                break
        font = QFont(family)
        font.setPointSize(15)
        self.setFont(font)

        self.document().setDefaultFont(font)

        option = QTextOption()
        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.document().setDefaultTextOption(option)

        self.setTabStopDistance(40)

        # 应用默认段落格式（行高等）
        self._apply_default_block_format()

        # 行号区域
        self._line_number_area = LineNumberArea(self)
        self._update_theme_colors()
        self.update_line_number_area_width()
        self.highlight_current_line()

    def _apply_default_block_format(self):
        """应用默认段落格式（行高、边距）。"""
        block_fmt = QTextBlockFormat()
        block_fmt.setLineHeight(180.0, 1)
        block_fmt.setLeftMargin(0)
        block_fmt.setRightMargin(0)

        doc = self.document()
        cursor = QTextCursor(doc)
        cursor.beginEditBlock()
        block = doc.begin()
        while block.isValid():
            QTextCursor(block).setBlockFormat(block_fmt)
            block = block.next()
        cursor.endEditBlock()
        cursor.movePosition(QTextCursor.Start)
        self.setTextCursor(cursor)

    def _init_connections(self):
        self.textChanged.connect(self._on_text_changed)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        signal_bus.theme_changed.connect(self._on_theme_changed)

    def _on_text_changed(self):
        if self._setting_content:
            return
        self._modified = True
        self._debounce_timer.start()

    def _on_debounce_timeout(self):
        self.content_changed.emit()

    # ---- 行号显示 ----

    def _update_theme_colors(self):
        """根据当前主题更新行号区域颜色。"""
        is_dark = style_manager.current_theme == "dark"
        if is_dark:
            self._ln_bg_color = "#2d2d2d"
            self._ln_text_color = "#999999"
            self._ln_current_line_color = "#3a3a3a"
        else:
            self._ln_bg_color = "#f0f0f0"
            self._ln_text_color = "#666666"
            self._ln_current_line_color = "#e8f0fe"

    def _on_theme_changed(self, theme: str):
        self._update_theme_colors()
        self._line_number_area.update()
        self.highlight_current_line()

    def line_number_area_width(self) -> int:
        """计算行号区域宽度。"""
        count = self.blockCount()
        digits = len(str(max(1, count)))
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def update_line_number_area_width(self):
        """更新编辑器左边距以容纳行号区域。"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """响应编辑器滚动/更新请求，同步更新行号区域。"""
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(
                0, rect.y(), self._line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def line_number_area_paint_event(self, event):
        """绘制行号区域。"""
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor(self._ln_bg_color))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(self._ln_text_color))
                painter.drawText(
                    0, top,
                    self._line_number_area.width(),
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        """高亮当前编辑行。"""
        if self.isReadOnly():
            return

        selection = QTextEdit.ExtraSelection()
        line_color = QColor(self._ln_current_line_color)
        selection.format.setBackground(line_color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    # ---- 缩进处理 ----

    @staticmethod
    def _add_indent(text: str) -> str:
        """为每个非空段落添加首行缩进。"""
        lines = text.split("\n")
        result = []
        for line in lines:
            if line.strip():
                result.append(INDENT_STR + line)
            else:
                result.append(line)
        return "\n".join(result)

    @staticmethod
    def _strip_indent(text: str) -> str:
        """移除段落开头的首行缩进字符。"""
        lines = text.split("\n")
        result = []
        for line in lines:
            result.append(line.lstrip("\u3000"))
        return "\n".join(result)

    def set_content(self, text: str):
        self._setting_content = True
        self.setPlainText(self._add_indent(text))
        self._apply_default_block_format()
        self._modified = False
        self.document().setModified(False)
        self._debounce_timer.stop()
        self._setting_content = False

    def get_content(self) -> str:
        return self._strip_indent(self.toPlainText())

    def count_words(self) -> int:
        text = self.toPlainText()
        # \u3000 全角空格 isspace() 返回 True，不计入字数
        return sum(1 for c in text if not c.isspace())

    def count_paragraphs(self) -> int:
        lines = self.toPlainText().split("\n")
        return sum(1 for line in lines if line.strip())

    def set_modified(self, modified: bool):
        self._modified = modified
        self.document().setModified(modified)

    def is_modified(self) -> bool:
        return self._modified

    def contextMenuEvent(self, event):
        """基于原生菜单的中文右键菜单。"""
        # 获取原生菜单（保留 OS 原生布局和样式）
        menu = self.createStandardContextMenu()

        # 翻译各菜单项文本
        translation = {
            "Undo": "撤销",
            "Redo": "重做",
            "Cut": "剪切",
            "Copy": "复制",
            "Paste": "粘贴",
            "Delete": "删除",
            "Select All": "全选",
        }
        for action in menu.actions():
            raw = action.text()
            text = raw.replace("&", "").split("\t")[0].strip()
            if not text:
                continue
            if text in translation:
                # 保留快捷键后缀
                suffix = raw.split("\t")[1] if "\t" in raw else ""
                action.setText(translation[text] + ("\t" + suffix if suffix else ""))

        # 追加 AI 功能
        has_sel = self.textCursor().hasSelection()
        menu.addSeparator()
        ai_act = menu.addAction("AI 续写")
        ai_act.triggered.connect(self.ai_continue_requested.emit)

        if has_sel:
            polish_act = menu.addAction("AI 润色")
            polish_act.triggered.connect(self.ai_polish_requested.emit)
            rewrite_act = menu.addAction("AI 重写")
            rewrite_act.triggered.connect(self.ai_rewrite_requested.emit)

        analyze_act = menu.addAction("AI 分析")
        analyze_act.triggered.connect(self.ai_analyze_requested.emit)

        menu.exec(event.globalPos())

    def keyPressEvent(self, event):
        """处理 Enter 键，自动为新段落添加首行缩进。"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            super().keyPressEvent(event)
            # Enter 后光标在新段落开头，插入缩进
            self._setting_content = True
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.insertText(INDENT_STR)
            self._setting_content = False
        else:
            super().keyPressEvent(event)


class LineNumberArea(QWidget):
    """行号显示区域。"""

    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._editor.line_number_area_paint_event(event)

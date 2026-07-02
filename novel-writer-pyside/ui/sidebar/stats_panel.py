"""统计面板组件 - 展示项目统计数据。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class StatsPanel(QWidget):
    """统计面板 - 展示项目统计数据。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("stats_panel")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_label = QLabel("统计")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        self.title_label.setObjectName("stats_title")
        self.title_label.setContentsMargins(16, 12, 16, 8)
        layout.addWidget(self.title_label)

        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(16, 8, 16, 16)
        content_layout.setSpacing(12)

        total_words_layout = QVBoxLayout()
        total_words_layout.setSpacing(4)
        total_words_label = QLabel("项目总字数")
        total_words_label.setStyleSheet("color: #666; font-size: 12px;")
        total_words_layout.addWidget(total_words_label)

        self.total_words_value = QLabel("0")
        total_words_font = QFont()
        total_words_font.setBold(True)
        total_words_font.setPointSize(24)
        self.total_words_value.setFont(total_words_font)
        self.total_words_value.setStyleSheet("color: #2c3e50;")
        total_words_layout.addWidget(self.total_words_value)

        content_layout.addLayout(total_words_layout)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("color: #e0e0e0;")
        content_layout.addWidget(line1)

        stats_grid = QVBoxLayout()
        stats_grid.setSpacing(8)

        chapter_row = QHBoxLayout()
        chapter_label = QLabel("章节总数")
        chapter_label.setStyleSheet("color: #666; font-size: 13px;")
        chapter_row.addWidget(chapter_label)
        chapter_row.addStretch()
        self.chapter_count_value = QLabel("0")
        self.chapter_count_value.setStyleSheet("color: #333; font-size: 13px; font-weight: bold;")
        chapter_row.addWidget(self.chapter_count_value)
        stats_grid.addLayout(chapter_row)

        volume_row = QHBoxLayout()
        volume_label = QLabel("分卷数")
        volume_label.setStyleSheet("color: #666; font-size: 13px;")
        volume_row.addWidget(volume_label)
        volume_row.addStretch()
        self.volume_count_value = QLabel("0")
        self.volume_count_value.setStyleSheet("color: #333; font-size: 13px; font-weight: bold;")
        volume_row.addWidget(self.volume_count_value)
        stats_grid.addLayout(volume_row)

        avg_row = QHBoxLayout()
        avg_label = QLabel("平均每章字数")
        avg_label.setStyleSheet("color: #666; font-size: 13px;")
        avg_row.addWidget(avg_label)
        avg_row.addStretch()
        self.avg_chars_value = QLabel("0")
        self.avg_chars_value.setStyleSheet("color: #333; font-size: 13px; font-weight: bold;")
        avg_row.addWidget(self.avg_chars_value)
        stats_grid.addLayout(avg_row)

        content_layout.addLayout(stats_grid)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("color: #e0e0e0;")
        content_layout.addWidget(line2)

        self.target_widget = QWidget()
        target_layout = QVBoxLayout(self.target_widget)
        target_layout.setContentsMargins(0, 0, 0, 0)
        target_layout.setSpacing(6)

        target_header = QHBoxLayout()
        target_label = QLabel("目标字数")
        target_label.setStyleSheet("color: #666; font-size: 13px;")
        target_header.addWidget(target_label)
        target_header.addStretch()
        self.target_percent_value = QLabel("0.0%")
        self.target_percent_value.setStyleSheet("color: #333; font-size: 13px; font-weight: bold;")
        target_header.addWidget(self.target_percent_value)
        target_layout.addLayout(target_header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("target_progress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        target_layout.addWidget(self.progress_bar)

        self.target_detail_label = QLabel("目标: 0字 / 已完成: 0.0%")
        self.target_detail_label.setStyleSheet("color: #888; font-size: 11px;")
        self.target_detail_label.setAlignment(Qt.AlignCenter)
        target_layout.addWidget(self.target_detail_label)

        content_layout.addWidget(self.target_widget)

        content_layout.addStretch()

        layout.addWidget(self.content_widget)

        self.empty_label = QLabel("暂无数据")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #999; font-size: 14px;")
        self.empty_label.setContentsMargins(16, 40, 16, 40)
        self.empty_label.hide()
        layout.addWidget(self.empty_label)

    def _format_number(self, number: int) -> str:
        return f"{number:,}"

    def update_stats(self, stats: dict):
        total_words = stats.get("total_words", 0)
        chapter_count = stats.get("chapter_count", 0)
        volume_count = stats.get("volume_count", 0)
        avg_chars_per_chapter = stats.get("avg_chars_per_chapter", 0)
        target_words = stats.get("target_words")

        self.total_words_value.setText(self._format_number(total_words))
        self.chapter_count_value.setText(self._format_number(chapter_count))
        self.volume_count_value.setText(self._format_number(volume_count))
        self.avg_chars_value.setText(self._format_number(avg_chars_per_chapter))

        if target_words and target_words > 0:
            self.target_widget.show()
            percent = (total_words / target_words) * 100
            percent = min(percent, 100.0)
            self.progress_bar.setValue(int(percent))
            self.target_percent_value.setText(f"{percent:.1f}%")
            self.target_detail_label.setText(
                f"目标: {self._format_number(target_words)}字 / 已完成: {percent:.1f}%"
            )
        else:
            self.target_widget.hide()

        self.content_widget.show()
        self.empty_label.hide()

    def clear(self):
        self.total_words_value.setText("0")
        self.chapter_count_value.setText("0")
        self.volume_count_value.setText("0")
        self.avg_chars_value.setText("0")
        self.progress_bar.setValue(0)
        self.target_percent_value.setText("0.0%")
        self.target_detail_label.setText("目标: 0字 / 已完成: 0.0%")
        self.content_widget.hide()
        self.empty_label.show()

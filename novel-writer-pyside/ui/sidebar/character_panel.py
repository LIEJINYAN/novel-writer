"""角色面板组件 - 管理小说角色列表。"""
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QComboBox,
    QMenu, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from services.character_service import character_service
from services.chapter_service import ChapterService
from utils.signal_bus import signal_bus


class CharacterItemWidget(QWidget):
    """角色列表项组件。"""

    def __init__(self, character, parent=None):
        super().__init__(parent)
        self._character = character
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        self.setMinimumHeight(50)

        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: #e8e8e8;
                border-radius: 16px;
                font-size: 16px;
                text-align: center;
                line-height: 32px;
                color: #555;
                font-weight: bold;
            }
        """)
        icon_label.setText(self._character.name[0] if self._character.name else "?")
        layout.addWidget(icon_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(self._character.name)
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(12)
        name_label.setFont(name_font)
        name_label.setObjectName("character_name")
        info_layout.addWidget(name_label)

        sub_info_layout = QHBoxLayout()
        sub_info_layout.setSpacing(8)

        role_label = QLabel(self._character.role or "未设定")
        role_label.setObjectName("character_role")
        role_label.setStyleSheet("font-size: 11px; color: #666;")
        sub_info_layout.addWidget(role_label)

        info_layout.addLayout(sub_info_layout)

        layout.addLayout(info_layout, 1)

        appearance_count = len(self._character.appearances)
        count_label = QLabel(f"{appearance_count}章")
        count_label.setObjectName("character_appearance_count")
        count_label.setStyleSheet("font-size: 11px; color: #aaa; padding: 2px 6px;")
        count_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(count_label)

    @property
    def character(self):
        return self._character


class CharacterPanel(QWidget):
    """角色面板 - 侧边栏角色管理标签页。"""

    character_selected = Signal(int)
    character_created = Signal(int)
    character_deleted = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("character_panel")
        self._project_id = None
        self._chapter_service = ChapterService()
        self._selected_character = None
        self._updating_appearances = False
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title_widget = QWidget()
        title_widget.setObjectName("character_header")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(16, 12, 16, 8)
        title_layout.setSpacing(2)

        self.title_label = QLabel("角色")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        self.title_label.setObjectName("character_title")
        title_layout.addWidget(self.title_label)

        layout.addWidget(title_widget)

        filter_widget = QWidget()
        filter_widget.setObjectName("character_filter")
        filter_layout = QVBoxLayout(filter_widget)
        filter_layout.setContentsMargins(16, 0, 16, 8)
        filter_layout.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索角色名称/别名...")
        self.search_input.setObjectName("character_search")
        filter_layout.addWidget(self.search_input)

        row_layout = QHBoxLayout()
        row_layout.setSpacing(8)

        self.role_combo = QComboBox()
        self.role_combo.addItem("全部类型")
        self.role_combo.addItem("主角")
        self.role_combo.addItem("配角")
        self.role_combo.addItem("反派")
        self.role_combo.setObjectName("character_role_combo")
        row_layout.addWidget(self.role_combo, 1)

        self.status_combo = QComboBox()
        self.status_combo.addItem("全部状态")
        self.status_combo.addItem("活跃")
        self.status_combo.addItem("已故")
        self.status_combo.addItem("失踪")
        self.status_combo.setObjectName("character_status_combo")
        row_layout.addWidget(self.status_combo, 1)

        filter_layout.addLayout(row_layout)

        layout.addWidget(filter_widget)

        action_widget = QWidget()
        action_widget.setObjectName("character_action")
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(16, 0, 16, 8)
        action_layout.setSpacing(8)

        self.add_btn = QPushButton("新建角色")
        self.add_btn.setObjectName("character_add_btn")
        action_layout.addWidget(self.add_btn)

        layout.addWidget(action_widget)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("character_list")
        self.list_widget.setSpacing(4)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        layout.addWidget(self.list_widget, 1)

        self.empty_label = QLabel("暂无角色\n点击「新建角色」创建")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #999; font-size: 13px;")
        self.empty_label.setContentsMargins(16, 40, 16, 40)
        self.empty_label.hide()
        layout.addWidget(self.empty_label)

        # ---- 出场记录详情区域 ----
        self._detail_widget = QWidget()
        self._detail_widget.setObjectName("character_detail")
        self._detail_widget.hide()
        detail_layout = QVBoxLayout(self._detail_widget)
        detail_layout.setContentsMargins(16, 4, 16, 8)
        detail_layout.setSpacing(4)

        freq_header_layout = QHBoxLayout()
        self._appearance_header = QLabel("出场记录")
        self._appearance_header.setStyleSheet("font-weight: bold; font-size: 12px;")
        freq_header_layout.addWidget(self._appearance_header)

        self._appearance_freq = QLabel("")
        self._appearance_freq.setStyleSheet("font-size: 11px; color: #888;")
        self._appearance_freq.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        freq_header_layout.addWidget(self._appearance_freq, 1)
        detail_layout.addLayout(freq_header_layout)

        self._appearance_list = QListWidget()
        self._appearance_list.setSelectionMode(QListWidget.NoSelection)
        detail_layout.addWidget(self._appearance_list)

        layout.addWidget(self._detail_widget)

    def _connect_signals(self):
        self.search_input.textChanged.connect(self._on_filter_changed)
        self.role_combo.currentTextChanged.connect(self._on_filter_changed)
        self.status_combo.currentTextChanged.connect(self._on_filter_changed)
        self.add_btn.clicked.connect(self._on_add_character)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.customContextMenuRequested.connect(self._on_context_menu)
        self._appearance_list.itemChanged.connect(self._on_appearance_toggled)

        signal_bus.project_opened.connect(self._on_project_opened)
        signal_bus.project_closed.connect(self._on_project_closed)

    def _on_project_opened(self, project_id: int):
        self._project_id = project_id
        self._refresh_list()

    def _on_project_closed(self):
        self._project_id = None
        self._clear_list()
        self.empty_label.show()

    def _on_filter_changed(self):
        self._refresh_list()

    def _on_add_character(self):
        if not self._project_id:
            return
        from ui.dialogs.character_dialog import CharacterDialog
        dialog = CharacterDialog(self._project_id, parent=self)
        if dialog.exec():
            character = dialog.get_character()
            if character:
                self.character_created.emit(character.id)
                self._refresh_list()

    def _on_item_double_clicked(self, item):
        widget = self.list_widget.itemWidget(item)
        if widget and hasattr(widget, 'character'):
            self._edit_character(widget.character)

    def _on_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return

        widget = self.list_widget.itemWidget(item)
        if not widget or not hasattr(widget, 'character'):
            return

        character = widget.character

        menu = QMenu(self)

        edit_action = menu.addAction("编辑")
        edit_action.triggered.connect(lambda: self._edit_character(character))

        menu.addSeparator()

        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(lambda: self._delete_character(character))

        menu.exec(self.list_widget.viewport().mapToGlobal(pos))

    def _edit_character(self, character):
        from ui.dialogs.character_dialog import CharacterDialog
        dialog = CharacterDialog(self._project_id, character.id, parent=self)
        if dialog.exec():
            self._refresh_list()

    def _delete_character(self, character):
        reply = QMessageBox.warning(
            self, "确认删除",
            f"确定要删除角色「{character.name}」吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        if character_service.delete(character.id):
            self.character_deleted.emit(character.id)
            self._refresh_list()

    def _refresh_list(self):
        if not self._project_id:
            return

        search = self.search_input.text().strip()
        role_type = self.role_combo.currentText()

        if role_type == "全部类型":
            role_type = ""

        characters = character_service.list(self._project_id, search, role_type)

        self._clear_list()

        if not characters:
            self.empty_label.show()
            return

        self.empty_label.hide()

        for char in characters:
            item = QListWidgetItem(self.list_widget)
            widget = CharacterItemWidget(char)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.setItemWidget(item, widget)

    def _clear_list(self):
        self.list_widget.clear()
        self._hide_detail()

    def _hide_detail(self):
        """隐藏出场记录详情区域。"""
        self._selected_character = None
        self._detail_widget.hide()
        self._appearance_list.clear()

    def _on_item_clicked(self, item):
        """单击角色列表项，显示出场记录。"""
        widget = self.list_widget.itemWidget(item)
        if widget and hasattr(widget, 'character'):
            self._selected_character = widget.character
            self._refresh_appearances()

    def _refresh_appearances(self):
        """刷新出场记录列表（所有章节 + 勾选状态）。"""
        if not self._project_id or not self._selected_character:
            self._hide_detail()
            return

        # 获取所有章节和已有的出场记录
        chapters = self._chapter_service.list_chapters(self._project_id)
        appearances = character_service.get_appearances(self._selected_character.id)
        appeared_chapter_ids = {a["chapter_id"] for a in appearances}

        self._detail_widget.show()
        self._appearance_list.clear()

        # 更新频率统计
        total = len(chapters)
        appeared = len(appearances)
        if total == 0:
            self._appearance_freq.setText("暂无章节")
            return

        self._appearance_freq.setText(f"第 {appeared} 章出场 · 共 {total} 章")

        # 填充所有章节的勾选列表
        self._updating_appearances = True
        try:
            for ch in chapters:
                title = ch.title or f"第 {ch.chapter_number} 章"
                label = f"第{ch.chapter_number}章 {title}"
                item = QListWidgetItem(label)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setData(Qt.UserRole, ch.id)  # 存 chapter_id
                if ch.id in appeared_chapter_ids:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
                self._appearance_list.addItem(item)
        finally:
            self._updating_appearances = False

    def _on_appearance_toggled(self, item):
        """勾选状态变更时持久化出场记录。"""
        if self._updating_appearances or not self._selected_character:
            return

        chapter_id = item.data(Qt.UserRole)
        if chapter_id is None:
            return

        char_id = self._selected_character.id
        checked = item.checkState() == Qt.Checked

        if checked:
            character_service.add_appearance(char_id, chapter_id)
        else:
            character_service.remove_appearance(char_id, chapter_id)

        # 更新频率统计
        appearances = character_service.get_appearances(char_id)
        total = self._appearance_list.count()
        self._appearance_freq.setText(
            f"第 {len(appearances)} 章出场 · 共 {total} 章"
        )

    def clear(self):
        self._project_id = None
        self._clear_list()
        self.empty_label.show()

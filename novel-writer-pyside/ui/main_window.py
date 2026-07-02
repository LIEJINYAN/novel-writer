"""Novel Writer 主窗口。"""
import os
import sys
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QTextEdit, QDockWidget, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QStatusBar, QToolBar, QTabWidget, QSplitter,
    QMessageBox, QApplication, QMenu, QMenuBar,
    QFileDialog, QListWidget, QDialog, QPushButton,
    QInputDialog, QAbstractItemView, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, QSettings, QAbstractItemModel
from PySide6.QtGui import QAction, QKeySequence, QShortcut, QTextCursor, QTextCharFormat, QColor, QBrush

from ui.styles.style_manager import style_manager
from ui.dialogs.new_project_dialog import NewProjectDialog
from ui.dialogs.ai_settings_dialog import AISettingsDialog
from ui.components.editor_widget import EditorWidget
from ui.components.search_panel import SearchPanel
from ui.sidebar.outline_panel import OutlinePanel
from ui.sidebar.stats_panel import StatsPanel
from ui.sidebar.ai_panel import AIPanel
from ui.sidebar.character_panel import CharacterPanel
from ui.sidebar.plot_panel import PlotPanel
from core.ai.editing_service import editing_service
from core.ai.analysis_service import analysis_service
from ui.dialogs.ai_polish_diff_dialog import AIPolishDiffDialog
from utils.signal_bus import signal_bus
from utils.logger import logger
from services.project_service import ProjectService
from services.chapter_service import ChapterService
from core.ai.manager import ai_manager
from core.ai.writing_service import writing_service
from core.ai.base import AIProviderError
from models import db_manager, Project, Volume, Chapter


class ProjectTreeWidget(QTreeWidget):
    """项目树组件 - 限制拖拽层级：章节只能挂在分卷下，不能成为其他章节的子节点。"""

    def dropEvent(self, event):
        """重写拖放事件，检查目标位置是否合法。"""
        dragged = self.currentItem()
        if not dragged:
            event.ignore()
            return

        dragged_data = dragged.data(0, Qt.UserRole)
        if not dragged_data:
            # 项目根节点，不允许移动
            event.ignore()
            return

        item_type = dragged_data[0] if isinstance(dragged_data, tuple) else None
        target = self.itemAt(event.pos())
        indicator = self.dropIndicatorPosition()

        if not target:
            # 拖到空白区域
            if item_type == "volume":
                # 分卷只能拖到根级别
                super().dropEvent(event)
            else:
                event.ignore()
            return

        target_data = target.data(0, Qt.UserRole)
        target_type = target_data[0] if isinstance(target_data, tuple) else None

        if item_type == "chapter":
            # 章节不能拖到根节点上成为子节点
            if target_type is None:
                event.ignore()
                return
            # 章节拖到章节上 (OnItem) -> 不允许，防止成为子节点
            if target_type == "chapter" and indicator == QAbstractItemView.OnItem:
                event.ignore()
                return
            # 章节拖到分卷上 (OnItem) -> 允许，成为该分卷的子节点
            # 章节拖到章节上方/下方 (Above/Below) -> 允许，作为兄弟节点

        elif item_type == "volume":
            # 分卷不能成为任何节点的子节点
            if indicator == QAbstractItemView.OnItem:
                event.ignore()
                return
            # 分卷只能在根级别移动
            if target_type is not None:
                event.ignore()
                return

        super().dropEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._project_service = ProjectService()
        self._chapter_service = ChapterService()
        self._current_project_id = None
        self._current_chapter_id = None
        self._open_chapters = {}
        self._autosave_timer = QTimer()
        self._stats_debounce_timer = QTimer()
        self._stats_debounce_timer.setSingleShot(True)
        self._stats_debounce_timer.timeout.connect(self._refresh_stats)
        self._current_matches = []
        self._current_match_index = -1
        self._current_search_keyword = ""
        self._tree_reorder_pending = False
        self._order_snapshot = None
        # AI 相关
        self._ai_panel = None
        self._ai_worker = None
        self._ai_target_chapter_id = None  # AI 生成目标章节，切换标签页时不变
        self._init_window()
        self._init_menu()
        self._init_toolbar()
        self._init_central_widget()
        self._init_docks()
        self._init_statusbar()
        self._init_connections()
        self._init_ai()

        logger.info("主窗口初始化完成")

    def _init_window(self):
        self.setWindowTitle("Novel Writer")
        self.resize(1400, 900)
        self.setMinimumSize(1000, 600)

    def _init_menu(self):
        menubar = self.menuBar()

        # ========== 文件菜单 ==========
        file_menu = menubar.addMenu("文件(&F)")

        new_action = QAction("新建项目(&N)", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_action)

        open_action = QAction("打开项目(&O)", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_project)
        file_menu.addAction(open_action)

        # 最近项目子菜单
        self._recent_menu = file_menu.addMenu("最近项目")
        self._update_recent_menu()

        file_menu.addSeparator()

        self._save_action = QAction("保存(&S)", self)
        self._save_action.setShortcut("Ctrl+S")
        file_menu.addAction(self._save_action)

        file_menu.addSeparator()

        close_action = QAction("关闭项目", self)
        close_action.triggered.connect(self._on_close_project)
        file_menu.addAction(close_action)

        delete_action = QAction("删除项目", self)
        delete_action.triggered.connect(self._on_delete_project)
        file_menu.addAction(delete_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&Q)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ========== 编辑菜单 ==========
        self._edit_menu = menubar.addMenu("编辑(&E)")

        # ========== 视图菜单 ==========
        view_menu = menubar.addMenu("视图(&V)")

        theme_menu = view_menu.addMenu("主题")
        dark_action = QAction("暗色", self)
        dark_action.triggered.connect(lambda: self._switch_theme("dark"))
        theme_menu.addAction(dark_action)

        light_action = QAction("亮色", self)
        light_action.triggered.connect(lambda: self._switch_theme("light"))
        theme_menu.addAction(light_action)

        # ========== 项目菜单 ==========
        project_menu = menubar.addMenu("项目(&P)")

        open_folder_action = QAction("在资源管理器中显示", self)
        open_folder_action.triggered.connect(self._on_open_project_folder)
        project_menu.addAction(open_folder_action)

        project_menu.addSeparator()

        proj_close_action = QAction("关闭项目", self)
        proj_close_action.triggered.connect(self._on_close_project)
        project_menu.addAction(proj_close_action)

        proj_delete_action = QAction("删除项目", self)
        proj_delete_action.triggered.connect(self._on_delete_project)
        project_menu.addAction(proj_delete_action)

        # ========== 工具菜单 ==========
        tool_menu = menubar.addMenu("工具(&T)")

        ai_settings_action = QAction("AI 设置...", self)
        ai_settings_action.triggered.connect(self._on_ai_settings)
        tool_menu.addAction(ai_settings_action)

        # ========== 帮助菜单 ==========
        help_menu = menubar.addMenu("帮助(&H)")
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _init_toolbar(self):
        toolbar = QToolBar("主工具栏", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        new_btn = toolbar.addAction("新建")
        new_btn.triggered.connect(self._on_new_project)

        open_btn = toolbar.addAction("打开")
        open_btn.triggered.connect(self._on_open_project)

    def _init_central_widget(self):
        central_container = QWidget()
        central_container.setObjectName("central_container")
        layout = QVBoxLayout(central_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._search_panel = SearchPanel()
        self._search_panel.setVisible(False)
        layout.addWidget(self._search_panel, 0)

        self._editor_tabs = QTabWidget()
        self._editor_tabs.setObjectName("editor_tabs")
        self._editor_tabs.setTabsClosable(True)
        self._editor_tabs.tabCloseRequested.connect(self._close_editor_tab)
        self._editor_tabs.setMovable(True)
        layout.addWidget(self._editor_tabs, 1)

        self.setCentralWidget(central_container)

        self._show_welcome_page()

    def _show_welcome_page(self):
        """显示欢迎页。"""
        self._editor_tabs.clear()
        welcome = QTextEdit()
        welcome.setObjectName("welcome_page")
        welcome.setHtml("<h1 style='text-align:center;color:#565f89;margin-top:200px;'>"
                       "欢迎使用 Novel Writer<br><br>"
                       "<span style='font-size:14px;color:#565f89;'>"
                       "文件 → 新建项目 开始创作</span></h1>")
        welcome.setReadOnly(True)
        self._editor_tabs.addTab(welcome, "欢迎")

    def _init_docks(self):
        # 左侧：项目树
        self._project_dock = QDockWidget("项目", self)
        self._project_dock.setObjectName("project_dock")
        self._project_tree = ProjectTreeWidget()
        self._project_tree.setHeaderHidden(True)
        self._project_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._project_tree.customContextMenuRequested.connect(self._on_tree_context_menu)
        self._project_tree.setDragEnabled(True)
        self._project_tree.setAcceptDrops(True)
        self._project_tree.setDropIndicatorShown(True)
        self._project_tree.setDragDropMode(QTreeWidget.InternalMove)
        self._project_tree.setSelectionMode(QTreeWidget.SingleSelection)
        self._project_tree.model().rowsMoved.connect(self._on_tree_rows_moved)
        self._project_dock.setWidget(self._project_tree)
        self._project_dock.setMinimumWidth(200)
        self.addDockWidget(Qt.LeftDockWidgetArea, self._project_dock)

        # 右侧：侧边栏
        self._sidebar_dock = QDockWidget("侧边栏", self)
        self._sidebar_dock.setObjectName("sidebar_dock")
        self._sidebar_tabs = QTabWidget()
        self._sidebar_tabs.setObjectName("sidebar_tabs")

        self._outline_panel = OutlinePanel()
        self._sidebar_tabs.addTab(self._outline_panel, "大纲")

        self._stats_panel = StatsPanel()
        self._sidebar_tabs.addTab(self._stats_panel, "统计")

        # AI 面板
        self._ai_panel = AIPanel()
        self._sidebar_tabs.addTab(self._ai_panel, "AI")

        # 角色面板
        self._character_panel = CharacterPanel()
        self._sidebar_tabs.addTab(self._character_panel, "角色")

        # 情节面板
        self._plot_panel = PlotPanel()
        self._sidebar_tabs.addTab(self._plot_panel, "情节")

        self._sidebar_dock.setWidget(self._sidebar_tabs)
        self._sidebar_dock.setMinimumWidth(250)
        self.addDockWidget(Qt.RightDockWidgetArea, self._sidebar_dock)

    def _init_statusbar(self):
        self._status_label = QLabel("就绪")
        self.statusBar().addWidget(self._status_label)

        self._word_count_label = QLabel("字数：0")
        self.statusBar().addPermanentWidget(self._word_count_label)

    def _init_connections(self):
        signal_bus.status_message.connect(self._on_status_message)
        signal_bus.project_opened.connect(self._on_project_opened)
        signal_bus.word_count_updated.connect(self._on_word_count_updated)
        self._project_tree.itemClicked.connect(self._on_tree_item_clicked)
        self._editor_tabs.currentChanged.connect(self._on_tab_changed)
        self._save_action.triggered.connect(self._on_save_current)
        self._autosave_timer.timeout.connect(self._on_autosave)
        self._reload_autosave_interval()

        self._search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self._search_shortcut.activated.connect(self._toggle_search_panel)
        self._search_panel.search_text_changed.connect(self._on_search_text_changed)
        self._search_panel.search_next.connect(self._on_search_next)
        self._search_panel.search_prev.connect(self._on_search_prev)
        self._search_panel.replace.connect(self._on_replace)
        self._search_panel.replace_all.connect(self._on_replace_all)
        self._search_panel.close_panel.connect(self._on_close_search_panel)

        # AI 面板信号
        if self._ai_panel is not None:
            self._ai_panel.continue_write_requested.connect(self._on_ai_continue_write)
            self._ai_panel.cancel_requested.connect(self._on_ai_cancel)
            self._ai_panel.settings_requested.connect(self._on_ai_settings)
            self._ai_panel.provider_changed.connect(self._on_ai_provider_changed)
            self._ai_panel.polish_requested.connect(self._on_ai_polish)
            self._ai_panel.rewrite_requested.connect(self._on_ai_rewrite)
            self._ai_panel.analyze_requested.connect(self._on_ai_analyze)

        # AI 续写快捷键 Ctrl+I
        self._ai_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        self._ai_shortcut.activated.connect(self._on_ai_continue_write)

        # AI 快捷键
        QShortcut(QKeySequence("Ctrl+Shift+P"), self, self._ai_panel.polish_requested.emit)
        QShortcut(QKeySequence("Ctrl+Shift+R"), self, self._ai_panel.rewrite_requested.emit)
        QShortcut(QKeySequence("Ctrl+Shift+A"), self, self._ai_panel.analyze_requested.emit)

        # 大纲面板 - 点击章节范围跳转
        self._outline_panel.navigate_to_chapter.connect(self._open_chapter_editor)

        # 编辑菜单 - AI 操作
        self._edit_menu.addSeparator()
        self._edit_menu.addAction("润色选中文本 (Ctrl+Shift+P)", self._ai_panel.polish_requested.emit, QKeySequence("Ctrl+Shift+P"))
        self._edit_menu.addAction("重写选中文本 (Ctrl+Shift+R)", self._ai_panel.rewrite_requested.emit, QKeySequence("Ctrl+Shift+R"))
        self._edit_menu.addAction("分析当前章节 (Ctrl+Shift+A)", self._ai_panel.analyze_requested.emit, QKeySequence("Ctrl+Shift+A"))

    def _init_ai(self):
        """初始化 AI 管理器并刷新面板。"""
        try:
            ai_manager.init()
        except Exception as e:
            logger.error(f"AI 管理器初始化失败: {e}")
        # 刷新 AI 面板的提供商列表
        if self._ai_panel is not None:
            self._ai_panel.update_providers()

    def _on_ai_provider_changed(self, provider_name: str):
        """AI 面板切换提供商。"""
        from core.ai.manager import ai_manager

        try:
            ai_manager.set_active_provider(provider_name)
            logger.info(f"切换 AI 提供商: {provider_name}")
            if self._ai_panel is not None:
                self._ai_panel.update_providers()
        except Exception as e:
            logger.error(f"切换提供商失败: {e}")

    # ========== 项目操作 ==========

    def _on_new_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec():
            info = dialog.get_project_info()
            try:
                project = self._project_service.create_project(info)
                self._current_project_id = project.id
                signal_bus.project_created.emit(project.id)
                signal_bus.status_message.emit(f"项目'{project.name}'创建成功")
                self._load_project_tree(project.id)
            except Exception as e:
                logger.error(f"创建项目失败: {e}")
                QMessageBox.critical(self, "错误", f"创建项目失败：{str(e)}")

    def _on_open_project(self):
        """打开项目对话框。"""
        recent_projects = self._get_recent_projects()

        if recent_projects:
            dialog = QDialog(self)
            dialog.setWindowTitle("打开项目")
            dialog.setMinimumWidth(400)
            layout = QVBoxLayout(dialog)

            layout.addWidget(QLabel("最近打开的项目："))
            list_widget = QListWidget()
            for name, path in recent_projects:
                list_widget.addItem(f"{name}  ({path})")
            list_widget.setCurrentRow(0)
            layout.addWidget(list_widget)

            btn_open = QPushButton("打开选定项目")
            btn_open.clicked.connect(dialog.accept)
            layout.addWidget(btn_open)

            btn_browse = QPushButton("浏览其他项目...")
            btn_browse.clicked.connect(lambda: self._browse_project(dialog))
            layout.addWidget(btn_browse)

            if dialog.exec():
                row = list_widget.currentRow()
                if row >= 0:
                    name, path = recent_projects[row]
                    self._open_project_by_path(path)
        else:
            self._browse_project()

    def _on_close_project(self):
        """关闭当前项目。"""
        if self._current_project_id is None:
            signal_bus.status_message.emit("当前没有打开的项目")
            return

        for chapter_id in list(self._open_chapters.keys()):
            self._save_chapter(chapter_id)

        self._open_chapters.clear()
        self._current_project_id = None
        self._project_tree.clear()
        self._editor_tabs.clear()
        self._word_count_label.setText("字数：0 | 段落：0")
        self._outline_panel.clear()
        self._stats_panel.clear()
        self._character_panel.clear()
        self._plot_panel.clear()
        self._show_welcome_page()
        signal_bus.project_closed.emit()
        signal_bus.status_message.emit("项目已关闭")

    def _on_delete_project(self):
        """删除（归档）当前项目。"""
        if self._current_project_id is None:
            signal_bus.status_message.emit("当前没有打开的项目")
            return

        session = db_manager.get_session()
        try:
            project = session.query(Project).filter_by(id=self._current_project_id).first()
            if not project:
                return

            reply = QMessageBox.warning(
                self, "确认删除",
                f"确定要归档项目「{project.name}」吗？\n\n"
                "项目将被标记为已归档，数据不会立即删除。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._project_service.delete_project(self._current_project_id)
                self._on_close_project()
                signal_bus.status_message.emit(f"项目已归档: {project.name}")
        finally:
            session.close()

    def _on_open_project_folder(self):
        """在文件资源管理器中打开项目目录。"""
        if self._current_project_id is None:
            signal_bus.status_message.emit("当前没有打开的项目")
            return

        session = db_manager.get_session()
        try:
            project = session.query(Project).filter_by(id=self._current_project_id).first()
            if project and project.path:
                path = project.path
                if os.path.exists(path):
                    if sys.platform == "win32":
                        os.startfile(path)
                    elif sys.platform == "darwin":
                        subprocess.run(["open", path])
                    else:
                        subprocess.run(["xdg-open", path])
                    signal_bus.status_message.emit(f"已打开: {path}")
                else:
                    QMessageBox.warning(self, "路径不存在", f"项目路径不存在：\n{path}")
        finally:
            session.close()

    def _on_tree_context_menu(self, pos):
        """项目树右键菜单。"""
        item = self._project_tree.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        data = item.data(0, Qt.UserRole)

        # 根节点（项目）
        if isinstance(data, int):
            open_folder_action = menu.addAction("在资源管理器中显示")
            open_folder_action.triggered.connect(self._on_open_project_folder)
            menu.addSeparator()
            close_action = menu.addAction("关闭项目")
            close_action.triggered.connect(self._on_close_project)
            delete_action = menu.addAction("删除项目")
            delete_action.triggered.connect(self._on_delete_project)
            menu.addSeparator()
            new_volume_action = menu.addAction("新建分卷...")
            new_volume_action.triggered.connect(self._on_new_volume)

        # 分卷节点
        elif isinstance(data, tuple) and data[0] == "volume":
            volume_id = data[1]
            new_chapter_action = menu.addAction("新建章节...")
            new_chapter_action.triggered.connect(lambda: self._on_new_chapter(volume_id))
            menu.addSeparator()
            rename_volume_action = menu.addAction("重命名分卷...")
            rename_volume_action.triggered.connect(lambda: self._on_rename_volume(volume_id))
            delete_volume_action = menu.addAction("删除分卷...")
            delete_volume_action.triggered.connect(lambda: self._on_delete_volume(volume_id))

        # 章节节点
        elif isinstance(data, tuple) and data[0] == "chapter":
            chapter_id = data[1]
            rename_chapter_action = menu.addAction("重命名章节...")
            rename_chapter_action.triggered.connect(lambda: self._on_rename_chapter(chapter_id))
            delete_chapter_action = menu.addAction("删除章节...")
            delete_chapter_action.triggered.connect(lambda: self._on_delete_chapter(chapter_id))

        menu.exec(self._project_tree.viewport().mapToGlobal(pos))

    # ========== 分卷操作 ==========

    def _on_new_volume(self):
        """新建分卷。"""
        if self._current_project_id is None:
            return

        name, ok = QInputDialog.getText(self, "新建分卷", "请输入分卷名称：")
        if not ok or not name.strip():
            return

        name = name.strip()
        try:
            self._chapter_service.create_volume(self._current_project_id, name)
            self._load_project_tree(self._current_project_id)
            signal_bus.status_message.emit(f"分卷'{name}'创建成功")
        except Exception as e:
            logger.error(f"创建分卷失败: {e}")
            QMessageBox.critical(self, "错误", f"创建分卷失败：{str(e)}")

    def _on_rename_volume(self, volume_id: int):
        """重命名分卷。"""
        try:
            volume = self._chapter_service.get_volume(volume_id)
            if not volume:
                return

            new_name, ok = QInputDialog.getText(
                self, "重命名分卷", "请输入新的分卷名称：", text=volume.name
            )
            if not ok or not new_name.strip():
                return

            new_name = new_name.strip()
            self._chapter_service.rename_volume(volume_id, new_name)
            self._load_project_tree(self._current_project_id)

            for chapter_id, (tab_idx, _) in list(self._open_chapters.items()):
                chapter = self._chapter_service.get_chapter(chapter_id)
                if chapter and chapter.volume_id == volume_id:
                    tab_title = f"第{chapter.chapter_number}章 {chapter.title}"
                    self._editor_tabs.setTabText(tab_idx, tab_title)

            signal_bus.status_message.emit(f"分卷已重命名为'{new_name}'")
        except Exception as e:
            logger.error(f"重命名分卷失败: {e}")
            QMessageBox.critical(self, "错误", f"重命名分卷失败：{str(e)}")

    def _on_delete_volume(self, volume_id: int):
        """删除分卷。"""
        try:
            volume = self._chapter_service.get_volume(volume_id)
            if not volume:
                return

            reply = QMessageBox.warning(
                self, "确认删除",
                f"确定要删除分卷「{volume.name}」吗？\n\n"
                "该分卷下的所有章节将被一并删除，此操作不可撤销。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

            chapters_to_close = []
            for chapter_id, (_, _) in list(self._open_chapters.items()):
                chapter = self._chapter_service.get_chapter(chapter_id)
                if chapter and chapter.volume_id == volume_id:
                    chapters_to_close.append(chapter_id)

            for chapter_id in chapters_to_close:
                self._close_chapter_tab(chapter_id)

            self._chapter_service.delete_volume(volume_id)
            self._load_project_tree(self._current_project_id)
            signal_bus.status_message.emit(f"分卷已删除: {volume.name}")
        except Exception as e:
            logger.error(f"删除分卷失败: {e}")
            QMessageBox.critical(self, "错误", f"删除分卷失败：{str(e)}")

    # ========== 章节操作 ==========

    def _on_new_chapter(self, volume_id: int):
        """新建章节。"""
        title, ok = QInputDialog.getText(self, "新建章节", "请输入章节标题：")
        if not ok or not title.strip():
            return

        title = title.strip()
        try:
            new_chapter = self._chapter_service.create_chapter(volume_id, title)
            self._load_project_tree(self._current_project_id)
            self._open_chapter_editor(new_chapter.id)
            signal_bus.status_message.emit(f"章节'{title}'创建成功")
        except Exception as e:
            logger.error(f"创建章节失败: {e}")
            QMessageBox.critical(self, "错误", f"创建章节失败：{str(e)}")

    def _on_rename_chapter(self, chapter_id: int):
        """重命名章节。"""
        try:
            chapter = self._chapter_service.get_chapter(chapter_id)
            if not chapter:
                return

            new_title, ok = QInputDialog.getText(
                self, "重命名章节", "请输入新的章节标题：", text=chapter.title
            )
            if not ok or not new_title.strip():
                return

            new_title = new_title.strip()
            self._chapter_service.rename_chapter(chapter_id, new_title)
            self._load_project_tree(self._current_project_id)

            if chapter_id in self._open_chapters:
                tab_idx, _ = self._open_chapters[chapter_id]
                updated_chapter = self._chapter_service.get_chapter(chapter_id)
                if updated_chapter:
                    tab_title = f"第{updated_chapter.chapter_number}章 {updated_chapter.title}"
                    self._editor_tabs.setTabText(tab_idx, tab_title)

            signal_bus.status_message.emit(f"章节已重命名为'{new_title}'")
        except Exception as e:
            logger.error(f"重命名章节失败: {e}")
            QMessageBox.critical(self, "错误", f"重命名章节失败：{str(e)}")

    def _on_delete_chapter(self, chapter_id: int):
        """删除章节。"""
        try:
            chapter = self._chapter_service.get_chapter(chapter_id)
            if not chapter:
                return

            reply = QMessageBox.warning(
                self, "确认删除",
                f"确定要删除章节「第{chapter.chapter_number}章 {chapter.title}」吗？\n\n"
                "此操作不可撤销。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

            if chapter_id in self._open_chapters:
                self._close_chapter_tab(chapter_id)

            self._chapter_service.delete_chapter(chapter_id)
            self._load_project_tree(self._current_project_id)
            signal_bus.status_message.emit(f"章节已删除: {chapter.title}")
        except Exception as e:
            logger.error(f"删除章节失败: {e}")
            QMessageBox.critical(self, "错误", f"删除章节失败：{str(e)}")

    # ========== 辅助方法 ==========

    def _close_chapter_tab(self, chapter_id: int):
        """关闭指定章节的标签页，更新 _open_chapters 映射。"""
        if chapter_id not in self._open_chapters:
            return

        tab_idx, _ = self._open_chapters[chapter_id]
        del self._open_chapters[chapter_id]

        for cid in list(self._open_chapters.keys()):
            idx, editor = self._open_chapters[cid]
            if idx > tab_idx:
                self._open_chapters[cid] = (idx - 1, editor)

        self._editor_tabs.removeTab(tab_idx)

    # ========== 章节编辑器 ==========

    def _on_tree_item_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if isinstance(data, tuple) and data[0] == "chapter":
            chapter_id = data[1]
            self._open_chapter_editor(chapter_id)

    def _open_chapter_editor(self, chapter_id: int):
        if chapter_id in self._open_chapters:
            tab_index, _ = self._open_chapters[chapter_id]
            self._editor_tabs.setCurrentIndex(tab_index)
            return

        chapter = self._chapter_service.get_chapter(chapter_id)
        if not chapter:
            logger.warning(f"章节不存在: {chapter_id}")
            return

        editor = EditorWidget()
        editor.set_content(chapter.content or "")
        # 应用撤销栈深度
        self._apply_undo_stack_depth_to_editor(editor)
        # AI 功能（右键菜单已由 EditorWidget 内置中文版）
        editor.ai_continue_requested.connect(self._on_ai_continue_write)
        editor.ai_polish_requested.connect(self._on_ai_polish)
        editor.ai_rewrite_requested.connect(self._on_ai_rewrite)
        editor.ai_analyze_requested.connect(self._on_ai_analyze)
        editor.content_changed.connect(lambda cid=chapter_id: self._on_editor_content_changed(cid))

        tab_title = f"第{chapter.chapter_number}章 {chapter.title}"
        tab_index = self._editor_tabs.addTab(editor, tab_title)
        self._open_chapters[chapter_id] = (tab_index, editor)

        self._editor_tabs.setCurrentIndex(tab_index)
        self._update_status_word_count(editor)

    def _on_editor_content_changed(self, chapter_id: int):
        if chapter_id not in self._open_chapters:
            return
        tab_index, editor = self._open_chapters[chapter_id]
        tab_text = self._editor_tabs.tabText(tab_index)
        if not tab_text.endswith("*"):
            self._editor_tabs.setTabText(tab_index, tab_text + "*")
        self._update_status_word_count(editor)
        # 防抖刷新统计面板（1秒后执行，避免频繁查库）
        self._stats_debounce_timer.start(1000)

    def _on_tab_changed(self, index: int):
        if index < 0:
            self._current_chapter_id = None
            return
        for chapter_id, (tab_idx, editor) in self._open_chapters.items():
            if tab_idx == index:
                self._current_chapter_id = chapter_id
                self._update_status_word_count(editor)
                # 如果搜索面板打开，重新搜索当前标签页
                if self._search_panel.isVisible() and self._search_panel.search_input.text():
                    self._do_search()
                return
        # 没有匹配的章节（例如欢迎页）
        self._current_chapter_id = None

    def _update_status_word_count(self, editor: EditorWidget):
        word_count = editor.count_words()
        para_count = editor.count_paragraphs()
        self._word_count_label.setText(f"字数：{word_count:,} | 段落：{para_count}")

    def _on_save_current(self):
        current_index = self._editor_tabs.currentIndex()
        if current_index < 0:
            return

        current_chapter_id = None
        for chapter_id, (tab_idx, _) in self._open_chapters.items():
            if tab_idx == current_index:
                current_chapter_id = chapter_id
                break

        if current_chapter_id is None:
            return

        self._save_chapter(current_chapter_id)
        self._status_label.setText("已保存")
        QTimer.singleShot(3000, lambda: self._status_label.setText("就绪"))

    def _save_chapter(self, chapter_id: int):
        if chapter_id not in self._open_chapters:
            return
        tab_index, editor = self._open_chapters[chapter_id]
        if not editor.is_modified():
            return

        content = editor.get_content()
        try:
            self._chapter_service.update_chapter_content(chapter_id, content)
            editor.set_modified(False)
            tab_text = self._editor_tabs.tabText(tab_index)
            if tab_text.endswith("*"):
                self._editor_tabs.setTabText(tab_index, tab_text[:-1])
            self._refresh_stats()
        except Exception as e:
            logger.error(f"保存章节失败: {e}")
            QMessageBox.critical(self, "错误", f"保存章节失败：{str(e)}")

    def _on_autosave(self):
        saved_count = 0
        for chapter_id in list(self._open_chapters.keys()):
            _, editor = self._open_chapters[chapter_id]
            if editor.is_modified():
                self._save_chapter(chapter_id)
                saved_count += 1

        if saved_count > 0:
            self._status_label.setText("已自动保存")
            QTimer.singleShot(3000, lambda: self._status_label.setText("就绪"))

    def _reload_autosave_interval(self):
        """从 QSettings 读取自动保存间隔并重启定时器。"""
        settings = QSettings("NovelWriter", "NovelWriter")
        interval = settings.value("autosave_interval", 30, type=int)
        self._autosave_timer.setInterval(interval * 1000)
        self._autosave_timer.start()

    def _apply_undo_stack_depth_to_editor(self, editor):
        """对单个编辑器应用撤销栈深度设置。"""
        settings = QSettings("NovelWriter", "NovelWriter")
        depth = settings.value("undo_stack_depth", 100, type=int)
        editor.document().setMaximumBlockCount(depth)

    def _apply_undo_stack_depth_to_editors(self):
        """对所有打开的编辑器应用撤销栈深度设置。"""
        settings = QSettings("NovelWriter", "NovelWriter")
        depth = settings.value("undo_stack_depth", 100, type=int)
        for chapter_id, (_, editor) in self._open_chapters.items():
            editor.document().setMaximumBlockCount(depth)

    def _on_general_settings_saved(self):
        """通用设置保存后的回调。"""
        self._reload_autosave_interval()
        self._apply_undo_stack_depth_to_editors()

    # ========== 工具方法 ==========

    def _close_editor_tab(self, index: int):
        chapter_id_to_close = None
        editor_to_close = None
        for chapter_id, (tab_idx, editor) in self._open_chapters.items():
            if tab_idx == index:
                chapter_id_to_close = chapter_id
                editor_to_close = editor
                break

        if chapter_id_to_close is None:
            self._editor_tabs.removeTab(index)
            return

        if editor_to_close.is_modified():
            reply = QMessageBox.question(
                self,
                "未保存的更改",
                "该章节有未保存的更改，是否保存？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Save:
                self._save_chapter(chapter_id_to_close)

        del self._open_chapters[chapter_id_to_close]

        for chapter_id in list(self._open_chapters.keys()):
            tab_idx, editor = self._open_chapters[chapter_id]
            if tab_idx > index:
                self._open_chapters[chapter_id] = (tab_idx - 1, editor)

        self._editor_tabs.removeTab(index)

    def _switch_theme(self, theme: str):
        app = QApplication.instance()
        style_manager.apply_theme(app, theme)
        signal_bus.theme_changed.emit(theme)
        # 持久化保存主题设置
        settings = QSettings("NovelWriter", "NovelWriter")
        settings.setValue("theme", theme)

    def _on_status_message(self, message: str):
        self._status_label.setText(message)
        QTimer.singleShot(3000, lambda: self._status_label.setText("就绪"))

    def _on_project_opened(self, project_id: int):
        self._open_chapters.clear()
        if self._editor_tabs.count() == 1 and self._editor_tabs.tabText(0) == "欢迎":
            self._editor_tabs.removeTab(0)
        self._current_project_id = project_id
        self._load_project_tree(project_id)
        self._refresh_outline()
        self._refresh_stats()

    def _on_word_count_updated(self, count: int):
        self._word_count_label.setText(f"字数：{count:,}")

    def _show_about(self):
        QMessageBox.about(self, "关于 Novel Writer",
            "Novel Writer v0.1.0\n\n"
            "AI 原生小说创作桌面系统\n"
            "基于 PySide6 构建\n\n"
            "© 2026 Novel Writer Team"
        )

    def _refresh_outline(self):
        if self._current_project_id:
            session = db_manager.get_session()
            try:
                project = session.query(Project).filter_by(id=self._current_project_id).first()
                if project:
                    # 兼容旧数据：如果 writing_method 存的是中文名称，自动修正为英文 ID
                    from core.methods.registry import get_method
                    if project.writing_method and not get_method(project.writing_method):
                        from core.methods.registry import list_methods
                        for m in list_methods():
                            if m.name == project.writing_method or project.writing_method in m.name:
                                project.writing_method = m.id
                                session.commit()
                                break
                    self._outline_panel.load_method(project.writing_method)
                else:
                    self._outline_panel.clear()
            finally:
                session.close()
        else:
            self._outline_panel.clear()

    def _refresh_stats(self):
        if self._current_project_id:
            session = db_manager.get_session()
            try:
                project = session.query(Project).filter_by(id=self._current_project_id).first()
                if not project:
                    self._stats_panel.clear()
                    return

                chapters = session.query(Chapter).filter_by(
                    project_id=self._current_project_id,
                    is_deleted=False
                ).all()

                total_words = sum(ch.word_count or 0 for ch in chapters)
                chapter_count = len(chapters)
                volume_count = session.query(Volume).filter_by(
                    project_id=self._current_project_id
                ).count()

                avg_chars_per_chapter = 0
                if chapter_count > 0:
                    avg_chars_per_chapter = int(total_words / chapter_count)

                stats = {
                    "total_words": total_words,
                    "chapter_count": chapter_count,
                    "volume_count": volume_count,
                    "avg_chars_per_chapter": avg_chars_per_chapter,
                }

                if project.target_words and project.target_words > 0:
                    stats["target_words"] = project.target_words

                self._stats_panel.update_stats(stats)
            finally:
                session.close()
        else:
            self._stats_panel.clear()

    def _load_project_tree(self, project_id: int):
        """加载项目树。"""
        session = db_manager.get_session()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return

            self._project_tree.clear()
            root = QTreeWidgetItem([project.name])
            root.setData(0, Qt.UserRole, project.id)
            self._project_tree.addTopLevelItem(root)

            volumes = session.query(Volume).filter_by(project_id=project_id).order_by(Volume.sort_order).all()
            for v in volumes:
                vol_item = QTreeWidgetItem([v.name])
                vol_item.setData(0, Qt.UserRole, ("volume", v.id))
                root.addChild(vol_item)

                chapters = session.query(Chapter).filter_by(
                    volume_id=v.id, is_deleted=False
                ).order_by(Chapter.chapter_number).all()
                for ch in chapters:
                    ch_item = QTreeWidgetItem([f"第{ch.chapter_number}章 {ch.title}"])
                    ch_item.setData(0, Qt.UserRole, ("chapter", ch.id))
                    vol_item.addChild(ch_item)

            root.setExpanded(True)
        finally:
            session.close()

    def _browse_project(self, parent_dialog=None):
        """浏览项目目录。"""
        if parent_dialog:
            parent_dialog.reject()

        dir_path = QFileDialog.getExistingDirectory(
            self, "选择项目目录",
            str(db_manager.data_dir / "projects"),
        )
        if dir_path:
            self._open_project_by_path(dir_path)

    def _open_project_by_path(self, project_path: str):
        """通过路径打开项目。"""
        from pathlib import Path

        session = db_manager.get_session()
        try:
            project = session.query(Project).filter(
                Project.path.like(f"%{project_path}%")
            ).first()

            if not project:
                name = Path(project_path).name
                project = session.query(Project).filter_by(name=name).first()

            if project:
                self._project_service.open_project(project.id)
                self._add_to_recent(project.name, project.path)
                self._update_recent_menu()
            else:
                signal_bus.status_message.emit("未找到匹配的项目")
        finally:
            session.close()

    def _get_recent_projects(self) -> list:
        """获取最近项目列表。"""
        settings = QSettings("NovelWriter", "NovelWriter")
        size = settings.beginReadArray("recent_projects")
        projects = []
        for i in range(size):
            settings.setArrayIndex(i)
            name = settings.value("name", "")
            path = settings.value("path", "")
            if name and path:
                projects.append((name, path))
        settings.endArray()
        return projects

    def _add_to_recent(self, name: str, path: str):
        """添加到最近项目。"""
        settings = QSettings("NovelWriter", "NovelWriter")

        projects = self._get_recent_projects()
        projects = [(n, p) for n, p in projects if n != name and p != path]
        projects.insert(0, (name, path))
        projects = projects[:10]

        settings.beginWriteArray("recent_projects")
        for i, (n, p) in enumerate(projects):
            settings.setArrayIndex(i)
            settings.setValue("name", n)
            settings.setValue("path", p)
        settings.endArray()

    def _update_recent_menu(self):
        """更新最近项目菜单。"""
        self._recent_menu.clear()
        projects = self._get_recent_projects()

        if not projects:
            action = self._recent_menu.addAction("（无最近项目）")
            action.setEnabled(False)
            return

        for name, path in projects:
            action = self._recent_menu.addAction(f"{name}")
            action.setToolTip(path)
            action.triggered.connect(lambda checked, p=path: self._open_project_by_path(p))

    # ========== 项目树拖拽排序 ==========

    def _take_order_snapshot(self):
        """从数据库获取当前排序快照，用于撤销。"""
        if self._current_project_id is None:
            return None
        session = db_manager.get_session()
        try:
            volumes = session.query(Volume).filter_by(
                project_id=self._current_project_id
            ).order_by(Volume.sort_order).all()
            snapshot = {
                'volumes': [(v.id, v.sort_order) for v in volumes],
                'chapters': [],
            }
            for v in volumes:
                chapters = session.query(Chapter).filter_by(
                    volume_id=v.id, is_deleted=False
                ).order_by(Chapter.chapter_number).all()
                for ch in chapters:
                    snapshot['chapters'].append((ch.id, ch.volume_id, ch.chapter_number))
            return snapshot
        finally:
            session.close()

    def _on_tree_rows_moved(self, parent, start, end, dest, row):
        if self._tree_reorder_pending:
            return
        # 在更新数据库之前保存当前数据库中的排序快照
        self._order_snapshot = self._take_order_snapshot()
        self._tree_reorder_pending = True
        QTimer.singleShot(0, self._reorder_from_tree)

    def _reorder_from_tree(self):
        try:
            if self._current_project_id is None:
                return

            root = self._project_tree.topLevelItem(0)
            if not root:
                return

            volume_count = root.childCount()
            for vol_idx in range(volume_count):
                vol_item = root.child(vol_idx)
                vol_data = vol_item.data(0, Qt.UserRole)
                if not isinstance(vol_data, tuple) or vol_data[0] != "volume":
                    continue
                volume_id = vol_data[1]
                self._chapter_service.reorder_volume(volume_id, vol_idx + 1)

                chapter_count = vol_item.childCount()
                for ch_idx in range(chapter_count):
                    ch_item = vol_item.child(ch_idx)
                    ch_data = ch_item.data(0, Qt.UserRole)
                    if not isinstance(ch_data, tuple) or ch_data[0] != "chapter":
                        continue
                    chapter_id = ch_data[1]
                    self._chapter_service.reorder_chapter(chapter_id, volume_id, ch_idx + 1)

            self._update_tab_titles_after_reorder()

            # 显示可撤销的确认提示条
            if self._order_snapshot is not None:
                self._show_reorder_toast(self._order_snapshot)
                self._order_snapshot = None
        except Exception as e:
            logger.error(f"同步树排序到数据库失败: {e}")
        finally:
            self._tree_reorder_pending = False

    def _show_reorder_toast(self, snapshot):
        """在编辑器区域底部显示非阻塞提示条。"""
        toast = QFrame()
        toast.setObjectName("reorder_toast")
        toast.setStyleSheet("""
            QFrame#reorder_toast {
                background-color: rgba(40, 40, 50, 220);
                border-radius: 6px;
                padding: 0px;
            }
            QFrame#reorder_toast QLabel {
                color: white;
                font-size: 13px;
            }
            QFrame#reorder_toast QPushButton {
                background-color: rgba(255, 255, 255, 30);
                color: white;
                border: 1px solid rgba(255, 255, 255, 80);
                border-radius: 4px;
                padding: 4px 14px;
                font-size: 12px;
                min-height: 24px;
            }
            QFrame#reorder_toast QPushButton:hover {
                background-color: rgba(255, 255, 255, 60);
            }
        """)

        layout = QHBoxLayout(toast)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        label = QLabel("章节顺序已调整")
        layout.addWidget(label)
        layout.addStretch()

        undo_btn = QPushButton("撤销")
        # 使用 functools.partial 或局部变量捕获 snapshot 和 toast
        undo_btn.clicked.connect(lambda checked, s=snapshot, t=toast: self._undo_reorder(s, t))
        layout.addWidget(undo_btn)

        # 将提示条插入到编辑器标签页下方、搜索面板上方
        central_layout = self.centralWidget().layout()
        # central_layout 中有 _editor_tabs (index 0) 和 _search_panel (index 1)
        central_layout.insertWidget(1, toast)

        # 5 秒后自动消失
        QTimer.singleShot(5000, toast.deleteLater)

    def _undo_reorder(self, snapshot, toast_widget):
        """从快照恢复排序。"""
        toast_widget.deleteLater()
        session = db_manager.get_session()
        try:
            # 恢复分卷排序
            for vol_id, sort_order in snapshot['volumes']:
                vol = session.query(Volume).filter_by(id=vol_id).first()
                if vol:
                    vol.sort_order = sort_order
            # 恢复章节的位置和所属分卷
            for ch_id, vol_id, ch_num in snapshot['chapters']:
                ch = session.query(Chapter).filter_by(id=ch_id).first()
                if ch:
                    ch.volume_id = vol_id
                    ch.chapter_number = ch_num
            session.commit()
            self._load_project_tree(self._current_project_id)
            self._update_tab_titles_after_reorder()
            signal_bus.status_message.emit("排序已撤销")
        except Exception as e:
            session.rollback()
            logger.error(f"撤销排序失败: {e}")
            signal_bus.status_message.emit("撤销失败")
        finally:
            session.close()

    def _update_tab_titles_after_reorder(self):
        for chapter_id, (tab_idx, _) in list(self._open_chapters.items()):
            chapter = self._chapter_service.get_chapter(chapter_id)
            if chapter:
                tab_title = f"第{chapter.chapter_number}章 {chapter.title}"
                current_text = self._editor_tabs.tabText(tab_idx)
                if current_text.endswith("*"):
                    tab_title += "*"
                self._editor_tabs.setTabText(tab_idx, tab_title)

    # ========== 搜索面板 ==========

    def _init_search_state(self):
        self._current_matches = []
        self._current_match_index = -1
        self._current_search_keyword = ""

    def _toggle_search_panel(self):
        if self._search_panel.isVisible():
            self._on_close_search_panel()
        else:
            self._search_panel.setVisible(True)
            self._search_panel.focus_search()
            editor = self._get_current_editor()
            if editor:
                selected_text = editor.textCursor().selectedText()
                if selected_text:
                    self._search_panel.set_search_text(selected_text)
                    self._do_search()
                else:
                    keyword = self._search_panel.search_input.text()
                    if keyword:
                        self._do_search()

    def _get_current_editor(self):
        current_index = self._editor_tabs.currentIndex()
        if current_index < 0:
            return None
        for chapter_id, (tab_idx, editor) in self._open_chapters.items():
            if tab_idx == current_index and isinstance(editor, EditorWidget):
                return editor
        return None

    def _on_search_text_changed(self, keyword: str):
        self._do_search()

    def _do_search(self):
        """执行搜索并高亮结果。"""
        editor = self._get_current_editor()
        if not editor:
            self._search_panel.set_match_count(0, 0)
            return

        keyword = self._search_panel.search_input.text()
        self._current_search_keyword = keyword

        if not keyword:
            self._clear_all_highlights()
            self._current_matches = []
            self._current_match_index = -1
            self._search_panel.set_match_count(0, 0)
            return

        self._highlight_matches(editor, keyword)

    def _highlight_matches(self, editor: EditorWidget, keyword: str):
        self._clear_all_highlights()
        self._current_matches = []
        self._current_match_index = -1

        if not keyword:
            self._search_panel.set_match_count(0, 0)
            return

        extra_selections = []
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QBrush(QColor("#f0c674")))

        search_cursor = QTextCursor(editor.document())
        while True:
            search_cursor = editor.document().find(keyword, search_cursor)
            if search_cursor.isNull():
                break
            extra_selection = QTextEdit.ExtraSelection()
            extra_selection.cursor = search_cursor
            extra_selection.format = highlight_format
            extra_selections.append(extra_selection)
            # 存储匹配开始和结束位置
            self._current_matches.append((
                search_cursor.selectionStart(),
                search_cursor.selectionEnd()
            ))

        editor.setExtraSelections(extra_selections)

        total = len(self._current_matches)
        if total > 0:
            self._current_match_index = 0
            self._goto_match(0, editor)
        self._search_panel.set_match_count(self._current_match_index + 1 if total > 0 else 0, total)

    def _clear_all_highlights(self):
        """清除所有打开的编辑器的高亮。"""
        for chapter_id, (tab_idx, editor) in self._open_chapters.items():
            if isinstance(editor, EditorWidget):
                editor.setExtraSelections([])

    def _on_search_next(self):
        if not self._current_matches:
            self._do_search()
            return
        editor = self._get_current_editor()
        if not editor:
            return
        self._current_match_index = (self._current_match_index + 1) % len(self._current_matches)
        self._goto_match(self._current_match_index, editor)
        self._search_panel.set_match_count(self._current_match_index + 1, len(self._current_matches))

    def _on_search_prev(self):
        if not self._current_matches:
            self._do_search()
            return
        editor = self._get_current_editor()
        if not editor:
            return
        self._current_match_index = (self._current_match_index - 1) % len(self._current_matches)
        self._goto_match(self._current_match_index, editor)
        self._search_panel.set_match_count(self._current_match_index + 1, len(self._current_matches))

    def _goto_match(self, index: int, editor: EditorWidget):
        if index < 0 or index >= len(self._current_matches):
            return
        start, end = self._current_matches[index]
        cursor = QTextCursor(editor.document())
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        editor.setTextCursor(cursor)
        editor.ensureCursorVisible()

    def _on_replace(self, search_text: str, replace_text: str):
        editor = self._get_current_editor()
        if not editor or not search_text:
            return

        if not self._current_matches:
            self._do_search()
            if not self._current_matches:
                return

        # 如果当前匹配索引无效，重置到0
        if self._current_match_index < 0:
            self._current_match_index = 0

        # 使用存储的位置直接替换
        start, end = self._current_matches[self._current_match_index]
        cursor = QTextCursor(editor.document())
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        editor.setTextCursor(cursor)
        cursor.insertText(replace_text)

        editor.content_changed.emit()
        self._do_search()

    def _on_replace_all(self, search_text: str, replace_text: str):
        editor = self._get_current_editor()
        if not editor or not search_text:
            return

        content = editor.toPlainText()
        new_content = content.replace(search_text, replace_text)
        if new_content != content:
            cursor_pos = editor.textCursor().position()
            editor.setPlainText(new_content)
            cursor = editor.textCursor()
            cursor.setPosition(min(cursor_pos, len(new_content)))
            editor.setTextCursor(cursor)
            editor._modified = True
            editor.content_changed.emit()
            self._do_search()

    def _on_close_search_panel(self):
        self._search_panel.setVisible(False)
        self._clear_all_highlights()
        self._current_matches = []
        self._current_match_index = -1

    # ========== 编辑器右键菜单 ==========

    def _on_editor_context_menu(self, editor, pos):
        """编辑器右键菜单，在默认菜单基础上添加 AI 续写选项。"""
        menu = editor.createStandardContextMenu()
        menu.addSeparator()
        ai_action = menu.addAction("AI 续写")
        ai_action.triggered.connect(self._on_ai_continue_write)
        menu.exec(editor.viewport().mapToGlobal(pos))

    # ========== AI 功能 ==========

    def _on_ai_continue_write(self, word_count: int = 2000):
        """触发 AI 续写。"""
        # 获取当前章节
        if not self._current_chapter_id:
            if self._ai_panel is not None:
                self._ai_panel.set_status("请先打开一个章节")
            return

        try:
            # 创建 AIWorker
            worker = writing_service.continue_write(
                self._current_chapter_id, self._current_project_id,
                max_tokens=word_count
            )

            # 连接信号
            worker.chunk_received.connect(self._on_ai_chunk_received)
            worker.finished_signal.connect(self._on_ai_finished)
            worker.error_signal.connect(self._on_ai_error)
            worker.retry_signal.connect(self._on_ai_retry)

            # 保存引用防止 GC
            self._ai_worker = worker
            self._ai_target_chapter_id = self._current_chapter_id

            # 设置 UI 状态
            self._ai_panel.set_generating(True)
            self._ai_panel.set_status("正在生成...")

            # 设置编辑器只读
            if self._current_chapter_id in self._open_chapters:
                _, editor = self._open_chapters[self._current_chapter_id]
                editor.setReadOnly(True)

            # 启动线程
            worker.start()

            # 发送信号总线信号
            signal_bus.ai_generation_started.emit("continue_write")

        except AIProviderError as e:
            self._ai_panel.set_status(f"错误: {e}")
            QMessageBox.warning(self, "AI 续写", str(e))
        except Exception as e:
            self._ai_panel.set_status(f"错误: {e}")
            QMessageBox.warning(self, "AI 续写失败", str(e))

    def _on_ai_chunk_received(self, text: str):
        """收到 AI 生成的一个文本块（始终插入到目标章节，不受标签页切换影响）。"""
        cid = self._ai_target_chapter_id or self._current_chapter_id
        if cid and cid in self._open_chapters:
            _, editor = self._open_chapters[cid]
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text)
            editor.setTextCursor(cursor)
            editor.ensureCursorVisible()

        # 更新信号总线
        signal_bus.ai_chunk_received.emit(text)

    def _on_ai_finished(self, full_text: str):
        """AI 生成完成。"""
        cid = self._ai_target_chapter_id or self._current_chapter_id
        # 恢复编辑器
        if cid and cid in self._open_chapters:
            tab_idx, editor = self._open_chapters[cid]
            editor.setReadOnly(False)
            # 标记为已修改
            editor.set_modified(True)
            editor.document().setModified(True)
            # 在标签页标题添加 * 标记
            tab_text = self._editor_tabs.tabText(tab_idx)
            if not tab_text.endswith("*"):
                self._editor_tabs.setTabText(tab_idx, tab_text + "*")
            # 触发防抖刷新统计
            self._stats_debounce_timer.start(1000)

        # 更新面板
        word_count = len(full_text.replace(" ", "").replace("\n", ""))
        self._ai_panel.set_generating(False)
        self._ai_panel.set_status(f"已生成 {word_count} 字")
        self._ai_panel.update_providers()

        # 清理 worker
        self._ai_worker = None
        self._ai_target_chapter_id = None
        self._ai_full_text = ""

        signal_bus.ai_generation_finished.emit("continue_write")

    def _on_ai_error(self, error_msg: str):
        """AI 生成出错。"""
        cid = self._ai_target_chapter_id or self._current_chapter_id
        # 恢复编辑器
        if cid and cid in self._open_chapters:
            _, editor = self._open_chapters[cid]
            editor.setReadOnly(False)

        # 更新面板
        self._ai_panel.set_generating(False)
        self._ai_panel.set_status(f"生成失败: {error_msg}")

        # 清理 worker
        self._ai_worker = None
        self._ai_target_chapter_id = None
        self._ai_full_text = ""

        signal_bus.ai_error.emit("continue_write", error_msg)

    def _on_ai_cancel(self):
        """取消 AI 生成。"""
        if self._ai_worker and self._ai_worker.isRunning():
            self._ai_worker.cancel()
            self._ai_panel.set_status("正在取消...")
        else:
            self._ai_panel.set_generating(False)
            self._ai_panel.set_status("已取消")
        self._ai_target_chapter_id = None

    def _on_ai_retry(self, attempt: int, max_retries: int, error_msg: str):
        """AI 重试状态更新。"""
        if self._ai_panel is not None:
            self._ai_panel.set_status(f"连接异常，第 {attempt}/{max_retries} 次重试...")

    def _on_ai_settings(self):
        """打开 AI 设置对话框。"""
        dialog = AISettingsDialog(self)
        dialog.settings_saved.connect(self._on_general_settings_saved)
        dialog.exec()

        # 对话框关闭后刷新面板
        if self._ai_panel is not None:
            self._ai_panel.update_providers()

    # ========== AI 润色/重写/分析功能 ==========

    def _on_ai_polish(self):
        """AI 润色选中文本。"""
        editor = self._get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        if not cursor.hasSelection():
            if self._ai_panel:
                self._ai_panel.set_status("请先选中要润色的文本")
            return

        selected = cursor.selectedText()
        # 保存选中范围以备后续替换
        self._ai_sel_start = cursor.selectionStart()
        self._ai_sel_end = cursor.selectionEnd()
        self._ai_original_text = selected  # 保存原文供差分对比

        try:
            worker = editing_service.polish(selected, "简洁")
            worker.chunk_received.connect(self._on_ai_polish_chunk)
            worker.finished_signal.connect(self._on_ai_polish_finished)
            worker.error_signal.connect(self._on_ai_error)
            worker.retry_signal.connect(self._on_ai_retry)
            self._ai_worker = worker
            self._ai_panel.set_generating(True)
            self._ai_panel.set_status("正在润色...")
            self._ai_full_text = ""
            worker.start()
        except Exception as e:
            self._ai_panel.set_status(f"润色失败: {e}")

    def _on_ai_polish_chunk(self, text: str):
        """收到润色结果片段。"""
        self._ai_full_text += text
        # 实时替换选中文本（随着流式输出不断更新）
        editor = self._get_current_editor()
        if editor and hasattr(self, '_ai_sel_start'):
            cursor = editor.textCursor()
            cursor.setPosition(self._ai_sel_start)
            cursor.setPosition(self._ai_sel_end, QTextCursor.KeepAnchor)
            cursor.insertText(self._ai_full_text)
            # 更新选中范围为插入后的文本范围
            self._ai_sel_end = self._ai_sel_start + len(self._ai_full_text)

    def _on_ai_polish_finished(self, full_text: str):
        """润色完成 - 弹出差分对话框供用户确认。"""
        from PySide6.QtWidgets import QDialog
        self._ai_panel.set_generating(False)
        self._ai_worker = None
        editor = self._get_current_editor()
        if not editor:
            self._ai_panel.set_status("润色完成")
            return

        # 获取原文（从已保存的原文或编辑器中获取）
        original = getattr(self, '_ai_original_text', '')
        if not original:
            cursor = editor.textCursor()
            cursor.setPosition(self._ai_sel_start)
            cursor.setPosition(self._ai_sel_end, QTextCursor.KeepAnchor)
            original = cursor.selectedText()

        # 弹出差分对话框
        dialog = AIPolishDiffDialog(original, full_text, self)
        
        def on_apply(polished_text):
            """用户确认应用润色。"""
            cursor = editor.textCursor()
            cursor.setPosition(self._ai_sel_start)
            cursor.setPosition(self._ai_sel_end, QTextCursor.KeepAnchor)
            cursor.insertText(polished_text)
            editor.set_modified(True)
            word_count = len(polished_text.replace(" ", "").replace("\n", ""))
            self._ai_panel.set_status(f"润色已应用，共 {word_count} 字")

        def on_retry():
            """用户要求重新润色。"""
            self._ai_panel.set_status("重新润色...")
            # 恢复原文
            cursor = editor.textCursor()
            cursor.setPosition(self._ai_sel_start)
            cursor.setPosition(self._ai_sel_end, QTextCursor.KeepAnchor)
            cursor.insertText(original)
            self._ai_sel_end = self._ai_sel_start + len(original)
            # 重新开始润色
            self._on_ai_polish()

        dialog.apply_polish.connect(on_apply)
        dialog.retry_polish.connect(on_retry)
        dialog.rejected.connect(lambda: self._ai_panel.set_status("润色已取消"))

        # 如果用户直接关闭对话框，恢复原文
        result = dialog.exec()
        if result != QDialog.DialogCode.Accepted:
            cursor = editor.textCursor()
            cursor.setPosition(self._ai_sel_start)
            cursor.setPosition(self._ai_sel_end, QTextCursor.KeepAnchor)
            cursor.insertText(original)
            editor.set_modified(False)
            self._ai_panel.set_status("润色已取消")

    def _on_ai_rewrite(self):
        """AI 重写选中文本。"""
        editor = self._get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        if not cursor.hasSelection():
            if self._ai_panel:
                self._ai_panel.set_status("请先选中要重写的文本")
            return

        selected = cursor.selectedText()
        self._ai_sel_start = cursor.selectionStart()
        self._ai_sel_end = cursor.selectionEnd()

        try:
            worker = editing_service.rewrite(selected, "扩写")
            worker.chunk_received.connect(self._on_ai_rewrite_chunk)
            worker.finished_signal.connect(self._on_ai_rewrite_finished)
            worker.error_signal.connect(self._on_ai_error)
            worker.retry_signal.connect(self._on_ai_retry)
            self._ai_worker = worker
            self._ai_panel.set_generating(True)
            self._ai_panel.set_status("正在重写...")
            self._ai_full_text = ""
            worker.start()
        except Exception as e:
            self._ai_panel.set_status(f"重写失败: {e}")

    def _on_ai_rewrite_chunk(self, text: str):
        """收到重写结果片段。"""
        self._ai_full_text += text
        # 实时替换选中文本
        editor = self._get_current_editor()
        if editor and hasattr(self, '_ai_sel_start'):
            cursor = editor.textCursor()
            cursor.setPosition(self._ai_sel_start)
            cursor.setPosition(self._ai_sel_end, QTextCursor.KeepAnchor)
            cursor.insertText(self._ai_full_text)

    def _on_ai_rewrite_finished(self, full_text: str):
        """重写完成 - 直接替换。"""
        self._ai_panel.set_generating(False)
        self._ai_worker = None
        word_count = len(full_text.replace(" ", "").replace("\n", ""))
        self._ai_panel.set_status(f"重写完成，共 {word_count} 字")
        editor = self._get_current_editor()
        if editor:
            editor.set_modified(True)

    def _on_ai_analyze(self):
        """AI 分析当前章节。"""
        editor = self._get_current_editor()
        if not editor:
            return
        content = editor.toPlainText()
        if not content.strip():
            if self._ai_panel:
                self._ai_panel.set_status("当前章节为空，无法分析")
            return

        try:
            worker = analysis_service.analyze_chapter(content, "")
            # 分析结果一次性返回，在 finished 中处理
            worker.chunk_received.connect(self._on_ai_analyze_chunk)
            worker.finished_signal.connect(self._on_ai_analyze_finished)
            worker.error_signal.connect(self._on_ai_error)
            worker.retry_signal.connect(self._on_ai_retry)
            self._ai_worker = worker
            self._ai_panel.set_generating(True)
            self._ai_panel.set_status("正在分析...")
            self._ai_full_text = ""
            worker.start()
        except Exception as e:
            self._ai_panel.set_status(f"分析失败: {e}")

    def _on_ai_analyze_chunk(self, text: str):
        """收到分析结果片段。"""
        self._ai_full_text += text

    def _on_ai_analyze_finished(self, full_text: str):
        """分析完成 - 结果显示在对话面板中。"""
        self._ai_panel.set_generating(False)
        self._ai_panel.set_status("分析完成")
        self._ai_worker = None

        # 在 AI 对话面板中显示分析结果
        if self._ai_panel:
            self._ai_panel.set_status("分析完成")
            # 在 AI 面板的对话区显示分析结果
            self._ai_panel.add_system_message(f"章节分析报告\n\n{full_text}")

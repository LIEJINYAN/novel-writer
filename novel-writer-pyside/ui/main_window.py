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
from PySide6.QtCore import Qt, QTimer, QSettings, QAbstractItemModel, QRegularExpression
from PySide6.QtGui import QAction, QKeySequence, QShortcut, QTextCursor, QTextCharFormat, QColor, QBrush, QTextDocument

from ui.styles.style_manager import style_manager
from ui.dialogs.new_project_dialog import NewProjectDialog
from ui.dialogs.ai_settings_dialog import AISettingsDialog
from ui.editor.editor_widget import EditorWidget
from ui.editor.editor_container import EditorContainer
from ui.sidebar.outline_panel import OutlinePanel
from ui.sidebar.stats_panel import StatsPanel
from ui.sidebar.ai_panel import AIPanel
from ui.sidebar.character_panel import CharacterPanel
from ui.sidebar.plot_panel import PlotPanel
from ui.sidebar.relationship_panel import RelationshipPanel
from ui.sidebar.timeline_panel import TimelinePanel
from ui.sidebar.world_panel import WorldPanel
from ui.sidebar.check_panel import CheckPanel
from ui.dialogs.ai_polish_diff_dialog import AIPolishDiffDialog
from ui.editor.ai_chat_panel import AIChatWidget
from utils.signal_bus import signal_bus
from utils.logger import logger
from services.project_service import ProjectService
from services.chapter_service import ChapterService
from services.editor_service import EditorService
from services.project_info_service import project_info_service
from services.ai_service import AIService
from core.ai.base import AIProviderError
from models import db_manager, Project, Volume, Chapter
from services.export_service import ExportService
from services.import_service import ImportService
from services.txt_import_service import TxtImportService
from services.epub_import_service import EpubImportService
from services.pdf_import_service import PdfImportService
from ui.dialogs.import_preview_dialog import ImportPreviewDialog
from ui.dialogs.trash_dialog import TrashDialog
from ui.dialogs.creative_wizard import CreativeWizard


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
        self._ai_service = AIService()
        self._export_service = ExportService()
        self._txt_import_service = TxtImportService()
        self._current_project_id = None
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
        self._auto_hidden_left = False  # 标记左侧栏是否被自动隐藏
        self._init_window()
        self._init_menu()
        self._init_toolbar()
        self._init_central_widget()
        self._init_docks()
        self._init_statusbar()
        self._editor_service = EditorService(self._chapter_service, self._editor_tabs)
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

        self._save_all_action = QAction("全部保存", self)
        self._save_all_action.setShortcut("Ctrl+Shift+S")
        self._save_all_action.triggered.connect(self._on_save_all)
        file_menu.addAction(self._save_all_action)

        file_menu.addSeparator()

        close_action = QAction("关闭项目", self)
        close_action.triggered.connect(self._on_close_project)
        file_menu.addAction(close_action)

        delete_action = QAction("删除项目", self)
        delete_action.triggered.connect(self._on_delete_project)
        file_menu.addAction(delete_action)

        close_tab_action = QAction("关闭标签页", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(self._on_close_current_tab)
        file_menu.addAction(close_tab_action)

        file_menu.addSeparator()

        # 导入子菜单
        import_menu = file_menu.addMenu("导入(&I)")

        import_original_action = QAction("从原版导入...", self)
        import_original_action.triggered.connect(self._on_import_original)
        import_menu.addAction(import_original_action)

        import_menu.addSeparator()

        txt_import_action = QAction("从 TXT/MD 导入...", self)
        txt_import_action.triggered.connect(self._on_import_txt)
        import_menu.addAction(txt_import_action)

        epub_import_action = QAction("从 EPUB 导入...", self)
        epub_import_action.triggered.connect(self._on_import_epub)
        import_menu.addAction(epub_import_action)

        pdf_import_action = QAction("从 PDF 导入...", self)
        pdf_import_action.triggered.connect(self._on_import_pdf)
        import_menu.addAction(pdf_import_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&Q)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ========== 编辑菜单 ==========
        self._edit_menu = menubar.addMenu("编辑(&E)")

        # ========== 视图菜单 ==========
        view_menu = menubar.addMenu("视图(&V)")

        # 专注模式
        focus_action = QAction("专注模式", self)
        focus_action.setShortcut("F11")
        focus_action.triggered.connect(self._on_focus_mode)
        view_menu.addAction(focus_action)

        view_menu.addSeparator()

        # 面板切换子菜单
        panel_menu = view_menu.addMenu("面板切换")
        toggle_left_action = QAction("切换左侧栏", self)
        toggle_left_action.setShortcut("Ctrl+Shift+L")
        toggle_left_action.triggered.connect(self._on_toggle_left_panel)
        panel_menu.addAction(toggle_left_action)

        toggle_right_action = QAction("切换右侧栏", self)
        toggle_right_action.setShortcut("Ctrl+Shift+R")
        toggle_right_action.triggered.connect(self._on_toggle_right_panel)
        panel_menu.addAction(toggle_right_action)

        toggle_bottom_action = QAction("切换底部面板", self)
        toggle_bottom_action.setShortcut("Ctrl+Shift+B")
        toggle_bottom_action.triggered.connect(self._on_toggle_bottom_panel)
        panel_menu.addAction(toggle_bottom_action)

        view_menu.addSeparator()

        # 主题子菜单
        theme_menu = view_menu.addMenu("主题")
        dark_action = QAction("暗色", self)
        dark_action.triggered.connect(lambda: self._switch_theme("dark"))
        theme_menu.addAction(dark_action)

        light_action = QAction("亮色", self)
        light_action.triggered.connect(lambda: self._switch_theme("light"))
        theme_menu.addAction(light_action)

        eye_protection_action = QAction("护眼黄", self)
        eye_protection_action.triggered.connect(lambda: self._switch_theme("eye_protection"))
        theme_menu.addAction(eye_protection_action)

        # 字体大小子菜单
        font_menu = view_menu.addMenu("字体大小")
        zoom_in_action = QAction("放大", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self._on_zoom_in)
        font_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("缩小", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self._on_zoom_out)
        font_menu.addAction(zoom_out_action)

        zoom_reset_action = QAction("重置", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self._on_zoom_reset)
        font_menu.addAction(zoom_reset_action)

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

        # ========== 写作菜单 ==========
        writing_menu = menubar.addMenu("写作(&W)")

        self._constitution_action = QAction("创作宪法...", self)
        self._constitution_action.triggered.connect(self._on_creative_wizard)
        writing_menu.addAction(self._constitution_action)

        specify_action = QAction("故事规格...", self)
        specify_action.triggered.connect(self._on_specify)
        writing_menu.addAction(specify_action)

        clarify_action = QAction("决策澄清...", self)
        clarify_action.triggered.connect(self._on_clarify)
        writing_menu.addAction(clarify_action)

        plan_action = QAction("创作计划...", self)
        plan_action.triggered.connect(self._on_plan)
        writing_menu.addAction(plan_action)

        tasks_action = QAction("任务分解...", self)
        tasks_action.triggered.connect(self._on_tasks)
        writing_menu.addAction(tasks_action)

        writing_menu.addSeparator()

        ai_write_action = QAction("AI 续写", self)
        ai_write_action.setShortcut("Ctrl+Enter")
        ai_write_action.triggered.connect(self._on_ai_continue_write)
        writing_menu.addAction(ai_write_action)

        quality_action = QAction("质量分析...", self)
        quality_action.triggered.connect(self._on_writing_quality_analysis)
        writing_menu.addAction(quality_action)

        writing_menu.addSeparator()

        audit_action = QAction("AI 审计...", self)
        audit_action.triggered.connect(self._on_writing_ai_audit)
        writing_menu.addAction(audit_action)

        # ========== AI 菜单 ==========
        ai_menu = menubar.addMenu("AI")

        ai_chat_action = QAction("AI 对话面板", self)
        ai_chat_action.setShortcut("Ctrl+Shift+A")
        ai_chat_action.triggered.connect(self._on_toggle_ai_chat)
        ai_menu.addAction(ai_chat_action)

        # 切换提供商子菜单
        provider_menu = ai_menu.addMenu("切换提供商")
        for provider_name in ["OpenAI", "Claude", "Gemini", "Ollama", "DeepSeek"]:
            act = QAction(provider_name, self)
            act.triggered.connect(lambda checked=False, p=provider_name.lower(): self._on_ai_provider_changed(p))
            provider_menu.addAction(act)

        # 切换模型子菜单
        model_menu = ai_menu.addMenu("切换模型")
        for model_name in ["gpt-4o", "claude-sonnet-4-5", "gemini-2.0-flash", "deepseek-chat"]:
            act = QAction(model_name, self)
            act.triggered.connect(lambda checked=False, m=model_name: self._on_ai_switch_model(m))
            model_menu.addAction(act)

        ai_menu.addSeparator()

        ai_settings_action = QAction("AI 设置...", self)
        ai_settings_action.triggered.connect(self._on_ai_settings)
        ai_menu.addAction(ai_settings_action)

        ai_menu.addSeparator()

        # 专家模式子菜单
        expert_menu = ai_menu.addMenu("专家模式")
        expert_structure_action = QAction("剧情结构专家", self)
        expert_structure_action.triggered.connect(lambda: self._on_ai_expert_mode("剧情结构专家"))
        expert_menu.addAction(expert_structure_action)

        expert_character_action = QAction("人物塑造专家", self)
        expert_character_action.triggered.connect(lambda: self._on_ai_expert_mode("人物塑造专家"))
        expert_menu.addAction(expert_character_action)

        expert_world_action = QAction("世界观构建专家", self)
        expert_world_action.triggered.connect(lambda: self._on_ai_expert_mode("世界观构建专家"))
        expert_menu.addAction(expert_world_action)

        expert_style_action = QAction("风格把控专家", self)
        expert_style_action.triggered.connect(lambda: self._on_ai_expert_mode("风格把控专家"))
        expert_menu.addAction(expert_style_action)

        # ========== 追踪菜单 ==========
        tracking_menu = menubar.addMenu("追踪(&T)")

        tracking_panel_action = QAction("综合追踪面板", self)
        tracking_panel_action.triggered.connect(self._on_tracking_panel)
        tracking_menu.addAction(tracking_panel_action)

        plot_check_action = QAction("情节检查...", self)
        plot_check_action.triggered.connect(self._on_plot_check)
        tracking_menu.addAction(plot_check_action)

        timeline_action = QAction("时间线管理...", self)
        timeline_action.triggered.connect(self._on_timeline_management)
        tracking_menu.addAction(timeline_action)

        relationship_action = QAction("关系图谱...", self)
        relationship_action.triggered.connect(self._on_relationship_graph)
        tracking_menu.addAction(relationship_action)

        tracking_menu.addSeparator()

        consistency_action = QAction("一致性检查...", self)
        consistency_action.triggered.connect(self._on_consistency_check)
        tracking_menu.addAction(consistency_action)

        # ========== 导出菜单 ==========
        export_menu = menubar.addMenu("导出(&X)")

        export_txt_action = QAction("全本导出 TXT", self)
        export_txt_action.triggered.connect(self._on_export_txt)
        export_menu.addAction(export_txt_action)

        export_md_action = QAction("全本导出 Markdown", self)
        export_md_action.triggered.connect(self._on_export_md)
        export_menu.addAction(export_md_action)

        export_menu.addSeparator()

        export_epub_action = QAction("全本导出 EPUB...", self)
        export_epub_action.triggered.connect(self._on_export_epub)
        export_menu.addAction(export_epub_action)

        export_pdf_action = QAction("全本导出 PDF...", self)
        export_pdf_action.triggered.connect(self._on_export_pdf)
        export_menu.addAction(export_pdf_action)

        export_menu.addSeparator()

        export_original_action = QAction("导出为原版格式...", self)
        export_original_action.triggered.connect(self._on_export_original)
        export_menu.addAction(export_original_action)

        # ========== 工具菜单 ==========
        tool_menu = menubar.addMenu("工具(&T)")

        settings_action = QAction("应用设置...", self)
        settings_action.triggered.connect(self._on_app_settings)
        tool_menu.addAction(settings_action)

        tool_menu.addSeparator()

        ai_settings_action = QAction("AI 设置...", self)
        ai_settings_action.triggered.connect(self._on_ai_settings)
        tool_menu.addAction(ai_settings_action)

        tool_menu.addSeparator()

        trash_action = QAction("回收站...", self)
        trash_action.triggered.connect(self._on_open_trash)
        tool_menu.addAction(trash_action)

        # ========== 帮助菜单 ==========
        help_menu = menubar.addMenu("帮助(&H)")
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _init_toolbar(self):
        toolbar = QToolBar("主工具栏", self)
        toolbar.setObjectName("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        new_btn = toolbar.addAction("新建")
        new_btn.triggered.connect(self._on_new_project)

        open_btn = toolbar.addAction("打开")
        open_btn.triggered.connect(self._on_open_project)

        toolbar.addSeparator()

        self._undo_act = toolbar.addAction("撤销")
        self._undo_act.setShortcut(QKeySequence.Undo)
        self._undo_act.setEnabled(False)
        self._undo_act.triggered.connect(lambda: self._get_current_editor() and self._get_current_editor().undo())

        self._redo_act = toolbar.addAction("重做")
        self._redo_act.setShortcut(QKeySequence.Redo)
        self._redo_act.setEnabled(False)
        self._redo_act.triggered.connect(lambda: self._get_current_editor() and self._get_current_editor().redo())

    def _init_central_widget(self):
        central_container = QWidget()
        central_container.setObjectName("central_container")
        layout = QVBoxLayout(central_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._editor_tabs = QTabWidget()
        self._editor_tabs.setObjectName("editor_tabs")
        self._editor_tabs.setTabsClosable(True)
        self._editor_tabs.tabCloseRequested.connect(self._close_editor_tab)
        self._editor_tabs.setMovable(True)
        # 标签页右键菜单（批量关闭）
        self._editor_tabs.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self._editor_tabs.tabBar().customContextMenuRequested.connect(self._on_tab_bar_context_menu)
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
        self._project_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
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

        # 关系面板
        self._relationship_panel = RelationshipPanel()
        self._sidebar_tabs.addTab(self._relationship_panel, "关系")

        # 时间线面板
        self._timeline_panel = TimelinePanel()
        self._sidebar_tabs.addTab(self._timeline_panel, "时间线")

        # 世界观面板
        self._world_panel = WorldPanel()
        self._sidebar_tabs.addTab(self._world_panel, "世界观")

        # 检查面板
        self._check_panel = CheckPanel()
        self._check_panel.navigate_to_chapter.connect(self._open_chapter_editor)
        self._sidebar_tabs.addTab(self._check_panel, "检查")

        self._sidebar_dock.setWidget(self._sidebar_tabs)
        self._sidebar_dock.setMinimumWidth(250)
        self.addDockWidget(Qt.RightDockWidgetArea, self._sidebar_dock)

        # 底部 AI 对话面板
        self._ai_chat_dock = QDockWidget("AI 对话", self)
        self._ai_chat_dock.setObjectName("ai_chat_dock")
        self._ai_chat_widget = AIChatWidget()
        self._ai_chat_dock.setWidget(self._ai_chat_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self._ai_chat_dock)
        self._ai_chat_dock.hide()  # 默认隐藏

    def _init_statusbar(self):
        self._status_label = QLabel("就绪")
        self.statusBar().addWidget(self._status_label)

        self._word_count_label = QLabel("字数：0")
        self.statusBar().addPermanentWidget(self._word_count_label)

        self._line_count_label = QLabel("行数：0")
        self.statusBar().addPermanentWidget(self._line_count_label)

        self._para_count_label = QLabel("段落：0")
        self.statusBar().addPermanentWidget(self._para_count_label)

        self._project_name_label = QLabel("")
        self.statusBar().addPermanentWidget(self._project_name_label)

        self._ai_provider_label = QLabel("AI: -")
        self.statusBar().addPermanentWidget(self._ai_provider_label)

    def _init_connections(self):
        signal_bus.status_message.connect(self._on_status_message)
        signal_bus.project_opened.connect(self._on_project_opened)
        signal_bus.word_count_updated.connect(self._on_word_count_updated)
        self._project_tree.itemClicked.connect(self._on_tree_item_clicked)
        self._editor_tabs.currentChanged.connect(self._on_tab_changed)
        self._save_action.triggered.connect(self._on_save_current)
        self._editor_service.reload_autosave_interval()

        # 编辑器服务信号
        self._editor_service.autosave_completed.connect(self._on_autosave_completed)
        self._editor_service.chapter_saved.connect(self._on_chapter_saved)

        self._search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self._search_shortcut.activated.connect(self._toggle_search_panel)

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

        # 全局快捷键
        QShortcut(QKeySequence("Ctrl+W"), self, self._on_close_current_tab)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self._on_save_all)
        QShortcut(QKeySequence("Ctrl+Shift+D"), self, self._on_generate_dialogue)
        QShortcut(QKeySequence("Ctrl+/"), self, self._on_show_shortcuts)

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
            self._ai_service.init()
        except Exception as e:
            logger.error(f"AI 管理器初始化失败: {e}")
        # 刷新 AI 面板的提供商列表
        if self._ai_panel is not None:
            self._ai_panel.update_providers()

    def _on_open_trash(self):
        """打开回收站对话框。"""
        dialog = TrashDialog(self)
        dialog.exec()
        # 关闭回收站后刷新项目树（可能有恢复/删除操作）
        self._reload_project_tree()

    def _on_ai_provider_changed(self, provider_name: str):
        """AI 面板切换提供商。"""
        try:
            self._ai_service.set_active_provider(provider_name)
            logger.info(f"切换 AI 提供商: {provider_name}")
            if self._ai_panel is not None:
                self._ai_panel.update_providers()
            self._update_ai_provider_label()
        except Exception as e:
            logger.error(f"切换提供商失败: {e}")

    # ========== 项目操作 ==========

    def _on_new_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec():
            info = dialog.get_project_info()
            try:
                project = self._project_service.create_project(info)
                db_manager.open_project(project.path)
                project_info_service.create(
                    name=project.name,
                    genre=project.genre,
                    writing_method=project.writing_method,
                )
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

    def _update_ai_provider_label(self):
        """更新状态栏的 AI 提供商标签。"""
        try:
            from core.ai.manager import ai_manager
            active = ai_manager.get_active_provider()
            if active:
                self._ai_provider_label.setText(f"AI: {active.display_name}")
            else:
                self._ai_provider_label.setText("AI: -")
        except Exception:
            self._ai_provider_label.setText("AI: -")

    def resizeEvent(self, event):
        """响应窗口大小变化，自动隐藏/显示侧栏。"""
        super().resizeEvent(event)
        width = self.width()

        if width < 1000 and not self._auto_hidden_left:
            # 自动隐藏左侧栏
            if self._project_dock.isVisible():
                self._project_dock.setVisible(False)
                self._auto_hidden_left = True
        elif width >= 1400 and self._auto_hidden_left:
            # 恢复左侧栏
            self._project_dock.setVisible(True)
            self._auto_hidden_left = False

    def _on_close_project(self):
        """关闭当前项目。"""
        if self._current_project_id is None:
            signal_bus.status_message.emit("当前没有打开的项目")
            return

        self._editor_service.save_all()
        self._editor_service.close_all_editors()
        self._current_project_id = None
        self._project_tree.clear()
        self._editor_tabs.clear()
        self._word_count_label.setText("字数：0")
        self._line_count_label.setText("行数：0")
        self._para_count_label.setText("段落：0")
        self._project_name_label.setText("")
        self._ai_provider_label.setText("AI: -")
        self._outline_panel.clear()
        self._stats_panel.clear()
        self._character_panel.clear()
        self._plot_panel.clear()
        self._relationship_panel.clear()
        self._timeline_panel.clear()
        self._world_panel.clear()
        self._check_panel.clear()
        self._show_welcome_page()
        db_manager.close_project()
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

        # 检查是否选中了多个章节（批量操作）
        selected_items = self._project_tree.selectedItems()
        selected_chapters = [
            si for si in selected_items
            if isinstance(si.data(0, Qt.UserRole), tuple)
            and si.data(0, Qt.UserRole)[0] == "chapter"
        ]

        if len(selected_chapters) > 1:
            self._show_batch_chapter_menu(pos, selected_chapters)
            return

        menu = QMenu(self)
        data = item.data(0, Qt.UserRole)

        # 根节点（项目）
        if isinstance(data, int):
            open_folder_action = menu.addAction("在资源管理器中显示")
            open_folder_action.triggered.connect(self._on_open_project_folder)
            menu.addSeparator()
            trash_action = menu.addAction("回收站...")
            trash_action.triggered.connect(self._on_open_trash)
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
            menu.addSeparator()
            export_vol_txt = menu.addAction("导出分卷为 TXT")
            export_vol_txt.triggered.connect(lambda: self._on_export_volume_txt(volume_id))
            export_vol_md = menu.addAction("导出分卷为 MD")
            export_vol_md.triggered.connect(lambda: self._on_export_volume_md(volume_id))
            menu.addSeparator()
            import_vol_txt = menu.addAction("从文件夹导入章节...")
            import_vol_txt.triggered.connect(lambda: self._on_import_volume_dir(volume_id))

        # 章节节点
        elif isinstance(data, tuple) and data[0] == "chapter":
            chapter_id = data[1]
            rename_chapter_action = menu.addAction("重命名章节...")
            rename_chapter_action.triggered.connect(lambda: self._on_rename_chapter(chapter_id))
            delete_chapter_action = menu.addAction("删除章节...")
            delete_chapter_action.triggered.connect(lambda: self._on_delete_chapter(chapter_id))
            menu.addSeparator()
            export_ch_txt = menu.addAction("导出为 TXT")
            export_ch_txt.triggered.connect(lambda: self._on_export_chapter_txt(chapter_id))
            export_ch_md = menu.addAction("导出为 MD")
            export_ch_md.triggered.connect(lambda: self._on_export_chapter_md(chapter_id))
            menu.addSeparator()
            import_ch_file = menu.addAction("从文件导入...")
            import_ch_file.triggered.connect(lambda: self._on_import_chapter_file(chapter_id))

        menu.exec(self._project_tree.viewport().mapToGlobal(pos))

    def _show_batch_chapter_menu(self, pos, selected_chapters):
        """显示批量章节操作菜单。"""
        chapter_ids = [si.data(0, Qt.UserRole)[1] for si in selected_chapters]
        count = len(chapter_ids)
        menu = QMenu(self)
        menu.setTitle(f"批量操作 ({count} 个章节)")

        batch_delete = menu.addAction(f"删除选中的 {count} 个章节...")
        batch_delete.triggered.connect(lambda: self._on_batch_delete_chapters(chapter_ids))

        menu.addSeparator()

        batch_export_txt = menu.addAction(f"导出选中章节为 TXT...")
        batch_export_txt.triggered.connect(lambda: self._on_batch_export_chapters_txt(chapter_ids))

        batch_export_md = menu.addAction(f"导出选中章节为 MD...")
        batch_export_md.triggered.connect(lambda: self._on_batch_export_chapters_md(chapter_ids))

        menu.addSeparator()

        # 移动到子菜单
        move_menu = menu.addMenu("移动到分卷...")
        session = db_manager.get_session()
        try:
            volumes = session.query(Volume).filter_by(
                project_id=self._current_project_id
            ).order_by(Volume.sort_order).all()
            for vol in volumes:
                vol_action = move_menu.addAction(vol.name)
                vol_action.triggered.connect(
                    lambda checked=False, v=vol.id: self._on_batch_move_chapters(chapter_ids, v)
                )
        finally:
            session.close()

        menu.exec(self._project_tree.viewport().mapToGlobal(pos))

    def _on_batch_delete_chapters(self, chapter_ids: list):
        """批量删除章节。"""
        reply = QMessageBox.warning(
            self, "确认批量删除",
            f"确定要删除选中的 {len(chapter_ids)} 个章节吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        # 关闭已打开的标签页
        for ch_id in chapter_ids:
            if self._editor_service.is_open(ch_id):
                self._close_chapter_tab(ch_id)

        try:
            for ch_id in chapter_ids:
                self._chapter_service.delete_chapter(ch_id)
            self._reload_project_tree()
            signal_bus.status_message.emit(f"已删除 {len(chapter_ids)} 个章节")
        except Exception as e:
            logger.error(f"批量删除章节失败: {e}")
            QMessageBox.critical(self, "错误", f"批量删除失败：{str(e)}")

    def _on_batch_export_chapters_txt(self, chapter_ids: list):
        """批量导出选中章节为 TXT。"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not dir_path:
            return

        success = 0
        for ch_id in chapter_ids:
            ch = self._chapter_service.get_chapter(ch_id)
            if not ch:
                continue
            file_name = f"第{ch.chapter_number}章 {ch.title}.txt"
            # 过滤文件名非法字符
            file_name = re.sub(r'[\\/:*?"<>|]', '', file_name)
            file_path = str(Path(dir_path) / file_name)
            try:
                self._export_service.export_chapter_txt(ch_id, file_path)
                success += 1
            except Exception as e:
                logger.error(f"导出章节 {ch_id} 失败: {e}")

        QMessageBox.information(self, "导出完成", f"成功导出 {success}/{len(chapter_ids)} 个章节")
        signal_bus.status_message.emit(f"批量导出 TXT 完成: {success}/{len(chapter_ids)}")

    def _on_batch_export_chapters_md(self, chapter_ids: list):
        """批量导出选中章节为 MD。"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not dir_path:
            return

        success = 0
        for ch_id in chapter_ids:
            ch = self._chapter_service.get_chapter(ch_id)
            if not ch:
                continue
            file_name = f"第{ch.chapter_number}章 {ch.title}.md"
            file_name = re.sub(r'[\\/:*?"<>|]', '', file_name)
            file_path = str(Path(dir_path) / file_name)
            try:
                self._export_service.export_chapter_md(ch_id, file_path)
                success += 1
            except Exception as e:
                logger.error(f"导出章节 {ch_id} 失败: {e}")

        QMessageBox.information(self, "导出完成", f"成功导出 {success}/{len(chapter_ids)} 个章节")
        signal_bus.status_message.emit(f"批量导出 MD 完成: {success}/{len(chapter_ids)}")

    def _on_batch_move_chapters(self, chapter_ids: list, target_volume_id: int):
        """批量移动章节到指定分卷。"""
        try:
            for ch_id in chapter_ids:
                self._chapter_service.reorder_chapter(ch_id, target_volume_id, 0)
            self._reload_project_tree()
            signal_bus.status_message.emit(f"已移动 {len(chapter_ids)} 个章节")
        except Exception as e:
            logger.error(f"批量移动章节失败: {e}")
            QMessageBox.critical(self, "错误", f"批量移动失败：{str(e)}")

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

            for chapter_id, (tab_idx, _) in list(self._editor_service.get_open_chapters().items()):
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
            for chapter_id, (_, _) in list(self._editor_service.get_open_chapters().items()):
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

            if self._editor_service.is_open(chapter_id):
                tab_idx = self._editor_service.get_tab_index(chapter_id)
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

            if self._editor_service.is_open(chapter_id):
                self._close_chapter_tab(chapter_id)

            self._chapter_service.delete_chapter(chapter_id)
            self._load_project_tree(self._current_project_id)
            signal_bus.status_message.emit(f"章节已删除: {chapter.title}")
        except Exception as e:
            logger.error(f"删除章节失败: {e}")
            QMessageBox.critical(self, "错误", f"删除章节失败：{str(e)}")

    # ========== 导出/导入操作 ==========

    def _on_import_original(self):
        """从原版格式导入项目。"""
        if self._current_project_id is not None:
            reply = QMessageBox.question(
                self, "确认导入",
                "导入操作将创建一个新项目，当前项目不受影响。是否继续？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply != QMessageBox.Yes:
                return

        dir_path = QFileDialog.getExistingDirectory(self, "选择原版项目目录")
        if not dir_path:
            return

        try:
            project_id = ImportService.import_original_project(dir_path)
            self._load_project_tree(project_id)
            signal_bus.status_message.emit("原版项目导入成功")
        except Exception as e:
            logger.error(f"导入原版项目失败: {e}")
            QMessageBox.critical(self, "导入失败", f"导入原版项目失败：\n{str(e)}")

    def _get_project_name(self, project_id: int) -> str:
        """获取项目名称。"""
        session = db_manager.get_session()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            return project.name if project else ""
        finally:
            session.close()

    def _on_export_txt(self):
        """导出全本为 TXT。"""
        if self._current_project_id is None:
            QMessageBox.warning(self, "提示", "请先打开一个项目")
            return

        project_name = self._get_project_name(self._current_project_id)
        if not project_name:
            return

        default_name = f"{project_name}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为 TXT", default_name, "文本文件 (*.txt)"
        )
        if not file_path:
            return

        try:
            self._export_service.export_txt(self._current_project_id, file_path)
            signal_bus.status_message.emit(f"TXT 导出成功: {file_path}")
        except Exception as e:
            logger.error(f"TXT 导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"TXT 导出失败：\n{str(e)}")

    def _on_export_md(self):
        """导出全本为 Markdown。"""
        if self._current_project_id is None:
            QMessageBox.warning(self, "提示", "请先打开一个项目")
            return

        project_name = self._get_project_name(self._current_project_id)
        if not project_name:
            return

        default_name = f"{project_name}.md"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为 Markdown", default_name, "Markdown 文件 (*.md)"
        )
        if not file_path:
            return

        try:
            self._export_service.export_md(self._current_project_id, file_path)
            signal_bus.status_message.emit(f"Markdown 导出成功: {file_path}")
        except Exception as e:
            logger.error(f"Markdown 导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"Markdown 导出失败：\n{str(e)}")

    def _on_export_epub(self):
        """导出全本为 EPUB。"""
        if self._current_project_id is None:
            QMessageBox.warning(self, "提示", "请先打开一个项目")
            return

        project_name = self._get_project_name(self._current_project_id)
        if not project_name:
            return

        title, ok = QInputDialog.getText(self, "EPUB 导出", "请输入书名：", text=project_name)
        if not ok or not title:
            return
        author, ok = QInputDialog.getText(self, "EPUB 导出", "请输入作者名：")
        if not ok:
            return

        default_name = f"{project_name}.epub"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为 EPUB", default_name, "EPUB 电子书 (*.epub)"
        )
        if not file_path:
            return

        settings = {"author": author}
        try:
            self._export_service.export_epub(self._current_project_id, file_path, settings)
            signal_bus.status_message.emit(f"EPUB 导出成功: {file_path}")
        except Exception as e:
            logger.error(f"EPUB 导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"EPUB 导出失败：\n{str(e)}")

    def _on_export_pdf(self):
        """导出全本为 PDF。"""
        if self._current_project_id is None:
            QMessageBox.warning(self, "提示", "请先打开一个项目")
            return

        project_name = self._get_project_name(self._current_project_id)
        if not project_name:
            return

        title, ok = QInputDialog.getText(self, "PDF 导出", "请输入书名：", text=project_name)
        if not ok or not title:
            return
        author, ok = QInputDialog.getText(self, "PDF 导出", "请输入作者名：")
        if not ok:
            return
        font_size, ok = QInputDialog.getInt(self, "PDF 导出", "请输入字号：", value=12, min=8, max=48)
        if not ok:
            return

        default_name = f"{project_name}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为 PDF", default_name, "PDF 文件 (*.pdf)"
        )
        if not file_path:
            return

        settings = {"author": author, "font_size": font_size}
        try:
            self._export_service.export_pdf(self._current_project_id, file_path, settings)
            signal_bus.status_message.emit(f"PDF 导出成功: {file_path}")
        except Exception as e:
            logger.error(f"PDF 导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"PDF 导出失败：\n{str(e)}")

    def _on_export_original(self):
        """导出为原版格式。"""
        if self._current_project_id is None:
            QMessageBox.warning(self, "提示", "请先打开一个项目")
            return

        project_name = self._get_project_name(self._current_project_id)
        if not project_name:
            return

        dir_path = QFileDialog.getExistingDirectory(self, "选择导出目标目录")
        if not dir_path:
            return

        target_path = str(Path(dir_path) / project_name)
        try:
            self._export_service.export_to_original(self._current_project_id, target_path)
            signal_bus.status_message.emit(f"原版格式导出成功: {target_path}")
        except Exception as e:
            logger.error(f"原版格式导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"原版格式导出失败：\n{str(e)}")

    def _on_export_chapter_txt(self, chapter_id: int):
        """导出单章为 TXT。"""
        default_name = f"chapter_{chapter_id}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出章节为 TXT", default_name, "文本文件 (*.txt)"
        )
        if not file_path:
            return

        try:
            self._export_service.export_chapter_txt(chapter_id, file_path)
            signal_bus.status_message.emit(f"章节 TXT 导出成功: {file_path}")
        except Exception as e:
            logger.error(f"章节 TXT 导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"章节 TXT 导出失败：\n{str(e)}")

    def _on_export_chapter_md(self, chapter_id: int):
        """导出单章为 Markdown。"""
        default_name = f"chapter_{chapter_id}.md"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出章节为 Markdown", default_name, "Markdown 文件 (*.md)"
        )
        if not file_path:
            return

        try:
            self._export_service.export_chapter_md(chapter_id, file_path)
            signal_bus.status_message.emit(f"章节 MD 导出成功: {file_path}")
        except Exception as e:
            logger.error(f"章节 MD 导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"章节 MD 导出失败：\n{str(e)}")

    def _on_export_volume_txt(self, volume_id: int):
        """导出分卷为 TXT。"""
        default_name = f"volume_{volume_id}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出分卷为 TXT", default_name, "文本文件 (*.txt)"
        )
        if not file_path:
            return

        try:
            self._export_service.export_volume_txt(volume_id, file_path)
            signal_bus.status_message.emit(f"分卷 TXT 导出成功: {file_path}")
        except Exception as e:
            logger.error(f"分卷 TXT 导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"分卷 TXT 导出失败：\n{str(e)}")

    def _on_export_volume_md(self, volume_id: int):
        """导出分卷为 Markdown。"""
        default_name = f"volume_{volume_id}.md"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出分卷为 Markdown", default_name, "Markdown 文件 (*.md)"
        )
        if not file_path:
            return

        try:
            self._export_service.export_volume_md(volume_id, file_path)
            signal_bus.status_message.emit(f"分卷 MD 导出成功: {file_path}")
        except Exception as e:
            logger.error(f"分卷 MD 导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"分卷 MD 导出失败：\n{str(e)}")

    # ========== 辅助方法 ==========

    def _close_chapter_tab(self, chapter_id: int):
        """关闭指定章节的标签页，更新编辑器服务中的映射。"""
        if not self._editor_service.is_open(chapter_id):
            return

        tab_idx = self._editor_service.get_tab_index(chapter_id)
        self._editor_service.unregister_editor(chapter_id)

        for cid in list(self._editor_service.get_open_chapters().keys()):
            idx, container = self._editor_service.get_open_chapters()[cid]
            if idx > tab_idx:
                self._editor_service.update_tab_index(cid, idx - 1)

        self._editor_tabs.removeTab(tab_idx)

    # ========== 章节编辑器 ==========

    def _on_tree_item_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if isinstance(data, tuple) and data[0] == "chapter":
            chapter_id = data[1]
            self._open_chapter_editor(chapter_id)

    def _open_chapter_editor(self, chapter_id: int):
        if self._editor_service.is_open(chapter_id):
            tab_index = self._editor_service.get_tab_index(chapter_id)
            self._editor_tabs.setCurrentIndex(tab_index)
            return

        chapter = self._chapter_service.get_chapter(chapter_id)
        if not chapter:
            logger.warning(f"章节不存在: {chapter_id}")
            return

        container = EditorContainer()
        editor = container.editor
        editor.set_content(chapter.content or "")
        # 从 QSettings 恢复编辑器字号
        settings = QSettings("NovelWriter", "NovelWriter")
        if settings.value("editor_font_size"):
            size = int(settings.value("editor_font_size"))
            if size > 0:
                font = editor.font()
                font.setPointSize(size)
                editor.setFont(font)
        # 应用撤销栈深度
        self._editor_service.apply_undo_depth(editor)
        # 撤销/重做按钮
        editor.undoAvailable.connect(self._undo_act.setEnabled)
        editor.redoAvailable.connect(self._redo_act.setEnabled)
        # AI 功能（右键菜单已由 EditorWidget 内置中文版）
        editor.ai_continue_requested.connect(self._on_ai_continue_write)
        editor.ai_polish_requested.connect(self._on_ai_polish)
        editor.ai_rewrite_requested.connect(self._on_ai_rewrite)
        editor.ai_analyze_requested.connect(self._on_ai_analyze)
        editor.content_changed.connect(lambda cid=chapter_id: self._on_editor_content_changed(cid))

        search_panel = container.search_panel
        search_panel.search_text_changed.connect(self._on_search_text_changed)
        search_panel.search_next.connect(self._on_search_next)
        search_panel.search_prev.connect(self._on_search_prev)
        search_panel.replace.connect(self._on_replace)
        search_panel.replace_all.connect(self._on_replace_all)
        search_panel.close_panel.connect(self._on_close_search_panel)
        search_panel.search_options_changed.connect(self._do_search)
        search_panel.in_selection_changed.connect(lambda: self._do_search())
        container.search_result_clicked.connect(self._on_search_result_clicked)

        tab_title = f"第{chapter.chapter_number}章 {chapter.title}"
        tab_index = self._editor_tabs.addTab(container, tab_title)
        self._editor_service.register_editor(chapter_id, container, tab_index)

        self._editor_tabs.setCurrentIndex(tab_index)
        self._update_status_word_count(editor)

    def _on_editor_content_changed(self, chapter_id: int):
        if not self._editor_service.is_open(chapter_id):
            return
        tab_index = self._editor_service.get_tab_index(chapter_id)
        container = self._editor_service.get_open_chapters()[chapter_id][1]
        editor = container.editor if isinstance(container, EditorContainer) else container
        tab_text = self._editor_tabs.tabText(tab_index)
        if not tab_text.endswith("*"):
            self._editor_tabs.setTabText(tab_index, tab_text + "*")
        self._update_status_word_count(editor)
        # 防抖刷新统计面板（1秒后执行，避免频繁查库）
        self._stats_debounce_timer.start(1000)

    def _on_tab_changed(self, index: int):
        if index < 0:
            self._editor_service.set_current_chapter_id(None)
            return
        for chapter_id, (tab_idx, container) in self._editor_service.get_open_chapters().items():
            if tab_idx == index:
                self._editor_service.set_current_chapter_id(chapter_id)
                editor = container.editor if isinstance(container, EditorContainer) else container
                self._update_status_word_count(editor)
                search_panel = self._get_current_search_panel()
                if search_panel and search_panel.isVisible() and search_panel.search_input.text():
                    self._do_search()
                return
        # 没有匹配的章节（例如欢迎页）
        self._editor_service.set_current_chapter_id(None)

    def _update_status_word_count(self, editor: EditorWidget):
        word_count = editor.count_words()
        para_count = editor.count_paragraphs()
        line_count = editor.blockCount()
        self._word_count_label.setText(f"字数：{word_count:,}")
        self._line_count_label.setText(f"行数：{line_count:,}")
        self._para_count_label.setText(f"段落：{para_count:,}")

    def _on_save_current(self):
        try:
            saved = self._editor_service.save_current()
            if saved:
                self._status_label.setText("已保存")
                QTimer.singleShot(3000, lambda: self._status_label.setText("就绪"))
        except Exception as e:
            logger.error(f"保存失败: {e}")
            QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")

    def _on_autosave_completed(self, saved_count: int):
        """自动保存完成后的 UI 更新。"""
        if saved_count > 0:
            self._status_label.setText("已自动保存")
            QTimer.singleShot(3000, lambda: self._status_label.setText("就绪"))

    def _on_chapter_saved(self, chapter_id: int):
        """章节保存后刷新统计。"""
        self._refresh_stats()

    def _on_general_settings_saved(self):
        """通用设置保存后的回调。"""
        self._editor_service.reload_autosave_interval()
        self._editor_service.apply_undo_depth_to_all()

    # ========== 工具方法 ==========

    def _close_editor_tab(self, index: int):
        chapter_id_to_close = None
        editor_to_close = None
        for chapter_id, (tab_idx, container) in self._editor_service.get_open_chapters().items():
            if tab_idx == index:
                chapter_id_to_close = chapter_id
                editor_to_close = container.editor if hasattr(container, 'editor') else container
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
                try:
                    self._editor_service.save_chapter(chapter_id_to_close)
                except Exception as e:
                    logger.error(f"保存章节失败: {e}")

        self._editor_service.unregister_editor(chapter_id_to_close)

        for chapter_id in list(self._editor_service.get_open_chapters().keys()):
            tab_idx, container = self._editor_service.get_open_chapters()[chapter_id]
            if tab_idx > index:
                self._editor_service.update_tab_index(chapter_id, tab_idx - 1)

        self._editor_tabs.removeTab(index)

    def _on_tab_bar_context_menu(self, pos):
        """编辑器标签页右键菜单（批量关闭）。"""
        tab_bar = self._editor_tabs.tabBar()
        tab_index = tab_bar.tabAt(pos)

        menu = QMenu(self)

        if self._editor_service.get_open_chapters():
            close_all_action = menu.addAction("关闭所有标签页")
            close_all_action.triggered.connect(self._on_close_all_tabs)

            close_others_action = menu.addAction("关闭其他标签页")
            if tab_index >= 0:
                close_others_action.triggered.connect(
                    lambda: self._on_close_other_tabs(tab_index)
                )
            else:
                close_others_action.setEnabled(False)

            menu.addSeparator()

        close_current_action = menu.addAction("关闭当前标签页")
        if tab_index >= 0:
            close_current_action.triggered.connect(
                lambda: self._close_editor_tab(tab_index)
            )
        else:
            close_current_action.setEnabled(False)

        menu.exec(tab_bar.mapToGlobal(pos))

    def _on_close_all_tabs(self):
        """关闭所有编辑器标签页。"""
        # 检查是否有未保存的更改
        open_chapters = self._editor_service.get_open_chapters()
        unsaved = [ch_id for ch_id, (_, container) in open_chapters.items()
                   if (container.editor if hasattr(container, 'editor') else container).is_modified()]
        if unsaved:
            reply = QMessageBox.question(
                self, "未保存的更改",
                f"有 {len(unsaved)} 个标签页未保存，是否全部保存？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Save:
                for ch_id in unsaved:
                    try:
                        self._editor_service.save_chapter(ch_id)
                    except Exception as e:
                        logger.error(f"保存章节 {ch_id} 失败: {e}")

        self._editor_service.close_all_editors()
        # 保留欢迎页
        self._editor_tabs.clear()
        self._show_welcome_page()

    def _on_close_other_tabs(self, keep_index: int):
        """关闭除指定标签页外的所有标签页。"""
        open_chapters = self._editor_service.get_open_chapters()
        # 收集要保留的 chapter_id
        keep_chapter_id = None
        for ch_id, (tab_idx, _) in open_chapters.items():
            if tab_idx == keep_index:
                keep_chapter_id = ch_id
                break

        # 从后往前关闭，避免索引变化
        tab_indices = sorted(
            [tab_idx for ch_id, (tab_idx, _) in open_chapters.items()
             if tab_idx != keep_index],
            reverse=True,
        )
        for idx in tab_indices:
            self._editor_tabs.removeTab(idx)

        # 重建 EditorService 中的映射（只保留保留的章节）
        self._editor_service.close_all_editors()
        if keep_chapter_id is not None:
            container = open_chapters[keep_chapter_id][1]
            self._editor_service.register_editor(keep_chapter_id, container, 0)

    def _switch_theme(self, theme: str):
        app = QApplication.instance()
        style_manager.apply_theme(app, theme)
        signal_bus.theme_changed.emit(theme)
        # 持久化保存主题设置（到 app_config 表）
        from services.app_config_service import app_config_service
        app_config_service.set("theme", theme)

    def _on_status_message(self, message: str):
        self._status_label.setText(message)
        QTimer.singleShot(3000, lambda: self._status_label.setText("就绪"))

    def _on_project_opened(self, project_id: int):
        self._editor_service.close_all_editors()
        if self._editor_tabs.count() == 1 and self._editor_tabs.tabText(0) == "欢迎":
            self._editor_tabs.removeTab(0)
        self._current_project_id = project_id
        self._load_project_tree(project_id)
        self._refresh_outline()
        self._refresh_stats()
        # 更新状态栏：项目名称
        project_name = self._get_project_name(project_id)
        self._project_name_label.setText(project_name)
        # 更新状态栏：AI 提供商
        self._update_ai_provider_label()

    def _on_word_count_updated(self, count: int):
        self._word_count_label.setText(f"字数：{count:,}")

    def _show_about(self):
        QMessageBox.about(self, "关于 Novel Writer",
            "Novel Writer v0.1.0\n\n"
            "AI 原生小说创作桌面系统\n"
            "基于 PySide6 构建\n\n"
            "© 2026 Novel Writer Team"
        )

    # ========== 视图菜单占位方法 ==========

    def _on_focus_mode(self):
        """切换专注模式：隐藏所有面板，仅保留编辑器+状态栏。"""
        if not hasattr(self, '_focus_mode_active'):
            self._focus_mode_active = False

        if not self._focus_mode_active:
            # 保存当前布局状态
            self._focus_saved_state = []
            # 保存各元素可见性
            for elem in [self.menuBar(), self._project_dock, self._sidebar_dock,
                         self.findChild(QToolBar, "主工具栏")]:
                if elem:
                    self._focus_saved_state.append((elem, elem.isVisible()))
                    elem.setVisible(False)
            self._focus_mode_active = True
            signal_bus.status_message.emit("专注模式已开启")
        else:
            # 恢复布局
            for elem, visible in self._focus_saved_state:
                if elem:
                    elem.setVisible(visible)
            self._focus_mode_active = False
            signal_bus.status_message.emit("专注模式已关闭")

    def _on_toggle_left_panel(self):
        """切换左侧栏（项目树）的显示状态。"""
        visible = self._project_dock.isVisible()
        self._project_dock.setVisible(not visible)

    def _on_toggle_right_panel(self):
        """切换右侧栏的显示状态。"""
        visible = self._sidebar_dock.isVisible()
        self._sidebar_dock.setVisible(not visible)

    def _on_toggle_bottom_panel(self):
        """切换底部面板的显示状态。"""
        signal_bus.status_message.emit("功能开发中: 底部面板")

    def _on_zoom_in(self):
        """放大编辑器字体。"""
        editor = self._get_current_editor()
        if editor is None:
            return
        font = editor.font()
        current_size = font.pointSize()
        if current_size < 0:
            current_size = 16
        font.setPointSize(current_size + 2)
        editor.setFont(font)
        settings = QSettings("NovelWriter", "NovelWriter")
        settings.setValue("editor_font_size", current_size + 2)
        signal_bus.status_message.emit(f"字体大小: {current_size + 2}pt")

    def _on_zoom_out(self):
        """缩小编辑器字体。"""
        editor = self._get_current_editor()
        if editor is None:
            return
        font = editor.font()
        current_size = font.pointSize()
        if current_size < 0:
            current_size = 16
        if current_size > 8:
            font.setPointSize(current_size - 2)
            editor.setFont(font)
            settings = QSettings("NovelWriter", "NovelWriter")
            settings.setValue("editor_font_size", current_size - 2)
            signal_bus.status_message.emit(f"字体大小: {current_size - 2}pt")
        else:
            signal_bus.status_message.emit("已达到最小字体")

    def _on_zoom_reset(self):
        """重置编辑器字体到默认大小。"""
        editor = self._get_current_editor()
        if editor is None:
            return
        font = editor.font()
        font.setPointSize(16)
        editor.setFont(font)
        settings = QSettings("NovelWriter", "NovelWriter")
        settings.setValue("editor_font_size", 16)
        signal_bus.status_message.emit("字体大小: 已重置")

    # ========== 全局快捷键占位方法 ==========

    def _on_close_current_tab(self):
        """关闭当前标签页（Ctrl+W）。"""
        current = self._editor_tabs.currentIndex()
        if current >= 0:
            self._close_editor_tab(current)

    def _on_save_all(self):
        """全部保存（Ctrl+Shift+S）。"""
        saved = self._editor_service.save_all()
        if saved > 0:
            self._status_label.setText(f"已保存全部 {saved} 个章节")
            QTimer.singleShot(3000, lambda: self._status_label.setText("就绪"))

    def _on_generate_dialogue(self):
        """AI 对话生成（Ctrl+Shift+D）。"""
        signal_bus.status_message.emit("AI 对话生成功能开发中")

    def _on_show_shortcuts(self):
        """显示快捷键参考（Ctrl+/）。"""
        shortcuts = [
            ("Ctrl+N", "新建项目"),
            ("Ctrl+O", "打开项目"),
            ("Ctrl+S", "保存当前章节"),
            ("Ctrl+Shift+S", "全部保存"),
            ("Ctrl+W", "关闭标签页"),
            ("Ctrl+Q", "退出"),
            ("Ctrl+Z/Y", "撤销/重做"),
            ("Ctrl+F", "搜索"),
            ("Ctrl+H", "替换"),
            ("Ctrl+I", "AI 续写"),
            ("Ctrl+Shift+P", "AI 润色"),
            ("Ctrl+Shift+A", "AI 分析"),
            ("Ctrl+Shift+L/R", "切换左侧栏/右侧栏"),
            ("F11", "专注模式"),
        ]
        text = "\n".join(f"{k:20s} {v}" for k, v in shortcuts)
        QMessageBox.information(self, "快捷键参考", text)

    # ========== 写作菜单占位方法 ==========

    def _on_creative_wizard(self):
        """打开七步法创作向导。"""
        wizard = CreativeWizard(self)
        wizard.exec()

    def _on_constitution(self):
        """创作宪法（七步法第1步）。"""
        signal_bus.status_message.emit("功能开发中: 创作宪法")

    def _on_specify(self):
        """故事规格（七步法第2步）。"""
        signal_bus.status_message.emit("功能开发中: 故事规格")

    def _on_clarify(self):
        """决策澄清（七步法第3步）。"""
        signal_bus.status_message.emit("功能开发中: 决策澄清")

    def _on_plan(self):
        """创作计划（七步法第4步）。"""
        signal_bus.status_message.emit("功能开发中: 创作计划")

    def _on_tasks(self):
        """任务分解（七步法第5步）。"""
        signal_bus.status_message.emit("功能开发中: 任务分解")

    def _on_writing_quality_analysis(self):
        """质量分析（七步法第7步）。"""
        signal_bus.status_message.emit("功能开发中: 质量分析")

    def _on_writing_ai_audit(self):
        """AI 审计。"""
        signal_bus.status_message.emit("功能开发中: AI 审计")

    # ========== AI 菜单占位方法 ==========

    def _on_toggle_ai_chat(self):
        """切换底部 AI 对话面板。"""
        visible = not self._ai_chat_dock.isVisible()
        self._ai_chat_dock.setVisible(visible)
        if visible:
            signal_bus.status_message.emit("AI 对话面板已打开")

    def _on_ai_switch_model(self, model_name: str):
        """切换 AI 模型。"""
        signal_bus.status_message.emit(f"功能开发中: 切换模型 - {model_name}")

    def _on_ai_expert_mode(self, expert_type: str):
        """AI 专家模式。"""
        signal_bus.status_message.emit(f"功能开发中: 专家模式 - {expert_type}")

    # ========== 追踪菜单占位方法 ==========

    def _on_tracking_panel(self):
        """打开综合追踪面板。"""
        signal_bus.status_message.emit("功能开发中: 综合追踪面板")

    def _on_plot_check(self):
        """情节检查 - 切换到情节面板。"""
        self._sidebar_tabs.setCurrentWidget(self._plot_panel)
        signal_bus.status_message.emit("情节检查")

    def _on_timeline_management(self):
        """时间线管理 - 切换到时间线面板。"""
        self._sidebar_tabs.setCurrentWidget(self._timeline_panel)
        signal_bus.status_message.emit("时间线管理")

    def _on_relationship_graph(self):
        """关系图谱 - 切换到关系面板。"""
        self._sidebar_tabs.setCurrentWidget(self._relationship_panel)
        signal_bus.status_message.emit("关系图谱")

    def _on_consistency_check(self):
        """一致性检查 - 切换到检查面板。"""
        self._sidebar_tabs.setCurrentWidget(self._check_panel)
        signal_bus.status_message.emit("一致性检查")

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
            try:
                if not db_manager.is_project_open:
                    return
                session = db_manager.get_project_session()

                chapters = session.query(Chapter).filter_by(
                    is_deleted=False
                ).all()

                total_words = sum(ch.word_count or 0 for ch in chapters)
                chapter_count = len(chapters)
                volume_count = session.query(Volume).count()

                avg_chars_per_chapter = 0
                if chapter_count > 0:
                    avg_chars_per_chapter = int(total_words / chapter_count)

                stats = {
                    "total_words": total_words,
                    "chapter_count": chapter_count,
                    "volume_count": volume_count,
                    "avg_chars_per_chapter": avg_chars_per_chapter,
                }

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

            p_session = db_manager.get_project_session()
            try:
                volumes = p_session.query(Volume).order_by(Volume.volume_number).all()
                for v in volumes:
                    vol_item = QTreeWidgetItem([v.title])
                    vol_item.setData(0, Qt.UserRole, ("volume", v.id))
                    root.addChild(vol_item)

                    chapters = p_session.query(Chapter).filter_by(
                        volume_id=v.id, is_deleted=False
                    ).order_by(Chapter.chapter_number).all()
                    for ch in chapters:
                        ch_item = QTreeWidgetItem([f"第{ch.chapter_number}章 {ch.title}"])
                        ch_item.setData(0, Qt.UserRole, ("chapter", ch.id))
                        vol_item.addChild(ch_item)
            finally:
                p_session.close()

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
                db_manager.open_project(project.path)
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

        # 将提示条插入到编辑器标签页下方
        central_layout = self.centralWidget().layout()
        # central_layout 中只有 _editor_tabs (index 0)，搜索面板在每个 EditorContainer 内部
        central_layout.addWidget(toast)

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
        for chapter_id, (tab_idx, _) in list(self._editor_service.get_open_chapters().items()):
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

    def _get_current_container(self):
        """获取当前标签页的 EditorContainer。"""
        return self._editor_service.get_current_container()

    def _get_current_search_panel(self):
        container = self._editor_service.get_current_container()
        return container.search_panel if container and hasattr(container, 'search_panel') else None

    def _toggle_search_panel(self):
        container = self._get_current_container()
        if not container:
            return
        search_panel = container.search_panel
        if search_panel.isVisible():
            self._on_close_search_panel()
        else:
            editor = container.editor
            # 通过 show_search 打开，确保正确定位到右上角
            container.show_search()
            has_selection = editor.textCursor().hasSelection()
            search_panel.set_selection_available(has_selection)
            selected_text = editor.textCursor().selectedText()
            if selected_text:
                search_panel.set_search_text(selected_text)
                self._do_search()
            else:
                keyword = search_panel.search_input.text()
                if keyword:
                    self._do_search()

    def _get_current_editor(self):
        return self._editor_service.get_current_editor()

    def _on_search_text_changed(self, keyword: str):
        self._do_search()

    def _do_search(self):
        """执行搜索并高亮结果。"""
        editor = self._get_current_editor()
        search_panel = self._get_current_search_panel()
        if not editor or not search_panel:
            return

        keyword = search_panel.search_input.text()
        self._current_search_keyword = keyword

        if not keyword:
            self._clear_all_highlights()
            self._current_matches = []
            self._current_match_index = -1
            search_panel.set_match_count(0, 0)
            return

        self._highlight_matches(editor, keyword, search_panel)

    def _highlight_matches(self, editor: EditorWidget, keyword: str, search_panel):
        self._clear_all_highlights()
        self._current_matches = []
        self._current_match_index = -1

        if not keyword:
            search_panel.set_match_count(0, 0)
            return

        sel_start = -1
        sel_end = -1
        if search_panel.in_selection:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                sel_start = cursor.selectionStart()
                sel_end = cursor.selectionEnd()

        # 构建查找参数
        if search_panel.use_regex:
            # 正则表达式匹配
            try:
                options = QRegularExpression.NoPatternOption if search_panel.case_sensitive else QRegularExpression.CaseInsensitiveOption
                pattern = QRegularExpression(keyword, options)
                if not pattern.isValid():
                    search_panel.match_label.setText("正则错误")
                    search_panel.match_label.setStyleSheet("color: #f7768e;")
                    return
            except Exception:
                search_panel.set_match_count(0, 0)
                return

            doc = editor.document()
            cursor = QTextCursor(doc)
            if sel_start >= 0:
                cursor.setPosition(sel_start)
            while True:
                cursor = doc.find(pattern, cursor)
                if cursor.isNull():
                    break
                match_start = cursor.selectionStart()
                match_end = cursor.selectionEnd()
                if sel_start >= 0 and (match_start < sel_start or match_end > sel_end):
                    if match_start > sel_end:
                        break
                    continue
                self._current_matches.append((match_start, match_end))
        else:
            # 普通文本匹配
            flags = QTextDocument.FindFlag(0)
            if search_panel.case_sensitive:
                flags |= QTextDocument.FindFlag.FindCaseSensitively
            if search_panel.whole_word:
                flags |= QTextDocument.FindFlag.FindWholeWords
            if search_panel.search_backward:
                flags |= QTextDocument.FindFlag.FindBackward

            doc = editor.document()
            cursor = QTextCursor(doc)
            if sel_start >= 0:
                cursor.setPosition(sel_end if search_panel.search_backward else sel_start)
            else:
                # 反向查找：从光标当前位置开始向后
                ec = editor.textCursor()
                if search_panel.search_backward:
                    cursor.setPosition(ec.selectionStart())
            while True:
                cursor = doc.find(keyword, cursor, flags)
                if cursor.isNull():
                    break
                match_start = cursor.selectionStart()
                match_end = cursor.selectionEnd()
                if sel_start >= 0 and (match_start < sel_start or match_end > sel_end):
                    if match_start > sel_end:
                        break
                    continue
                self._current_matches.append((match_start, match_end))
                if search_panel.search_backward and cursor.atStart():
                    break

        # 设置高亮
        self._update_highlights(editor)

        # 更新搜索结果列表
        container = self._get_current_container()
        if container:
            container.update_search_results(self._current_matches, editor)

        total = len(self._current_matches)
        if total > 0:
            self._current_match_index = 0
            self._goto_match(0, editor)
        search_panel.set_match_count(self._current_match_index + 1 if total > 0 else 0, total)

    def _update_highlights(self, editor: EditorWidget):
        """更新编辑器高亮：所有匹配项浅色，当前匹配项突出色。"""
        extra_selections = []

        # 所有匹配项 - 浅色背景
        all_format = QTextCharFormat()
        all_format.setBackground(QBrush(QColor(255, 220, 0, 60)))

        for i, (start, end) in enumerate(self._current_matches):
            sel = QTextEdit.ExtraSelection()
            sel.cursor = QTextCursor(editor.document())
            sel.cursor.setPosition(start)
            sel.cursor.setPosition(end, QTextCursor.KeepAnchor)
            sel.format = all_format
            extra_selections.append(sel)

        # 当前匹配项 - 突出色
        if 0 <= self._current_match_index < len(self._current_matches):
            current_format = QTextCharFormat()
            current_format.setBackground(QBrush(QColor("#f0c674")))

            start, end = self._current_matches[self._current_match_index]
            sel = QTextEdit.ExtraSelection()
            sel.cursor = QTextCursor(editor.document())
            sel.cursor.setPosition(start)
            sel.cursor.setPosition(end, QTextCursor.KeepAnchor)
            sel.format = current_format
            extra_selections.append(sel)

        editor.setExtraSelections(extra_selections)

    def _clear_all_highlights(self):
        """清除所有打开的编辑器的高亮。"""
        for chapter_id, (tab_idx, container) in self._editor_service.get_open_chapters().items():
            editor = container.editor if hasattr(container, 'editor') else container
            if hasattr(editor, 'setExtraSelections'):
                editor.setExtraSelections([])

    def _on_search_next(self):
        if not self._current_matches:
            self._do_search()
            return
        editor = self._get_current_editor()
        search_panel = self._get_current_search_panel()
        if not editor or not search_panel:
            return
        self._current_match_index = (self._current_match_index + 1) % len(self._current_matches)
        self._goto_match(self._current_match_index, editor)
        search_panel.set_match_count(self._current_match_index + 1, len(self._current_matches))

    def _on_search_prev(self):
        if not self._current_matches:
            self._do_search()
            return
        editor = self._get_current_editor()
        search_panel = self._get_current_search_panel()
        if not editor or not search_panel:
            return
        self._current_match_index = (self._current_match_index - 1) % len(self._current_matches)
        self._goto_match(self._current_match_index, editor)
        search_panel.set_match_count(self._current_match_index + 1, len(self._current_matches))

    def _goto_match(self, index: int, editor: EditorWidget):
        if index < 0 or index >= len(self._current_matches):
            return
        start, end = self._current_matches[index]
        cursor = QTextCursor(editor.document())
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        editor.setTextCursor(cursor)
        editor.ensureCursorVisible()
        # 更新高亮以突出当前匹配
        self._update_highlights(editor)

    def _on_search_result_clicked(self, match_index: int):
        """点击搜索结果列表项时跳转到对应位置。"""
        editor = self._get_current_editor()
        search_panel = self._get_current_search_panel()
        if not editor or not search_panel:
            return
        if 0 <= match_index < len(self._current_matches):
            self._current_match_index = match_index
            self._goto_match(match_index, editor)
            search_panel.set_match_count(match_index + 1, len(self._current_matches))

    def _apply_preserve_case(self, original: str, replacement: str) -> str:
        """根据原文本的大小写模式调整替换文本的大小写。"""
        if not original or not replacement:
            return replacement

        if original.isupper():
            return replacement.upper()
        elif original.islower():
            return replacement.lower()
        elif original[0].isupper() and original[1:].islower():
            if len(replacement) > 0:
                return replacement[0].upper() + replacement[1:].lower()
            return replacement
        elif original.istitle():
            return replacement.title()
        return replacement

    def _on_replace(self, search_text: str, replace_text: str):
        editor = self._get_current_editor()
        search_panel = self._get_current_search_panel()
        if not editor or not search_text:
            return

        if not self._current_matches:
            self._do_search()
            if not self._current_matches:
                return

        if self._current_match_index < 0:
            self._current_match_index = 0

        start, end = self._current_matches[self._current_match_index]
        cursor = QTextCursor(editor.document())
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        original_text = cursor.selectedText()

        final_replace_text = replace_text
        if search_panel and search_panel.preserve_case:
            final_replace_text = self._apply_preserve_case(original_text, replace_text)

        editor.setTextCursor(cursor)
        cursor.insertText(final_replace_text)

        editor.content_changed.emit()
        self._do_search()

    def _on_replace_all(self, search_text: str, replace_text: str):
        editor = self._get_current_editor()
        search_panel = self._get_current_search_panel()
        if not editor or not search_text:
            return

        if not search_panel or not search_panel.preserve_case:
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
        else:
            if not self._current_matches:
                self._do_search()
            if not self._current_matches:
                return

            cursor = QTextCursor(editor.document())
            cursor.beginEditBlock()
            for i in range(len(self._current_matches) - 1, -1, -1):
                start, end = self._current_matches[i]
                sel_cursor = QTextCursor(editor.document())
                sel_cursor.setPosition(start)
                sel_cursor.setPosition(end, QTextCursor.KeepAnchor)
                original_text = sel_cursor.selectedText()
                final_replace_text = self._apply_preserve_case(original_text, replace_text)
                sel_cursor.insertText(final_replace_text)
            cursor.endEditBlock()

            editor._modified = True
            editor.content_changed.emit()
            self._do_search()

    def _on_close_search_panel(self):
        container = self._get_current_container()
        if container:
            container.hide_search()
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
        current_cid = self._editor_service.get_current_chapter_id()
        # 获取当前章节
        if not current_cid:
            if self._ai_panel is not None:
                self._ai_panel.set_status("请先打开一个章节")
            return

        try:
            # 创建 AIWorker
            worker = self._ai_service.continue_writing(
                current_cid, self._current_project_id,
                max_tokens=word_count
            )

            # 连接信号
            worker.chunk_received.connect(self._on_ai_chunk_received)
            worker.finished_signal.connect(self._on_ai_finished)
            worker.error_signal.connect(self._on_ai_error)
            worker.retry_signal.connect(self._on_ai_retry)

            # 保存引用防止 GC
            self._ai_worker = worker
            self._ai_target_chapter_id = current_cid

            # 设置 UI 状态
            self._ai_panel.set_generating(True)
            self._ai_panel.set_status("正在生成...")

            # 设置编辑器只读
            editor = self._editor_service.get_editor(current_cid)
            if editor:
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
        cid = self._ai_target_chapter_id or self._editor_service.get_current_chapter_id()
        editor = self._editor_service.get_editor(cid) if cid else None
        if editor:
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text)
            editor.setTextCursor(cursor)
            editor.ensureCursorVisible()

        # 更新信号总线
        signal_bus.ai_chunk_received.emit(text)

    def _on_ai_finished(self, full_text: str):
        """AI 生成完成。"""
        cid = self._ai_target_chapter_id or self._editor_service.get_current_chapter_id()
        # 恢复编辑器
        if cid and self._editor_service.is_open(cid):
            tab_idx = self._editor_service.get_tab_index(cid)
            editor = self._editor_service.get_editor(cid)
            if editor:
                editor.setReadOnly(False)
                # 标记为已修改
                editor.set_modified(True)
                editor.document().setModified(True)
            # 在标签页标题添加 * 标记
            if tab_idx is not None:
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
        cid = self._ai_target_chapter_id or self._editor_service.get_current_chapter_id()
        # 恢复编辑器
        if cid and self._editor_service.is_open(cid):
            editor = self._editor_service.get_editor(cid)
            if editor:
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

    def _on_app_settings(self):
        """打开应用设置对话框。"""
        from ui.dialogs.app_settings_dialog import AppSettingsDialog
        dialog = AppSettingsDialog(self)
        dialog.exec()

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
            worker = self._ai_service.polish_text(selected, "简洁")
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
            worker = self._ai_service.rewrite_text(selected, "扩写")
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
            worker = self._ai_service.analyze_chapter(content, "")
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

    # ========== TXT/MD 导入 ==========

    def _on_import_txt(self):
        """从 TXT/MD 文件导入全本。"""
        if not self._current_project_id:
            QMessageBox.information(self, "提示", "请先打开一个项目")
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 TXT/MD 文件", "", "文本文件 (*.txt *.md);;所有文件 (*)"
        )
        if not file_path:
            return

        try:
            sections = self._txt_import_service.split_full_book(file_path)
            if not sections:
                QMessageBox.information(self, "提示", "未能识别任何章节内容")
                return

            dialog = ImportPreviewDialog(sections, self._current_project_id, self)
            if dialog.exec() == QDialog.Accepted:
                volume_id = dialog.get_target_volume_id()
                target_name = dialog.get_new_volume_name() if volume_id is None else None
                result = self._txt_import_service.import_full_book(
                    file_path, self._current_project_id,
                    volume_id=volume_id, target_name=target_name
                )
                QMessageBox.information(
                    self, "导入完成",
                    f"成功导入 {result['success']} 个章节"
                )
                self._reload_project_tree()
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))

    def _reload_project_tree(self):
        """刷新项目树（无参数版本）。"""
        if self._current_project_id:
            self._load_project_tree(self._current_project_id)

    def _on_import_epub(self):
        """从 EPUB 文件导入全本。"""
        if not self._current_project_id:
            QMessageBox.information(self, "提示", "请先打开一个项目")
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 EPUB 文件", "", "EPUB 电子书 (*.epub);;所有文件 (*)"
        )
        if not file_path:
            return

        try:
            sections = EpubImportService._parse_epub(file_path)
            if not sections:
                QMessageBox.information(self, "提示", "未能识别任何章节内容")
                return

            dialog = ImportPreviewDialog(sections, self._current_project_id, self)
            if dialog.exec() == QDialog.Accepted:
                volume_id = dialog.get_target_volume_id()
                target_name = dialog.get_new_volume_name() if volume_id is None else None
                result = EpubImportService.import_epub_full_book(
                    file_path, self._current_project_id,
                    volume_id=volume_id, target_name=target_name
                )
                QMessageBox.information(
                    self, "导入完成",
                    f"成功导入 {result['success']} 个章节"
                )
                self._reload_project_tree()
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))

    def _on_import_pdf(self):
        """从 PDF 文件导入全本。"""
        if not self._current_project_id:
            QMessageBox.information(self, "提示", "请先打开一个项目")
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 PDF 文件", "", "PDF 文件 (*.pdf);;所有文件 (*)"
        )
        if not file_path:
            return

        try:
            sections = PdfImportService._parse_pdf(file_path)
            if not sections:
                QMessageBox.information(self, "提示", "未能识别任何章节内容")
                return

            dialog = ImportPreviewDialog(sections, self._current_project_id, self)
            if dialog.exec() == QDialog.Accepted:
                volume_id = dialog.get_target_volume_id()
                target_name = dialog.get_new_volume_name() if volume_id is None else None
                result = PdfImportService.import_pdf_full_book(
                    file_path, self._current_project_id,
                    volume_id=volume_id, target_name=target_name
                )
                QMessageBox.information(
                    self, "导入完成",
                    f"成功导入 {result['success']} 个章节"
                )
                self._reload_project_tree()
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))

    def _on_import_chapter_file(self, chapter_id: int):
        """从文件导入替换单章内容。"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "文本文件 (*.txt *.md);;所有文件 (*)"
        )
        if not file_path:
            return

        try:
            chapter = self._txt_import_service.import_chapter_from_file(file_path, chapter_id)
            # 刷新编辑器
            editor = self._editor_service.get_editor(chapter_id)
            if editor:
                editor.set_content(chapter.content or "")
                editor.set_modified(False)
                # 更新状态栏
                wc = editor.count_words()
                pc = editor.count_paragraphs()
                signal_bus.status_message.emit(f"已导入: {wc} 字, {pc} 段")
            signal_bus.word_count_updated.emit()
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))

    def _on_import_volume_dir(self, volume_id: int):
        """从文件夹批量导入章节到分卷。"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择包含章节文件的文件夹")
        if not dir_path:
            return

        try:
            result = self._txt_import_service.import_volume_from_dir(dir_path, volume_id)
            msg = f"成功导入 {result['success']} 个章节"
            if result['skipped'] > 0:
                msg += f"\n跳过 {result['skipped']} 个文件"
            QMessageBox.information(self, "导入完成", msg)
            self._reload_project_tree()
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))

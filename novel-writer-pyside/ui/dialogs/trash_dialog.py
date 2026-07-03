"""回收站对话框 — 查看和恢复软删除的章节/分卷/项目。"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
    QMessageBox, QWidget, QAbstractItemView,
)
from PySide6.QtCore import Qt

from models import db_manager, Project, Volume, Chapter
from services.chapter_service import ChapterService
from services.project_service import ProjectService
from utils.logger import logger


class TrashDialog(QDialog):
    """回收站对话框 - 管理已删除的章节、分卷和已归档的项目。"""

    TAB_VOLUME = 0
    TAB_CHAPTER = 1
    TAB_PROJECT = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._chapter_service = ChapterService()
        self._project_service = ProjectService()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        self.setWindowTitle("回收站")
        self.setMinimumSize(720, 460)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 说明
        hint = QLabel(
            "已删除的分卷/章节和已归档的项目会出现在这里。"
            "选中后可以恢复或彻底删除。"
        )
        hint.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(hint)

        # 标签页
        self._tabs = QTabWidget()
        self._tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self._tabs)

        # tab 0：已删除的分卷
        self._volume_tab = QWidget()
        self._tabs.addTab(self._volume_tab, "已删除的分卷")
        self._init_volume_tab()

        # tab 1：已删除的章节
        self._chapter_tab = QWidget()
        self._tabs.addTab(self._chapter_tab, "已删除的章节")
        self._init_chapter_tab()

        # tab 2：已归档的项目
        self._project_tab = QWidget()
        self._tabs.addTab(self._project_tab, "已归档的项目")
        self._init_project_tab()

        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self._restore_btn = QPushButton("恢复选中项")
        self._restore_btn.setMinimumWidth(100)
        self._restore_btn.clicked.connect(self._on_restore)
        btn_layout.addWidget(self._restore_btn)

        self._delete_btn = QPushButton("彻底删除选中项")
        self._delete_btn.setMinimumWidth(100)
        self._delete_btn.setStyleSheet("color: #e06c75;")
        self._delete_btn.clicked.connect(self._on_hard_delete)
        btn_layout.addWidget(self._delete_btn)

        self._empty_btn = QPushButton("清空回收站")
        self._empty_btn.setMinimumWidth(100)
        self._empty_btn.setStyleSheet("color: #e06c75;")
        self._empty_btn.clicked.connect(self._on_empty_trash)
        btn_layout.addWidget(self._empty_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setMinimumWidth(80)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _init_volume_tab(self):
        layout = QVBoxLayout(self._volume_tab)
        self._vol_table = QTableWidget(0, 4)
        self._vol_table.setHorizontalHeaderLabels(["ID", "分卷名称", "所属项目", "删除时间"])
        self._vol_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._vol_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._vol_table.horizontalHeader().setStretchLastSection(True)
        self._vol_table.setColumnWidth(0, 50)
        self._vol_table.setColumnWidth(1, 200)
        self._vol_table.setColumnWidth(2, 150)
        self._vol_table.verticalHeader().hide()
        self._vol_table.setAlternatingRowColors(True)
        self._vol_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._vol_table.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(self._vol_table)

    def _init_chapter_tab(self):
        layout = QVBoxLayout(self._chapter_tab)
        self._ch_table = QTableWidget(0, 5)
        self._ch_table.setHorizontalHeaderLabels(["ID", "章节标题", "所属分卷", "所属项目", "删除时间"])
        self._ch_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._ch_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._ch_table.horizontalHeader().setStretchLastSection(True)
        self._ch_table.setColumnWidth(0, 50)
        self._ch_table.setColumnWidth(1, 200)
        self._ch_table.setColumnWidth(2, 120)
        self._ch_table.setColumnWidth(3, 120)
        self._ch_table.verticalHeader().hide()
        self._ch_table.setAlternatingRowColors(True)
        self._ch_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._ch_table.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(self._ch_table)

    def _init_project_tab(self):
        layout = QVBoxLayout(self._project_tab)
        self._pj_table = QTableWidget(0, 4)
        self._pj_table.setHorizontalHeaderLabels(["ID", "项目名称", "类型", "归档时间"])
        self._pj_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._pj_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._pj_table.horizontalHeader().setStretchLastSection(True)
        self._pj_table.setColumnWidth(0, 50)
        self._pj_table.setColumnWidth(1, 200)
        self._pj_table.setColumnWidth(2, 100)
        self._pj_table.verticalHeader().hide()
        self._pj_table.setAlternatingRowColors(True)
        self._pj_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._pj_table.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(self._pj_table)

    def _on_tab_changed(self, index: int):
        """标签页切换时更新按钮状态。"""
        pass  # 按钮始终可用

    def _load_data(self):
        """加载回收站数据。"""
        self._load_volumes()
        self._load_chapters()
        self._load_projects()

    def _load_volumes(self):
        """加载已删除的分卷。"""
        volumes = self._chapter_service.list_deleted_volumes()
        self._vol_table.setRowCount(len(volumes))
        for row, v in enumerate(volumes):
            self._vol_table.setItem(row, 0, QTableWidgetItem(str(v.id)))
            self._vol_table.setItem(row, 1, QTableWidgetItem(v.title))
            self._vol_table.setItem(row, 2, QTableWidgetItem("—"))
            deleted_at = v.deleted_at.strftime("%Y-%m-%d %H:%M") if v.deleted_at else ""
            self._vol_table.setItem(row, 3, QTableWidgetItem(deleted_at))
        self._tabs.setTabText(self.TAB_VOLUME, f"已删除的分卷 ({len(volumes)})")

    def _load_chapters(self):
        """加载已删除的章节（不包含已删除分卷下的章节，它们随分卷一起恢复/删除）。"""
        chapters = self._chapter_service.list_deleted_chapters()
        self._ch_table.setRowCount(len(chapters))
        session = db_manager.get_session()
        try:
            for row, ch in enumerate(chapters):
                self._ch_table.setItem(row, 0, QTableWidgetItem(str(ch.id)))
                title = f"第{ch.chapter_number}章 {ch.title}" if ch.title else f"第{ch.chapter_number}章"
                self._ch_table.setItem(row, 1, QTableWidgetItem(title))
                # 所属分卷名
                vol = session.query(Volume).filter_by(id=ch.volume_id).first()
                vname = vol.name if vol else f"(分卷 {ch.volume_id})"
                self._ch_table.setItem(row, 2, QTableWidgetItem(vname))
                self._ch_table.setItem(row, 3, QTableWidgetItem("—"))
                deleted_at = ch.deleted_at.strftime("%Y-%m-%d %H:%M") if ch.deleted_at else ""
                self._ch_table.setItem(row, 4, QTableWidgetItem(deleted_at))
        finally:
            session.close()
        self._tabs.setTabText(self.TAB_CHAPTER, f"已删除的章节 ({len(chapters)})")

    def _load_projects(self):
        """加载已归档的项目。"""
        projects = self._project_service.list_archived_projects()
        self._pj_table.setRowCount(len(projects))
        for row, p in enumerate(projects):
            self._pj_table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self._pj_table.setItem(row, 1, QTableWidgetItem(p.name))
            self._pj_table.setItem(row, 2, QTableWidgetItem(p.genre or ""))
            archived_at = p.updated_at.strftime("%Y-%m-%d %H:%M") if p.updated_at else ""
            self._pj_table.setItem(row, 3, QTableWidgetItem(archived_at))
        self._tabs.setTabText(self.TAB_PROJECT, f"已归档的项目 ({len(projects)})")

    def _get_selected_ids(self, table, col=0) -> list[int]:
        """从表格获取选中的 ID 列表（去重）。"""
        ids = []
        for item in table.selectedItems():
            if item.column() == col:
                try:
                    ids.append(int(item.text()))
                except ValueError:
                    pass
        # 去重
        return list(dict.fromkeys(ids))

    def _current_table(self):
        """返回当前标签页对应的表格控件。"""
        idx = self._tabs.currentIndex()
        if idx == self.TAB_VOLUME:
            return self._vol_table
        elif idx == self.TAB_CHAPTER:
            return self._ch_table
        elif idx == self.TAB_PROJECT:
            return self._pj_table
        return None

    def _on_restore(self):
        """恢复选中项。"""
        current_tab = self._tabs.currentIndex()
        restored = 0

        if current_tab == self.TAB_VOLUME:
            ids = self._get_selected_ids(self._vol_table)
            for vid in ids:
                count = self._chapter_service.restore_volume(vid)
                if count >= 0:
                    restored += 1
        elif current_tab == self.TAB_CHAPTER:
            ids = self._get_selected_ids(self._ch_table)
            for ch_id in ids:
                if self._chapter_service.restore_chapter(ch_id):
                    restored += 1
        elif current_tab == self.TAB_PROJECT:
            ids = self._get_selected_ids(self._pj_table)
            for pj_id in ids:
                if self._project_service.restore_project(pj_id):
                    restored += 1

        if restored > 0:
            self._load_data()
            logger.info(f"回收站: 恢复 {restored} 项")
        else:
            table = self._current_table()
            if table and table.rowCount() == 0:
                QMessageBox.information(self, "提示", "当前标签页没有可恢复的项")
            else:
                QMessageBox.information(self, "提示", "请先选中要恢复的项")

    def _on_hard_delete(self):
        """彻底删除选中项。"""
        current_tab = self._tabs.currentIndex()
        ids = []
        label = ""

        if current_tab == self.TAB_VOLUME:
            ids = self._get_selected_ids(self._vol_table)
            label = f"{len(ids)} 个分卷（含其下所有章节）"
        elif current_tab == self.TAB_CHAPTER:
            ids = self._get_selected_ids(self._ch_table)
            label = f"{len(ids)} 个章节"
        elif current_tab == self.TAB_PROJECT:
            ids = self._get_selected_ids(self._pj_table)
            label = f"{len(ids)} 个项目"

        if not ids:
            table = self._current_table()
            if table and table.rowCount() == 0:
                QMessageBox.information(self, "提示", "当前标签页没有可删除的项")
            else:
                QMessageBox.information(self, "提示", "请先选中要删除的项")
            return

        reply = QMessageBox.warning(
            self, "确认彻底删除",
            f"确定要彻底删除选中的 {label} 吗？\n\n"
            "此操作不可撤销，数据将从数据库永久移除。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        deleted = 0
        errors = []
        if current_tab == self.TAB_VOLUME:
            for vid in ids:
                try:
                    if self._chapter_service.hard_delete_volume(vid):
                        deleted += 1
                except Exception as e:
                    errors.append(str(e))
        elif current_tab == self.TAB_CHAPTER:
            for ch_id in ids:
                try:
                    if self._chapter_service.hard_delete_chapter(ch_id):
                        deleted += 1
                except Exception as e:
                    errors.append(str(e))
        elif current_tab == self.TAB_PROJECT:
            for pj_id in ids:
                try:
                    if self._project_service.hard_delete_project(pj_id):
                        deleted += 1
                except Exception as e:
                    errors.append(str(e))

        if errors:
            QMessageBox.critical(
                self, "删除失败",
                f"部分项目删除失败：\n\n" + "\n".join(errors[:5])
            )
        elif deleted > 0:
            self._load_data()
            logger.info(f"回收站: 永久删除 {deleted} 项")

    def _on_empty_trash(self):
        """清空回收站。"""
        reply = QMessageBox.warning(
            self, "确认清空回收站",
            "确定要清空回收站吗？\n\n"
            "以下数据将被永久移除：\n"
            "  - 所有已删除的分卷（含其下章节）\n"
            "  - 所有已删除的章节\n"
            "  - 所有已归档的项目\n\n"
            "此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        vol_count = self._chapter_service.hard_delete_all_volumes()
        ch_count = self._chapter_service.hard_delete_all_chapters()
        pj_count = self._project_service.hard_delete_all_projects()
        self._load_data()
        QMessageBox.information(
            self, "清空完成",
            f"已永久删除 {vol_count} 个分卷、{ch_count} 个章节、{pj_count} 个项目"
        )
        logger.info(f"回收站已清空: {vol_count} 分卷, {ch_count} 章节, {pj_count} 项目")

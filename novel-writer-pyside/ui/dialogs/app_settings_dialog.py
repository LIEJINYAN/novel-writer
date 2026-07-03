"""应用设置对话框。"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
    QSpinBox, QPushButton, QDialogButtonBox, QLabel, QTabWidget,
    QWidget, QMessageBox,
)
from PySide6.QtCore import Qt
from services.app_config_service import app_config_service
from app.config import AppConfig


class AppSettingsDialog(QDialog):
    """全局应用设置。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("应用设置")
        self.setMinimumWidth(480)
        self._changed = False
        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # ---- 常规 ----
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        general_layout.setSpacing(10)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["dark", "light"])
        general_layout.addRow("主题:", self._theme_combo)

        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["zh-CN", "en-US"])
        general_layout.addRow("语言:", self._lang_combo)

        self._auto_save_spin = QSpinBox()
        self._auto_save_spin.setRange(10, 600)
        self._auto_save_spin.setSuffix(" 秒")
        self._auto_save_spin.setSingleStep(10)
        general_layout.addRow("自动保存间隔:", self._auto_save_spin)

        tabs.addTab(general_tab, "常规")

        # ---- 编辑器 ----
        editor_tab = QWidget()
        editor_layout = QFormLayout(editor_tab)
        editor_layout.setSpacing(10)

        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(10, 32)
        editor_layout.addRow("字体大小:", self._font_size_spin)

        self._tab_width_spin = QSpinBox()
        self._tab_width_spin.setRange(2, 8)
        editor_layout.addRow("缩进宽度:", self._tab_width_spin)

        tabs.addTab(editor_tab, "编辑器")

        layout.addWidget(tabs)

        # 按钮
        btn_layout = QHBoxLayout()
        self._restore_btn = QPushButton("恢复默认")
        self._restore_btn.clicked.connect(self._restore_defaults)
        btn_layout.addWidget(self._restore_btn)
        btn_layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        btn_layout.addWidget(buttons)
        layout.addLayout(btn_layout)

    def _load_settings(self):
        """从 DB 加载配置。"""
        self._theme_combo.setCurrentText(
            app_config_service.get("theme", "dark")
        )
        self._lang_combo.setCurrentText(
            app_config_service.get("language", "zh-CN")
        )
        self._auto_save_spin.setValue(
            app_config_service.get_int("auto_save_interval", 60)
        )
        self._font_size_spin.setValue(
            app_config_service.get_int("editor_font_size", 14)
        )
        self._tab_width_spin.setValue(
            app_config_service.get_int("editor_tab_width", 4)
        )

    def _on_save(self):
        """保存设置到 DB 和运行时配置。"""
        config = AppConfig()

        # DB 持久化
        app_config_service.set("theme", self._theme_combo.currentText())
        app_config_service.set("language", self._lang_combo.currentText())
        app_config_service.set("auto_save_interval",
                                str(self._auto_save_spin.value()))
        app_config_service.set("editor_font_size",
                                str(self._font_size_spin.value()))
        app_config_service.set("editor_tab_width",
                                str(self._tab_width_spin.value()))

        # 运行时配置
        config.set("theme", self._theme_combo.currentText())
        config.set("language", self._lang_combo.currentText())

        QMessageBox.information(self, "设置已保存",
                                "部分设置（如主题、语言）将在下次启动时生效。")
        self._changed = True
        self.accept()

    def _restore_defaults(self):
        """恢复默认值。"""
        self._theme_combo.setCurrentText("dark")
        self._lang_combo.setCurrentText("zh-CN")
        self._auto_save_spin.setValue(60)
        self._font_size_spin.setValue(14)
        self._tab_width_spin.setValue(4)

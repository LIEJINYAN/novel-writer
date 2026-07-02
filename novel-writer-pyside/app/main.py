"""Novel Writer 应用入口。"""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSettings

# 将项目根目录加入 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models import db_manager
from ui.main_window import MainWindow
from ui.styles.style_manager import style_manager
from utils.logger import logger


def init_app() -> bool:
    """初始化应用（数据库、配置等）。"""
    try:
        db_manager.init_db()
        logger.info("数据库初始化成功")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False


def main():
    """应用主入口。"""
    app = QApplication(sys.argv)
    app.setApplicationName("Novel Writer")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("NovelWriter")

    # 设置控制台编码为 UTF-8（解决 Windows GBK 乱码）
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    # 初始化数据库
    if not init_app():
        logger.error("初始化失败，应用退出")
        sys.exit(1)

    # 读取保存的主题，默认暗色
    settings = QSettings("NovelWriter", "NovelWriter")
    saved_theme = settings.value("theme", "dark")
    style_manager.apply_theme(app, saved_theme)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    logger.success("应用启动成功")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

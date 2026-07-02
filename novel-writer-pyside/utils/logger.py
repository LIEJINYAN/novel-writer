"""日志模块。"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

class Logger:
    def __init__(self):
        self._logger = logging.getLogger("novel_writer")
        self._logger.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S",
        ))
        self._logger.addHandler(console_handler)
        
        # 文件处理器（按天轮转）
        try:
            log_dir = Path.home() / ".novel-writer" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{datetime.now():%Y-%m-%d}.log"
            
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            ))
            self._logger.addHandler(file_handler)
        except Exception:
            pass  # 文件日志失败不影响运行
    
    def info(self, msg: str, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)
    
    def success(self, msg: str, *args, **kwargs):
        self._logger.info(f"✓ {msg}", *args, **kwargs)
    
    def warn(self, msg: str, *args, **kwargs):
        self._logger.warning(f"⚠ {msg}", *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self._logger.error(f"✗ {msg}", *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)


logger = Logger()

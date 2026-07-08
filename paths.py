"""解析一般執行與 PyInstaller 打包後的檔案路徑。"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from excel_manager import UPLOAD_FOLDER_NAME

EXCEL_FILENAME = "A Namecard-system-database.xlsx"


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def base_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resource_dir() -> Path:
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def ensure_runtime_files() -> None:
    """首次執行 exe 時，把內建資料檔複製到 exe 旁邊。"""
    if not is_frozen():
        return

    target_base = base_dir()
    bundled_base = resource_dir()
    excel_target = target_base / EXCEL_FILENAME
    excel_source = bundled_base / EXCEL_FILENAME
    if not excel_target.exists() and excel_source.is_file():
        shutil.copy2(excel_source, excel_target)

    (target_base / UPLOAD_FOLDER_NAME).mkdir(parents=True, exist_ok=True)

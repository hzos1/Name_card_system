"""名片 OCR 自動填入 Excel 主程式。"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

import shutil

from card_ocr import IMAGE_EXTENSIONS, PDF_EXTENSIONS, extract_text_lines
from card_parser import card_to_row_values, parse_card_text
from excel_manager import UPLOAD_FOLDER_NAME, ExcelManager

SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | PDF_EXTENSIONS
DEFAULT_EXCEL = "A Namecard-system-database.xlsx"
UPLOAD_DIR = Path(UPLOAD_FOLDER_NAME)


def fill_missing_with_na(row_data: dict[str, str | None]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in row_data.items():
        text = "" if value is None else str(value).strip()
        normalized[key] = text if text else "NA"
    return normalized


def prompt_event() -> str:
    while True:
        event = input("請輸入 Event（活動名稱）: ").strip()
        if event:
            return event
        print("Event 不可為空，請重新輸入。")


def prompt_scan_date() -> str | date:
    while True:
        text = input(
            "請輸入掃描日期（格式：DD/MM/YYYY、YYYY-MM-DD 或 YYYY/MM/DD）: "
        ).strip()
        if not text:
            print("掃描日期不可為空，請重新輸入。")
            continue
        formatted = ExcelManager._format_scan_date(text)
        if isinstance(formatted, date):
            return formatted
        print(f"無法辨識日期格式：{text}，請重新輸入。")


def prompt_input_folder() -> Path:
    default = Path.cwd()
    text = input(f"名片圖片/PDF 所在資料夾（直接 Enter 使用 {default}）: ").strip()
    folder = Path(text) if text else default
    if not folder.is_dir():
        raise FileNotFoundError(f"找不到資料夾：{folder}")
    return folder


def ensure_in_upload_dir(card_path: Path) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = UPLOAD_DIR / card_path.name
    if card_path.resolve() != dest.resolve():
        shutil.copy2(card_path, dest)
    return dest


def collect_card_files(folder: Path, files: list[Path] | None = None) -> list[Path]:
    if files:
        candidates = files
    else:
        candidates = sorted(
            path
            for path in folder.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
    result: list[Path] = []
    for path in candidates:
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            print(f"略過不支援的檔案：{path.name}")
            continue
        if not path.is_file():
            print(f"略過找不到的檔案：{path}")
            continue
        result.append(path)
    return result


def process_card_file(
    manager: ExcelManager,
    card_path: Path,
    event: str,
    scan_date: str | date,
    *,
    skip_existing: bool = True,
) -> bool:
    if skip_existing and card_path.name in manager.get_existing_photo_names():
        print(f"  已存在，略過：{card_path.name}")
        return False

    print(f"  處理中：{card_path.name}")
    saved_path = ensure_in_upload_dir(card_path)
    lines = extract_text_lines(saved_path)
    card = parse_card_text(lines)
    row_data = fill_missing_with_na(card_to_row_values(card))
    card_id = manager.get_next_card_id()
    row_idx = manager.add_card(
        card_id=card_id,
        row_data=row_data,
        scan_date=scan_date,
        event=event,
        photo_name=saved_path.name,
        photo_path=saved_path,
    )
    print(
        f"  已寫入第 {row_idx} 列 | {card_id} | "
        f"{row_data.get('Name', 'NA')} | "
        f"{row_data.get('Company_name', 'NA')}"
    )
    return True


def process_cards(
    excel_path: Path,
    event: str,
    scan_date: str | date,
    card_files: list[Path],
    *,
    skip_existing: bool = True,
) -> tuple[int, int]:
    manager = ExcelManager(excel_path)
    processed = 0
    skipped = 0

    print(f"\n開始處理 {len(card_files)} 個名片檔案...")
    print(f"Event: {event}")
    print(f"掃描日期: {scan_date}")
    print(f"Excel: {excel_path}\n")

    for card_path in card_files:
        try:
            if process_card_file(
                manager,
                card_path,
                event,
                scan_date,
                skip_existing=skip_existing,
            ):
                processed += 1
            else:
                skipped += 1
        except Exception as exc:
            print(f"  處理失敗：{card_path.name} -> {exc}")

    if processed:
        manager.save()
        print(f"\n已儲存 Excel：{excel_path}")
    else:
        print("\n沒有新資料寫入，Excel 未更新。")

    return processed, skipped


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="依名片圖片/PDF 自動 OCR 並填入 Excel 資料庫。",
    )
    parser.add_argument(
        "--excel",
        default=DEFAULT_EXCEL,
        help=f"Excel 資料庫路徑（預設：{DEFAULT_EXCEL}）",
    )
    parser.add_argument("--event", help="活動名稱（Event）")
    parser.add_argument("--scan-date", help="掃描日期")
    parser.add_argument(
        "--folder",
        type=Path,
        help="名片圖片/PDF 所在資料夾",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="指定要處理的名片檔案（可取代資料夾掃描）",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="即使 Excel 已有相同檔名也重新寫入",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    excel_path = Path(args.excel)
    if not excel_path.is_file():
        print(f"找不到 Excel 檔案：{excel_path}", file=sys.stderr)
        return 1

    print("=== 名片 OCR 自動填入 Excel ===\n")

    event = args.event.strip() if args.event else prompt_event()
    scan_date = (
        ExcelManager._format_scan_date(args.scan_date.strip())
        if args.scan_date
        else prompt_scan_date()
    )
    if isinstance(scan_date, str):
        print(f"無法辨識日期格式：{args.scan_date}", file=sys.stderr)
        return 1

    if args.files:
        card_files = collect_card_files(Path.cwd(), list(args.files))
    else:
        folder = args.folder or prompt_input_folder()
        card_files = collect_card_files(folder)

    if not card_files:
        print("找不到可處理的名片圖片或 PDF。", file=sys.stderr)
        return 1

    processed, skipped = process_cards(
        excel_path=excel_path,
        event=event,
        scan_date=scan_date,
        card_files=card_files,
        skip_existing=not args.force,
    )
    print(f"\n完成：新增 {processed} 筆，略過 {skipped} 筆。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

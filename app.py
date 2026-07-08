"""HTML Web App：上傳名片、搜尋資料庫並預覽 PDF。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from card_ocr import extract_text_lines
from card_parser import card_to_row_values, parse_card_text
from excel_manager import (
    ExcelManager,
    HEADERS,
    SCAN_CARD_HEADER,
    UPLOAD_FOLDER_NAME,
    scan_card_link_text,
)

BASE_DIR = Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR / "A Namecard-system-database.xlsx"
UPLOAD_DIR = BASE_DIR / UPLOAD_FOLDER_NAME
ALT_PDF_DIR = BASE_DIR / "Namecard-system-database"
ALLOWED_EXTENSIONS = {".pdf"}

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

PDF_SEARCH_DIRS = [
    UPLOAD_DIR,
    ALT_PDF_DIR,
    BASE_DIR,
]

EDITABLE_ROW_HEADERS = [
    "Name",
    "Company_name",
    "Title",
    "Tel",
    "FEX",
    "company_Tel",
    "Email",
    "Company Address",
    "Company Website",
    "Line/ID",
    "Wechat_ID",
    "備註",
]


def _fill_missing_with_na(row_data: dict[str, str | None]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in row_data.items():
        text = "" if value is None else str(value).strip()
        normalized[key] = text if text else "NA"
    return normalized


def _is_allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _build_unique_path(filename: str) -> Path:
    safe_name = secure_filename(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = Path(safe_name).stem or "name_card"
    suffix = Path(safe_name).suffix.lower() or ".pdf"
    return UPLOAD_DIR / f"{stem}_{timestamp}{suffix}"


def _scan_filename_from_cell(cell) -> str | None:
    if cell.hyperlink and cell.hyperlink.target:
        target = str(cell.hyperlink.target)
        if target.startswith("file://"):
            return Path(target.removeprefix("file://")).name
        return Path(target).name
    return None


def _find_pdf_path(filename: str) -> Path | None:
    safe_name = secure_filename(Path(filename).name)
    if not safe_name:
        return None
    for folder in PDF_SEARCH_DIRS:
        candidate = folder / safe_name
        if candidate.is_file():
            return candidate.resolve()
    return None


def _pdf_url_for_name(filename: str) -> str:
    return url_for("serve_pdf", filename=secure_filename(Path(filename).name))


def _find_pdf_by_card_id_in_dirs(card_id: str) -> Path | None:
    card_prefix = card_id.strip().upper()
    if not card_prefix:
        return None
    for folder in PDF_SEARCH_DIRS:
        if not folder.is_dir():
            continue
        matches = sorted(folder.glob(f"{card_prefix}*.pdf"))
        if matches:
            return matches[0].resolve()
    return None


def _find_pdf_by_card_id(card_id: str) -> Path | None:
    if not EXCEL_PATH.is_file():
        return None
    manager = ExcelManager(EXCEL_PATH)
    headers = manager._header_index
    sheet = manager.sheet
    target_id = card_id.strip().lower()
    for row in range(2, sheet.max_row + 1):
        value = str(sheet.cell(row=row, column=headers["卡片ID"]).value or "").strip().lower()
        if value != target_id:
            continue
        scan_cell = sheet.cell(row=row, column=headers[SCAN_CARD_HEADER])
        pdf_name = _scan_filename_from_cell(scan_cell)
        if pdf_name:
            found = _find_pdf_path(pdf_name)
            if found:
                return found
        return _find_pdf_by_card_id_in_dirs(card_id)
    return None


def _load_search_results(keyword: str) -> list[dict[str, str]]:
    if not EXCEL_PATH.is_file():
        return []

    manager = ExcelManager(EXCEL_PATH)
    sheet = manager.sheet
    headers = manager._header_index
    keyword_l = keyword.strip().lower()
    results: list[dict[str, str]] = []

    for row in range(2, sheet.max_row + 1):
        card_id = str(sheet.cell(row=row, column=headers["卡片ID"]).value or "").strip()
        if not card_id:
            continue
        name = str(sheet.cell(row=row, column=headers["Name"]).value or "").strip()
        company = str(sheet.cell(row=row, column=headers["Company_name"]).value or "").strip()
        title = str(sheet.cell(row=row, column=headers["Title"]).value or "").strip()
        tel = str(sheet.cell(row=row, column=headers["Tel"]).value or "").strip()
        company_tel = str(sheet.cell(row=row, column=headers["company_Tel"]).value or "").strip()
        event = str(sheet.cell(row=row, column=headers["Event"]).value or "").strip()
        scan_date = str(sheet.cell(row=row, column=headers["Scan_date"]).value or "").strip()
        scan_cell = sheet.cell(row=row, column=headers[SCAN_CARD_HEADER])
        pdf_name = _scan_filename_from_cell(scan_cell)

        search_blob = " ".join(
            [card_id, name, company, title, tel, company_tel, event, scan_date]
        ).lower()
        if keyword_l and keyword_l not in search_blob:
            continue

        found_pdf = _find_pdf_path(pdf_name) if pdf_name else _find_pdf_by_card_id_in_dirs(card_id)
        pdf_exists = bool(found_pdf)
        results.append(
            {
                "card_id": card_id,
                "name": name or "NA",
                "company": company or "NA",
                "title": title or "NA",
                "tel": tel or "NA",
                "company_tel": company_tel or "NA",
                "event": event or "NA",
                "scan_date": scan_date or "NA",
                "pdf_name": (found_pdf.name if found_pdf else "NA"),
                "pdf_url": _pdf_url_for_name(found_pdf.name) if found_pdf else "",
            }
        )
    return results


@app.route("/cards/pdf/<path:filename>")
def serve_pdf(filename: str):
    target = _find_pdf_path(filename)
    if not target:
        abort(404)
    return send_file(target, mimetype="application/pdf")


@app.route("/cards/pdf-by-id/<card_id>")
def serve_pdf_by_card_id(card_id: str):
    target = _find_pdf_by_card_id(card_id)
    if not target:
        abort(404)
    return send_file(target, mimetype="application/pdf")


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    result: dict[str, str] | None = None
    draft: dict[str, str] | None = None
    error: str | None = None

    if request.method == "POST":
        action = request.form.get("action", "scan").strip().lower()
        event = request.form.get("event", "").strip()
        scan_date_text = request.form.get("scan_date", "").strip()

        if action == "confirm":
            saved_name = secure_filename(request.form.get("saved_file_name", "").strip())
            saved_path = _find_pdf_path(saved_name) if saved_name else None

            if not event:
                error = "請輸入 Event。"
            elif not scan_date_text:
                error = "請輸入掃描日期。"
            elif not saved_path:
                error = "找不到暫存的名片檔案，請重新掃描。"
            else:
                formatted_date = ExcelManager._format_scan_date(scan_date_text)
                if isinstance(formatted_date, str):
                    error = "掃描日期格式錯誤，請使用 YYYY-MM-DD。"
                elif not EXCEL_PATH.is_file():
                    error = f"找不到 Excel 檔案：{EXCEL_PATH.name}"
                else:
                    row_data = _fill_missing_with_na(
                        {header: request.form.get(header, "").strip() for header in EDITABLE_ROW_HEADERS}
                    )
                    try:
                        manager = ExcelManager(EXCEL_PATH)
                        card_id = manager.get_next_card_id()
                        manager.add_card(
                            card_id=card_id,
                            row_data=row_data,
                            scan_date=formatted_date,
                            event=event,
                            photo_name=saved_path.name,
                            photo_path=saved_path,
                        )
                        manager.save()

                        full_row = {
                            "卡片ID": card_id,
                            "Scan_date": str(formatted_date),
                            "Event": event,
                            **row_data,
                            SCAN_CARD_HEADER: scan_card_link_text(card_id),
                        }
                        result = {
                            "fields": [
                                {
                                    "column": header,
                                    "value": full_row.get(header, "NA"),
                                }
                                for header in HEADERS
                            ],
                            "file_name": saved_path.name,
                            "pdf_url": _pdf_url_for_name(saved_path.name),
                        }
                    except Exception as exc:
                        error = f"處理失敗：{exc}"
        else:
            card_file = request.files.get("card_pdf")
            if not event:
                error = "請輸入 Event。"
            elif not scan_date_text:
                error = "請輸入掃描日期。"
            elif card_file is None or not card_file.filename:
                error = "請選擇要上傳的名片 PDF。"
            elif not _is_allowed_file(card_file.filename):
                error = "目前只支援 PDF 檔案。"
            else:
                formatted_date = ExcelManager._format_scan_date(scan_date_text)
                if isinstance(formatted_date, str):
                    error = "掃描日期格式錯誤，請使用 YYYY-MM-DD。"
                else:
                    try:
                        saved_path = _build_unique_path(card_file.filename)
                        card_file.save(saved_path)

                        lines = extract_text_lines(saved_path)
                        card = parse_card_text(lines)
                        row_data = _fill_missing_with_na(card_to_row_values(card))
                        draft = {
                            "event": event,
                            "scan_date": str(formatted_date),
                            "saved_file_name": saved_path.name,
                            "pdf_url": _pdf_url_for_name(saved_path.name),
                            "fields": [
                                {"column": header, "value": row_data.get(header, "NA")}
                                for header in EDITABLE_ROW_HEADERS
                            ],
                        }
                    except Exception as exc:
                        error = f"處理失敗：{exc}"

    query = request.args.get("q", "").strip()
    search_results = _load_search_results(query) if query else []
    preview = request.args.get("preview", "").strip()
    preview_url = ""
    if preview:
        safe_preview = secure_filename(Path(preview).name)
        if safe_preview and _find_pdf_path(safe_preview):
            preview_url = _pdf_url_for_name(safe_preview)

    return render_template(
        "index.html",
        result=result,
        draft=draft,
        error=error,
        query=query,
        search_results=search_results,
        preview_url=preview_url,
    )


if __name__ == "__main__":
    import os
    import threading
    import webbrowser

    def _open_browser() -> None:
        webbrowser.open("http://127.0.0.1:5000")

    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(1.0, _open_browser).start()

    app.run(debug=True, host="127.0.0.1", port=5000)

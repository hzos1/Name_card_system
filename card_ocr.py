"""從名片 PDF 或圖片擷取 OCR 文字。"""

from __future__ import annotations

from pathlib import Path

import fitz
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
PDF_EXTENSIONS = {".pdf"}

_ocr_engine: RapidOCR | None = None


def _get_ocr() -> RapidOCR:
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = RapidOCR()
    return _ocr_engine


def _image_to_array(image: Image.Image) -> np.ndarray:
    rgb = image.convert("RGB")
    return np.array(rgb)


def _ocr_image(image: Image.Image) -> list[str]:
    result, _ = _get_ocr()(_image_to_array(image))
    if not result:
        return []
    return [line[1].strip() for line in result if line[1].strip()]


def _ocr_pdf(path: Path) -> list[str]:
    doc = fitz.open(path)
    lines: list[str] = []
    for page in doc:
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        channels = pix.n
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, channels)
        if channels == 4:
            img = img[:, :, :3]
        ocr_lines, _ = _get_ocr()(img)
        if ocr_lines:
            lines.extend(line[1].strip() for line in ocr_lines if line[1].strip())
        if len(lines) < 3:
            text = page.get_text("text").strip()
            if text:
                lines.extend(line.strip() for line in text.splitlines() if line.strip())
    return _dedupe_lines(lines)


def _dedupe_lines(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for line in lines:
        key = line.lower().replace(" ", "")
        if key in seen:
            continue
        seen.add(key)
        result.append(line)
    return result


def extract_text_lines(path: str | Path) -> list[str]:
    """讀取名片檔案並回傳 OCR 文字行。"""
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix in PDF_EXTENSIONS:
        return _ocr_pdf(file_path)
    if suffix in IMAGE_EXTENSIONS:
        with Image.open(file_path) as image:
            return _ocr_image(image)
    raise ValueError(f"不支援的檔案格式: {suffix}")

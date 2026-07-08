"""將 OCR 文字解析為名片欄位。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache

from opencc import OpenCC

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.I)
WEBSITE_RE = re.compile(
    r"(?:https?://|www\.)[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
    re.I,
)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s\-().]{6,}\d)")
WECHAT_RE = re.compile(
    r"(?:we\s*chat\s*(?:id)?|微信)\s*[:：]?\s*([A-Za-z0-9._-]+)",
    re.I,
)
LINE_RE = re.compile(r"(?:line\s*(?:id)?)\s*[:：]?\s*([A-Za-z0-9._-]+)", re.I)

TITLE_KEYWORDS = (
    "manager",
    "director",
    "president",
    "founder",
    "engineer",
    "consultant",
    "general",
    "head",
    "chief",
    "officer",
    "doctor",
    "dds",
    "博士",
    "總監",
    "經理",
    "主任",
    "創始",
    "負責人",
    "副總",
    "division",
    "forecasting",
)

COMPANY_KEYWORDS = (
    "limited",
    "ltd",
    "inc",
    "corp",
    "company",
    "express",
    "council",
    "bank",
    "university",
    "college",
    "bio",
    "tech",
    "有限公司",
    "股份",
    "銀行",
    "科技",
    "公司",
)

ADDRESS_KEYWORDS = (
    "road",
    "street",
    "avenue",
    "suite",
    "floor",
    "tower",
    "building",
    "kowloon",
    "room",
    "plaza",
    "centre",
    "center",
    "headquarters",
    "路",
    "街",
    "道",
    "樓",
    "室",
    "座",
    "香港",
    "九龍",
)

STREET_ADDRESS_KEYWORDS = (
    "road",
    "street",
    "avenue",
    "suite",
    "floor",
    "tower",
    "building",
    "room",
    "plaza",
    "centre",
    "center",
    "headquarters",
    "路",
    "街",
    "道",
    "樓",
    "室",
    "座",
)


@dataclass
class CardData:
    name: str | None = None
    company_name: str | None = None
    title: str | None = None
    tel: str | None = None
    fax: str | None = None
    company_tel: str | None = None
    email: str | None = None
    company_address: str | None = None
    company_website: str | None = None
    line_id: str | None = None
    wechat_id: str | None = None
    notes: str | None = None
    raw_lines: list[str] = field(default_factory=list)


def _normalize_phone(value: str) -> str:
    digits = re.sub(r"[^\d+]", "", value)
    digits = re.sub(r"^\+?852", "", digits)
    digits = re.sub(r"\D", "", digits)
    if len(digits) == 8:
        return f"{digits[:4]} {digits[4:]}"
    return value.strip()


def _extract_labeled_phone(line: str) -> tuple[str, str] | None:
    patterns = [
        (r"^\s*m\s*[:：]?\s*(.+)$", "mobile"),
        (r"^\s*d\s*[:：]?\s*(.+)$", "company"),
        (r"^\s*f\s*[:：]?\s*(.+)$", "fax"),
        (r"\b(?:m|mobile|手機)\s*[:：]\s*(.+)$", "mobile"),
        (r"\b(?:f|fax)\s*[:：]\s*(.+)$", "fax"),
        (r"\b(?:t|tel|d|direct)\s*[:：]\s*(.+)$", "company"),
        (r"\b(?:tel|telephone)\s*[:：]\s*(.+)$", "company"),
        (r"\bfax\s*[:：]\s*(.+)$", "fax"),
        (r"\be-?mail\s*[:：]\s*(.+)$", "email"),
    ]
    lower = line.lower()
    for pattern, kind in patterns:
        match = re.search(pattern, lower, re.I)
        if match:
            return kind, match.group(1).strip()
    return None


def _is_garbled(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("*"):
        return True
    weird = sum(ch in "~`^|\\<>{}[]" for ch in stripped)
    if weird >= 2:
        return True
    alnum = sum(ch.isalnum() or ch in " .,'-" for ch in stripped)
    if alnum / max(len(stripped), 1) < 0.6:
        return True
    return False


def _looks_like_name(line: str) -> bool:
    if _is_garbled(line):
        return False
    if re.search(r"(?:博士|醫生|醫師|dental|dentist)", line, re.I):
        return False
    if EMAIL_RE.search(line) or WEBSITE_RE.search(line):
        return False
    if PHONE_RE.fullmatch(line.replace(" ", "")) or (
        PHONE_RE.search(line) and len(line) < 20
    ):
        return False
    keywords = TITLE_KEYWORDS + COMPANY_KEYWORDS + ADDRESS_KEYWORDS
    if any(keyword in line.lower() for keyword in keywords):
        return False
    if re.fullmatch(r"[A-Za-z][A-Za-z.'\- ]{2,40}", line.strip()):
        if re.fullmatch(r"[A-Za-z0-9._-]{4,}", line.strip()) and " " not in line.strip():
            return False
        return True
    if re.fullmatch(r"[\u4e00-\u9fff]{2,4}", line.strip()):
        return True
    if re.search(r"[A-Za-z]+ [A-Za-z]+", line) and len(line) <= 40:
        return True
    return False


def _looks_like_company(line: str) -> bool:
    if line.startswith("（") or line.startswith("("):
        return False
    lower = line.lower()
    return any(keyword in lower for keyword in COMPANY_KEYWORDS)


def _looks_like_title(line: str) -> bool:
    lower = line.lower()
    if _looks_like_address(line):
        return False
    return any(keyword in lower for keyword in TITLE_KEYWORDS)


def _looks_like_wechat_id(line: str) -> bool:
    text = line.strip()
    if " " in text or len(text) < 4 or len(text) > 32:
        return False
    if EMAIL_RE.search(text) or WEBSITE_RE.search(text):
        return False
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9._-]{3,31}", text))


@lru_cache(maxsize=1)
def _opencc_converter() -> OpenCC:
    return OpenCC("s2t")


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def _to_traditional(text: str | None) -> str | None:
    if text is None:
        return None
    stripped = text.strip()
    if not stripped:
        return None
    if not _contains_cjk(stripped):
        return stripped
    return _opencc_converter().convert(stripped)


def _has_street_address_pattern(line: str) -> bool:
    lower = line.lower()
    if ADDRESS_START_RE.search(line):
        return True
    if any(keyword in lower for keyword in STREET_ADDRESS_KEYWORDS):
        return True
    return bool(re.search(r"\d", line))


ADDRESS_START_RE = re.compile(
    r"(?:\b(?:flat|unit|room|suite|level)\s*[#.:]?\s*[A-Za-z0-9-]+"
    r"|\b\d{1,3}\s*/\s*F\b"
    r"|\bLG\s*/\s*F\b"
    r"|\bG\s*/\s*F\b)",
    re.I,
)
HONG_KONG_END_RE = re.compile(r"Hong Kong(?:\s+SAR)?|H\.K\.", re.I)


def _extract_address_from_lines(lines: list[str]) -> str | None:
    """Address often starts at Flat/Unit/Room/Suite/Level or xx/F,
    and may span up to 3 lines above the Hong Kong line."""
    cleaned = [line.strip() for line in lines if line and line.strip()]

    for idx, line in enumerate(cleaned):
        end_match = HONG_KONG_END_RE.search(line)
        if not end_match:
            continue

        context = cleaned[max(0, idx - 3) : idx + 1]
        start_line_idx: int | None = None
        start_char_idx = 0

        for j, ctx_line in enumerate(context):
            if _looks_like_company(ctx_line) and not ADDRESS_START_RE.search(ctx_line):
                continue
            start_match = ADDRESS_START_RE.search(ctx_line)
            if start_match:
                start_line_idx = j
                start_char_idx = start_match.start()
                break

        if start_line_idx is None:
            for j, ctx_line in enumerate(context):
                if _has_street_address_pattern(ctx_line) and not _looks_like_company(ctx_line):
                    start_line_idx = j
                    start_char_idx = 0
                    break

        if start_line_idx is None:
            start_match = ADDRESS_START_RE.search(line)
            if start_match:
                return line[start_match.start() : end_match.end()].strip(" ,;")
            continue

        selected = context[start_line_idx:]
        if len(selected) == 1:
            address = selected[0][start_char_idx : end_match.end()]
        else:
            first = selected[0][start_char_idx:]
            middle = selected[1:-1]
            last = selected[-1][: end_match.end()]
            address = ", ".join([first, *middle, last])

        return address.strip(" ,;")

    return None


def _looks_like_address(line: str) -> bool:
    if len(line) < 12:
        return False
    if _looks_like_company(line) and not _has_street_address_pattern(line):
        return False
    lower = line.lower()
    return _has_street_address_pattern(line) or any(
        keyword in lower for keyword in ("kowloon", "hong kong")
    )


def _normalize_company_address(
    address: str | None,
    company_name: str | None,
) -> str | None:
    if not address or not address.strip():
        return None

    parts = [part.strip() for part in re.split(r"\s*;\s*", address) if part.strip()]
    if company_name:
        company_key = company_name.strip().lower()
        parts = [part for part in parts if part.lower() != company_key]

    address_parts = [part for part in parts if _looks_like_address(part)]
    if not address_parts:
        address_parts = [
            part
            for part in parts
            if not (_looks_like_company(part) and not _has_street_address_pattern(part))
        ]

    if not address_parts:
        return None

    english_parts = [part for part in address_parts if re.search(r"[A-Za-z]", part)]
    candidates = english_parts or address_parts

    # Rule: address starts from Flat/Unit/Room/Suite/Level or floor pattern
    # and ends at "Hong Kong".
    for part in candidates:
        start = ADDRESS_START_RE.search(part)
        if not start:
            continue
        end_match = HONG_KONG_END_RE.search(part)
        if end_match:
            return part[start.start() : end_match.end()].strip(" ,;")

    floor_start = re.compile(
        r"(?:\b\d{1,3}\s*/\s*F\b|\bLG\s*/\s*F\b|\bG\s*/\s*F\b)",
        re.I,
    )
    for part in candidates:
        start = floor_start.search(part)
        if not start:
            continue
        match = re.search(r"Hong Kong", part, re.I)
        if match:
            return part[start.start() : match.end()].strip(" ,;")

    for part in candidates:
        start = floor_start.search(part)
        if not start:
            continue
        idx = part.lower().find("hong kong", start.start())
        if idx != -1:
            return part[start.start() : idx + len("Hong Kong")].strip(" ,;")

    # Fallback: keep previous behavior if no floor-start pattern found.
    for part in candidates:
        match = re.search(r"(.+?Hong Kong)\s*$", part, re.I)
        if match:
            return match.group(1).strip(" ,;")

    return candidates[0]


def parse_card_text(lines: list[str]) -> CardData:
    card = CardData(raw_lines=list(lines))
    remaining: list[str] = []

    for line in lines:
        email_match = EMAIL_RE.search(line)
        if email_match and not card.email:
            card.email = email_match.group(0)

        website_match = WEBSITE_RE.search(line)
        if website_match and not card.company_website:
            card.company_website = website_match.group(0)

        wechat_match = WECHAT_RE.search(line)
        if wechat_match and not card.wechat_id:
            card.wechat_id = wechat_match.group(1)

        line_match = LINE_RE.search(line)
        if line_match and not card.line_id:
            card.line_id = line_match.group(1)

        labeled = _extract_labeled_phone(line)
        if labeled:
            kind, value = labeled
            phones = PHONE_RE.findall(value)
            if phones:
                phone = _normalize_phone(phones[0])
                if kind == "mobile" and not card.tel:
                    card.tel = phone
                elif kind == "fax" and not card.fax:
                    card.fax = phone
                elif kind == "company" and not card.company_tel:
                    card.company_tel = phone
            continue

        if "fax" in line.lower() and not card.fax:
            phones = PHONE_RE.findall(line)
            if phones:
                card.fax = _normalize_phone(phones[-1])
                continue

        if re.search(r"\b(?:tel|telephone)\b", line, re.I) and not card.company_tel:
            phones = PHONE_RE.findall(line)
            if phones:
                card.company_tel = _normalize_phone(phones[0])
                continue

        unlabeled_phones = PHONE_RE.findall(line)
        if unlabeled_phones and not re.search(r"\b(?:fax|f)\b", line, re.I):
            if len(unlabeled_phones) == 1 and "+" in line:
                phone = _normalize_phone(unlabeled_phones[0])
                if not card.company_tel:
                    card.company_tel = phone
                elif not card.tel:
                    card.tel = phone
                continue

        if _looks_like_wechat_id(line) and re.search(r"we\s*chat|微信", line, re.I):
            wechat_match = WECHAT_RE.search(line)
            card.wechat_id = (
                wechat_match.group(1) if wechat_match else line.strip()
            )
            continue

        stripped = line.strip()
        if not stripped:
            continue
        if EMAIL_RE.fullmatch(stripped):
            continue
        remaining.append(stripped)

    company_candidates = [line for line in remaining if _looks_like_company(line)]
    if company_candidates:
        ranked = sorted(
            company_candidates,
            key=lambda line: (
                bool(
                    re.search(
                        r"(?:limited|ltd|inc|corp|有限公司)\s*\.?$",
                        line,
                        re.I,
                    )
                ),
                bool(
                    re.search(
                        r"\b(?:limited|ltd|inc|corp|有限公司)\b",
                        line,
                        re.I,
                    )
                ),
                len(line),
            ),
            reverse=True,
        )
        card.company_name = ranked[0]

    title_candidates = [line for line in remaining if _looks_like_title(line)]
    if title_candidates:
        short_titles = sorted(title_candidates, key=len)[:4]
        card.title = ", ".join(short_titles)

    name_candidates = [line for line in remaining if _looks_like_name(line)]
    if name_candidates:
        latin_names = [
            line for line in name_candidates if re.search(r"[A-Za-z]{2,}", line)
        ]
        chinese_names = [
            line
            for line in name_candidates
            if re.fullmatch(r"[\u4e00-\u9fff]{2,4}", line)
        ]
        if latin_names:
            card.name = latin_names[0]
        elif chinese_names:
            card.name = chinese_names[0]

    if not card.tel:
        for line in remaining:
            if re.search(r"\b(?:m|mobile)\b", line, re.I):
                phones = PHONE_RE.findall(line)
                if phones:
                    card.tel = _normalize_phone(phones[0])
                    break

    if not card.company_tel:
        phones: list[str] = []
        for line in remaining:
            if EMAIL_RE.search(line) or WEBSITE_RE.search(line):
                continue
            found = PHONE_RE.findall(line)
            phones.extend(_normalize_phone(p) for p in found)
        used = {card.tel, card.fax}
        for phone in phones:
            if phone not in used:
                card.company_tel = phone
                break

    for line in remaining:
        if line == card.name:
            continue
        if line == card.company_name:
            continue
        if line == card.title:
            continue
        if line in (card.company_address or ""):
            continue
        if card.company_name:
            continue
        if len(line) <= 3:
            continue
        if _looks_like_company(line):
            card.company_name = line
            break

    extracted_address = _extract_address_from_lines(lines)
    if extracted_address:
        card.company_address = extracted_address
    else:
        for line in remaining:
            if _looks_like_address(line):
                card.company_address = (
                    f"{card.company_address}; {line}" if card.company_address else line
                )

    card.company_address = _normalize_company_address(
        card.company_address,
        card.company_name,
    )
    card.name = _to_traditional(card.name)
    card.company_name = _to_traditional(card.company_name)
    card.title = _to_traditional(card.title)
    card.company_address = _to_traditional(card.company_address)
    card.notes = _to_traditional(card.notes)

    return card


def card_to_row_values(card: CardData, na: str = "N/A") -> dict[str, str | None]:
    def val(value: str | None) -> str | None:
        if value is None or not str(value).strip():
            return None
        return _to_traditional(str(value).strip())

    return {
        "Name": val(card.name),
        "Company_name": val(card.company_name),
        "Title": val(card.title),
        "Tel": val(card.tel) or na,
        "FEX": val(card.fax) or na,
        "company_Tel": val(card.company_tel) or na,
        "Email": val(card.email),
        "Company Address": val(card.company_address),
        "Company Website": val(card.company_website) or na,
        "Line/ID": val(card.line_id) or na,
        "Wechat_ID": val(card.wechat_id) or na,
        "備註": val(card.notes),
    }

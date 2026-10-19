"""Tiện ích dùng chung cho script của inlink-generator."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = SKILL_ROOT / "runs"

# Sheet kế hoạch content mặc định: đặt qua biến môi trường INLINK_SHEET_ID (hoặc truyền --sheet-id).
DEFAULT_SHEET_ID = os.environ.get("INLINK_SHEET_ID", "").strip()

HEADING_STYLES = {
    "HEADING_1", "HEADING_2", "HEADING_3", "HEADING_4", "HEADING_5", "HEADING_6",
    "TITLE", "SUBTITLE",
}

_DOC_ID_RE = re.compile(r"/document/d/([a-zA-Z0-9_-]+)")
_BARE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{20,}$")


def emit(payload: dict, out: str | None = None) -> None:
    """In JSON ra stdout hoặc ghi file. Luôn có khóa error."""
    payload.setdefault("error", None)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if out:
        out_path = Path(out).expanduser()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(json.dumps({"written": str(out_path), "error": None}, ensure_ascii=False))
    else:
        print(text)


def fail(message: str, **extra) -> None:
    """Trả lỗi dạng JSON rồi thoát. Thông điệp tiếng Việt, nêu rõ cần làm gì."""
    payload = {"ok": False, "error": message}
    payload.update(extra)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(0)


def log(message: str) -> None:
    print(message, file=sys.stderr)


def extract_doc_id(url_or_id: str) -> str:
    """Lấy document ID từ 1 link Google Docs, hoặc trả nguyên nếu đã là ID trần."""
    s = url_or_id.strip()
    m = _DOC_ID_RE.search(s)
    if m:
        return m.group(1)
    if _BARE_ID_RE.match(s):
        return s
    raise ValueError(f"Không nhận ra định dạng link/ID Google Doc: {url_or_id!r}")


def utf16_len(s: str) -> int:
    """Docs API dùng UTF-16 code unit làm index — không phải len() Python thường."""
    return len(s.encode("utf-16-le")) // 2


def utf16_slice(s: str, start_u16: int, end_u16: int) -> str:
    """Cắt chuỗi Python theo offset UTF-16 (đơn vị Docs API dùng cho index)."""

    def _py_index(u16_target: int) -> int:
        acc = 0
        for i, ch in enumerate(s):
            ch_len = len(ch.encode("utf-16-le")) // 2
            if acc + ch_len > u16_target:
                return i
            acc += ch_len
        return len(s)

    return s[_py_index(start_u16):_py_index(end_u16)]


def is_heading(named_style: str | None) -> bool:
    return bool(named_style) and named_style in HEADING_STYLES


def col_letter(n: int) -> str:
    """1 -> 'A', 26 -> 'Z', 27 -> 'AA' ..."""
    s = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        s = chr(65 + rem) + s
    return s or "A"


def run_dir(doc_id: str) -> Path:
    d = RUNS_DIR / doc_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def sheets_service(creds):
    from googleapiclient.discovery import build
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def docs_service(creds):
    from googleapiclient.discovery import build
    return build("docs", "v1", credentials=creds, cache_discovery=False)


def has_suggestions(node) -> bool:
    """Quét đệ quy 1 node JSON của Docs API tìm dấu vết suggested-edit chưa resolve."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("suggested") and v:
                return True
            if has_suggestions(v):
                return True
    elif isinstance(node, list):
        return any(has_suggestions(x) for x in node)
    return False


def flatten_document(document: dict) -> list[dict]:
    """Dàn phẳng body.content của Docs API thành list đoạn văn (bỏ qua bảng/ảnh — ngoài phạm vi v1).

    Mỗi đoạn: index, start_index, end_index, named_style, is_heading, text, bullet,
    runs (start_index, end_index, text, bold, italic, link_url) — index đều là UTF-16
    code unit như Docs API dùng, KHÔNG phải len() Python thường.
    """
    paragraphs = []
    body = document.get("body", {}).get("content", [])
    p_idx = 0
    for element in body:
        para = element.get("paragraph")
        if not para:
            continue  # table/tableOfContents/sectionBreak... ngoài phạm vi v1
        style = para.get("paragraphStyle", {}).get("namedStyleType")
        p_start = element.get("startIndex", 0)
        p_end = element.get("endIndex", 0)
        runs = []
        text_parts = []
        for el in para.get("elements", []):
            tr = el.get("textRun")
            if not tr:
                continue  # inlineObjectElement, footnoteReference... ngoài phạm vi v1
            content = tr.get("content", "")
            stripped = content[:-1] if content.endswith("\n") else content
            if stripped == "":
                continue
            r_start = el.get("startIndex", 0)
            r_end = r_start + utf16_len(stripped)
            ts = tr.get("textStyle", {})
            runs.append({
                "start_index": r_start,
                "end_index": r_end,
                "text": stripped,
                "bold": bool(ts.get("bold")),
                "italic": bool(ts.get("italic")),
                "link_url": (ts.get("link") or {}).get("url"),
            })
            text_parts.append(stripped)
        paragraphs.append({
            "index": p_idx,
            "start_index": p_start,
            "end_index": p_end,
            "named_style": style,
            "is_heading": is_heading(style),
            "text": "".join(text_parts),
            "bullet": bool(para.get("bullet")),
            "runs": runs,
        })
        p_idx += 1
    return paragraphs


_WORD_BOUND_START = r"(?<![^\W_])"
_WORD_BOUND_END = r"(?![^\W_])"


def build_anchor_pattern(phrase: str) -> re.Pattern:
    words = phrase.strip().split()
    escaped = r"\s+".join(re.escape(w) for w in words)
    return re.compile(_WORD_BOUND_START + escaped + _WORD_BOUND_END, re.IGNORECASE | re.UNICODE)


def find_non_overlapping_matches(text: str, candidates: list[dict]) -> list[dict]:
    """Tìm occurrence không chồng lấn của nhiều candidate trong 1 đoạn text — candidate dài xử
    lý trước, chiếm span trước (chặn candidate ngắn là substring của candidate dài, VD
    "iPhone 18" trong "iPhone 18 Pro"). Word-boundary Unicode-aware, không phân biệt hoa/thường.
    Trả list [{anchor_text, target_url, start, end, matched_text}], sort theo start."""
    ordered = sorted(candidates, key=lambda c: -len(c["anchor_text"]))
    claimed: list[tuple[int, int]] = []
    results = []
    for c in ordered:
        pattern = build_anchor_pattern(c["anchor_text"])
        for m in pattern.finditer(text):
            span = (m.start(), m.end())
            if any(not (span[1] <= s or e <= span[0]) for s, e in claimed):
                continue
            claimed.append(span)
            results.append({
                "anchor_text": c["anchor_text"],
                "target_url": c["target_url"],
                "start": span[0],
                "end": span[1],
                "matched_text": text[span[0]:span[1]],
            })
    results.sort(key=lambda r: r["start"])
    return results


def existing_links_from(paragraphs: list[dict]) -> list[dict]:
    links = []
    for p in paragraphs:
        for r in p["runs"]:
            if r["link_url"]:
                links.append({
                    "url": r["link_url"],
                    "anchor_text": r["text"],
                    "paragraph_index": p["index"],
                    "start_index": r["start_index"],
                    "end_index": r["end_index"],
                })
    return links

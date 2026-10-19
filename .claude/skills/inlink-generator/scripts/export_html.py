"""Xuất đoạn HTML sẵn dán WordPress từ chính doc_structure.json + placements.json đã dùng để
ghi vào Google Doc (không crawl lại) — vì Google Docs không có khái niệm target="_blank",
placement mới luôn được render thành <a target="_blank" rel="noopener"><strong>...</strong></a>
đầy đủ ở đây. Link/bold đã có TỪ TRƯỚC trong bài giữ nguyên <a href>/<strong> (không ép
target="_blank" lên link cũ, chỉ áp cho placement mới).

Ngoài phạm vi v1: ảnh, bảng, footnote.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common

_HEADING_TAGS = {
    "HEADING_1": "h1", "HEADING_2": "h2", "HEADING_3": "h3",
    "HEADING_4": "h4", "HEADING_5": "h5", "HEADING_6": "h6",
    "TITLE": "h1", "SUBTITLE": "h2",
}


def _run_spans(paragraph: dict) -> list[tuple[int, int, dict]]:
    spans = []
    offset = 0
    for r in paragraph["runs"]:
        run_len = len(r["text"])
        spans.append((offset, offset + run_len, r))
        offset += run_len
    return spans


def _render_plain(text: str, spans: list[tuple[int, int, dict]], start: int, end: int) -> str:
    """Render [start,end) theo offset Python trong text, giữ bold/link ĐÃ CÓ SẴN trong run gốc."""
    out = []
    for r_start, r_end, r in spans:
        s, e = max(start, r_start), min(end, r_end)
        if s >= e:
            continue
        chunk = html.escape(text[s:e])
        if r["link_url"]:
            chunk = f'<a href="{html.escape(r["link_url"])}">{chunk}</a>'
        if r.get("italic"):
            chunk = f"<em>{chunk}</em>"
        if r["bold"]:
            chunk = f"<strong>{chunk}</strong>"
        out.append(chunk)
    return "".join(out)


def render_paragraph(paragraph: dict, placements: list[dict]) -> tuple[str, str]:
    tag = _HEADING_TAGS.get(paragraph["named_style"], "p")
    text = paragraph["text"]
    spans = _run_spans(paragraph)
    ordered = sorted(placements, key=lambda pl: pl["text_start"])

    pieces = []
    cursor = 0
    for pl in ordered:
        if pl["text_start"] > cursor:
            pieces.append(_render_plain(text, spans, cursor, pl["text_start"]))
        anchor_html = html.escape(pl["matched_text"])
        pieces.append(
            f'<a href="{html.escape(pl["target_url"])}" target="_blank" rel="noopener">'
            f"<strong>{anchor_html}</strong></a>"
        )
        cursor = pl["text_end"]
    if cursor < len(text):
        pieces.append(_render_plain(text, spans, cursor, len(text)))

    inner = "".join(pieces)
    if paragraph.get("bullet"):
        return f"<li>{inner}</li>", "li"
    return f"<{tag}>{inner}</{tag}>", tag


def render_html(doc_structure: dict, placements: list[dict]) -> str:
    by_paragraph: dict[int, list[dict]] = {}
    for pl in placements:
        by_paragraph.setdefault(pl["paragraph_index"], []).append(pl)

    lines = []
    in_list = False
    for p in doc_structure["paragraphs"]:
        rendered, tag = render_paragraph(p, by_paragraph.get(p["index"], []))
        if tag == "li":
            if not in_list:
                lines.append("<ul>")
                in_list = True
        elif in_list:
            lines.append("</ul>")
            in_list = False
        lines.append(rendered)
    if in_list:
        lines.append("</ul>")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc-structure", required=True)
    parser.add_argument("--placements", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    doc_structure = json.loads(Path(args.doc_structure).read_text(encoding="utf-8"))
    placements = json.loads(Path(args.placements).read_text(encoding="utf-8"))

    common.emit({"ok": True, "html": render_html(doc_structure, placements)}, out=args.out)


if __name__ == "__main__":
    main()

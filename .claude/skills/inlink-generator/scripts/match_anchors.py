"""Tìm mọi occurrence HỢP LỆ của từng anchor trong nội dung bài — xác định (deterministic),
KHÔNG quyết định. Claude đọc output này để chọn occurrence phù hợp ngữ cảnh nhất cho mỗi
anchor (script không tự chọn).

Đảm bảo:
- Bỏ heading và mọi range đã có link sẵn khỏi vùng có thể match.
- target_url đã tồn tại như 1 link trong bài -> already_present, không tìm thêm.
- Anchor dài xử lý trước, chiếm span trước -> anchor ngắn là substring của anchor dài
  (VD "iPhone 18" trong "iPhone 18 Pro") không thể giành lại span đã bị chiếm.
- Word-boundary Unicode-aware, so không phân biệt hoa/thường, không sửa text gốc.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common


def eligible_ranges(paragraph: dict) -> list[tuple[int, int]]:
    """Trả list (start,end) theo offset Python trong paragraph['text'] KHÔNG bị link cũ chiếm."""
    text = paragraph["text"]
    p_start = paragraph["start_index"]
    covered = []
    for r in paragraph["runs"]:
        if r["link_url"]:
            covered.append((r["start_index"] - p_start, r["end_index"] - p_start))
    covered.sort()

    free = []
    cursor = 0
    for s, e in covered:
        if s > cursor:
            free.append((cursor, s))
        cursor = max(cursor, e)
    if cursor < len(text):
        free.append((cursor, len(text)))
    return free


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc-structure", required=True, help="JSON từ fetch_doc_structure.py")
    parser.add_argument(
        "--candidates", required=True,
        help='JSON list [{"anchor_text": "...", "target_url": "..."}] — Claude đã suy ra + xác nhận với user',
    )
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    doc = json.loads(Path(args.doc_structure).read_text(encoding="utf-8"))
    candidates = json.loads(Path(args.candidates).read_text(encoding="utf-8"))

    paragraphs = [p for p in doc["paragraphs"] if not p["is_heading"]]

    warnings = []
    seen_anchor_url: dict[str, str] = {}
    for c in candidates:
        key = c["anchor_text"].strip().lower()
        if key in seen_anchor_url and seen_anchor_url[key] != c["target_url"]:
            warnings.append(
                f"Anchor '{c['anchor_text']}' xuất hiện với 2 URL đích khác nhau: "
                f"{seen_anchor_url[key]} và {c['target_url']}"
            )
        seen_anchor_url[key] = c["target_url"]

    existing_by_url = {}
    for link in doc.get("existing_links", []):
        existing_by_url.setdefault(link["url"], link)

    results = []
    for c in candidates:
        existing = existing_by_url.get(c["target_url"])
        results.append({
            "anchor_text": c["anchor_text"],
            "target_url": c["target_url"],
            "already_present": bool(existing),
            "existing_location": existing,
            "occurrences": [],
        })

    # Candidate dài xử lý trước để chiếm span trước candidate ngắn là substring của nó — xử lý
    # bởi common.find_non_overlapping_matches(), gọi lại mỗi đoạn/mỗi vùng eligible riêng (các
    # đoạn văn độc lập về toạ độ nên không cần giữ "claimed" chung xuyên suốt các đoạn).
    active_candidates = [c for c, r in zip(candidates, results) if not r["already_present"]]
    by_key = {(r["anchor_text"], r["target_url"]): r for r in results}

    for p in paragraphs:
        for f_start, f_end in eligible_ranges(p):
            segment = p["text"][f_start:f_end]
            for m in common.find_non_overlapping_matches(segment, active_candidates):
                m_start, m_end = f_start + m["start"], f_start + m["end"]
                r = by_key[(m["anchor_text"], m["target_url"])]
                doc_start = p["start_index"] + common.utf16_len(p["text"][:m_start])
                doc_end = p["start_index"] + common.utf16_len(p["text"][:m_end])
                r["occurrences"].append({
                    "paragraph_index": p["index"],
                    "text_start": m_start,
                    "text_end": m_end,
                    "start_index": doc_start,
                    "end_index": doc_end,
                    "matched_text": p["text"][m_start:m_end],
                    "context_before": p["text"][max(0, m_start - 60):m_start],
                    "context_after": p["text"][m_end:m_end + 60],
                    "paragraph_has_existing_link": any(rn["link_url"] for rn in p["runs"]),
                })

    for r in results:
        r["occurrences"].sort(key=lambda o: o["start_index"])

    for r in results:
        r["not_found"] = (not r["already_present"]) and (not r["occurrences"])

    common.emit({"ok": True, "results": results, "warnings": warnings}, out=args.out)


if __name__ == "__main__":
    main()

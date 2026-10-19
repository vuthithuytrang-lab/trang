"""Ghi bold+link vào Google Doc thật qua batchUpdate, sau khi:
1. So revisionId hiện tại của Doc với revision đã dùng để fetch cấu trúc (an toàn kép: vừa
   tự so sánh để báo lỗi tiếng Việt rõ ràng, vừa gửi kèm writeControl.requiredRevisionId để
   Google tự chặn atomic nếu có ai sửa Doc đúng lúc submit).
2. So lại text hiện có tại từng range với matched_text đã tìm được — placement nào lệch thì
   BỎ QUA riêng placement đó (không abort cả batch).

Chỉ set textStyle (không chèn/xoá ký tự) nên không cần tính lại index giữa các request
trong cùng batch.

Input placements: list [{anchor_text, target_url, paragraph_index, start_index, end_index,
matched_text, ...}] — chính là các occurrence Claude đã chọn, copy nguyên từ output của
match_anchors.py (giữ đủ field) rồi thêm target_url nếu chưa có.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common
from auth import find_credential


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc-id", required=True, help="Link Google Doc hoặc ID trần")
    parser.add_argument("--placements", required=True, help="File JSON danh sách placement Claude đã chọn")
    parser.add_argument("--expected-revision", required=True, help="revision_id lấy từ fetch_doc_structure.py")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--highlight-paragraphs", action="store_true",
        help="Bôi vàng toàn bộ đoạn văn chứa placement (dễ soát lại đã chèn ở đâu), ngoài bold+link ở đúng anchor",
    )
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    found = find_credential()
    if not found:
        common.fail(
            "Chưa có credential đủ quyền (Sheets + Docs). Chạy auth.py (auto_oauth) trước."
        )
    label, creds = found
    svc = common.docs_service(creds)

    try:
        doc_id = common.extract_doc_id(args.doc_id)
    except ValueError as e:
        common.fail(str(e))

    placements = json.loads(Path(args.placements).read_text(encoding="utf-8"))
    if not placements:
        common.fail("File placements rỗng — không có gì để ghi.")

    from googleapiclient.errors import HttpError

    fresh = svc.documents().get(
        documentId=doc_id, suggestionsViewMode="PREVIEW_WITHOUT_SUGGESTIONS"
    ).execute()
    current_revision = fresh.get("revisionId")
    if current_revision != args.expected_revision:
        common.fail(
            "doc_changed_since_fetch: Doc đã bị sửa từ lúc lấy cấu trúc tới giờ, index có thể "
            "lệch. Chạy lại fetch_doc_structure.py + match_anchors.py rồi chọn placement lại.",
            expected_revision=args.expected_revision,
            current_revision=current_revision,
        )

    paragraphs_by_index = {p["index"]: p for p in common.flatten_document(fresh)}

    requests = []
    applied = []
    skipped = []
    for pl in placements:
        para = paragraphs_by_index.get(pl["paragraph_index"])
        if para is None:
            skipped.append({**pl, "reason": "paragraph_index_not_found"})
            continue
        rel_start = pl["start_index"] - para["start_index"]
        rel_end = pl["end_index"] - para["start_index"]
        actual_text = common.utf16_slice(para["text"], rel_start, rel_end)
        expected_text = pl.get("matched_text", "")
        if actual_text.strip().lower() != expected_text.strip().lower():
            skipped.append({**pl, "reason": "text_mismatch_at_index", "actual_text": actual_text})
            continue
        requests.append({
            "updateTextStyle": {
                "range": {"startIndex": pl["start_index"], "endIndex": pl["end_index"]},
                "textStyle": {"bold": True, "link": {"url": pl["target_url"]}},
                "fields": "bold,link",
            }
        })
        applied.append(pl)

    if args.highlight_paragraphs:
        highlighted_paragraphs = {pl["paragraph_index"] for pl in applied}
        for p_idx in highlighted_paragraphs:
            para = paragraphs_by_index[p_idx]
            requests.append({
                "updateTextStyle": {
                    "range": {
                        "startIndex": para["start_index"],
                        "endIndex": para["start_index"] + common.utf16_len(para["text"]),
                    },
                    "textStyle": {
                        "backgroundColor": {"color": {"rgbColor": {"red": 1, "green": 1, "blue": 0}}}
                    },
                    "fields": "backgroundColor",
                }
            })

    if args.dry_run:
        common.emit({
            "ok": True,
            "dry_run": True,
            "would_apply": len(requests),
            "requests": requests,
            "skipped": skipped,
        }, out=args.out)
        return

    if not requests:
        common.emit({
            "ok": True,
            "applied": 0,
            "skipped": skipped,
            "note": "Không có placement hợp lệ để ghi.",
        }, out=args.out)
        return

    try:
        svc.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": requests,
                "writeControl": {"requiredRevisionId": current_revision},
            },
        ).execute()
    except HttpError as e:
        common.fail(
            f"Ghi Doc thất bại (có thể Doc vừa bị sửa đúng lúc submit): {e}",
            expected_revision=current_revision,
        )

    after = svc.documents().get(documentId=doc_id, fields="revisionId").execute()

    common.emit({
        "ok": True,
        "applied": len(applied),
        "applied_placements": applied,
        "skipped": skipped,
        "revision_before": current_revision,
        "revision_after": after.get("revisionId"),
        "doc_url": f"https://docs.google.com/document/d/{doc_id}/edit",
    }, out=args.out)


if __name__ == "__main__":
    main()

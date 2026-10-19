"""Chèn 1 đoạn văn MỚI, ngắn, vào Doc để có chỗ hợp ngữ cảnh gắn anchor không có sẵn trong bài
gốc (fallback khi match_anchors.py trả not_found). Chỉ dùng sau khi Claude đã tự viết đoạn text
phù hợp ngữ cảnh và đã xác nhận với user — KHÔNG tự động chèn hàng loạt không hỏi.

Khác apply_links.py: có insertText (chèn ký tự, làm lệch index phần sau) — nhưng vì mọi
updateTextStyle ở đây chỉ áp lên chính đoạn VỪA chèn (offset tính từ --insert-index, biết
trước), không đụng gì ở sau, nên không cần tính lại index của phần còn lại của Doc.
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
    parser.add_argument(
        "--insert-index", required=True, type=int,
        help="Vị trí chèn (UTF-16 index) — thường là start_index của 1 đoạn văn hiện có, để đoạn mới chèn ngay trước đoạn đó",
    )
    parser.add_argument("--text", required=True, help="Nội dung đoạn mới (không cần \\n cuối, script tự thêm)")
    parser.add_argument(
        "--candidates", required=True,
        help='JSON list [{"anchor_text": "...", "target_url": "..."}] cần gắn trong đoạn mới',
    )
    parser.add_argument("--expected-revision", required=True, help="revision_id lấy từ fetch_doc_structure.py")
    parser.add_argument("--dry-run", action="store_true")
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

    candidates = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    spans = common.find_non_overlapping_matches(args.text, candidates)
    if not spans:
        common.fail(
            "Không anchor nào khớp trong đoạn text mới — kiểm tra lại câu chữ đã viết đúng anchor chưa.",
            text=args.text,
        )

    from googleapiclient.errors import HttpError

    fresh = svc.documents().get(
        documentId=doc_id, suggestionsViewMode="PREVIEW_WITHOUT_SUGGESTIONS"
    ).execute()
    current_revision = fresh.get("revisionId")
    if current_revision != args.expected_revision:
        common.fail(
            "doc_changed_since_fetch: Doc đã bị sửa từ lúc lấy cấu trúc tới giờ, index có thể "
            "lệch. Chạy lại fetch_doc_structure.py rồi thử lại.",
            expected_revision=args.expected_revision,
            current_revision=current_revision,
        )

    text_to_insert = args.text.rstrip("\n") + "\n"
    insert_end = args.insert_index + common.utf16_len(text_to_insert)

    requests = [
        {
            "insertText": {
                "location": {"index": args.insert_index},
                "text": text_to_insert,
            }
        },
        {
            # Đoạn mới luôn là văn bản thường — chặn rủi ro kế thừa style HEADING nếu vị trí
            # chèn nằm ngay trước/trong 1 đoạn heading.
            "updateParagraphStyle": {
                "range": {"startIndex": args.insert_index, "endIndex": insert_end},
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "fields": "namedStyleType",
            }
        },
        {
            # Luôn bôi vàng toàn bộ đoạn mới chèn — đây là NỘI DUNG MỚI (không phải chữ có sẵn
            # được định dạng lại), BTV/KTS cần thấy ngay để soát trước khi đăng.
            "updateTextStyle": {
                "range": {"startIndex": args.insert_index, "endIndex": insert_end},
                "textStyle": {
                    "backgroundColor": {"color": {"rgbColor": {"red": 1, "green": 1, "blue": 0}}}
                },
                "fields": "backgroundColor",
            }
        },
    ]
    for sp in spans:
        start = args.insert_index + common.utf16_len(args.text[:sp["start"]])
        end = args.insert_index + common.utf16_len(args.text[:sp["end"]])
        requests.append({
            "updateTextStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "textStyle": {"bold": True, "link": {"url": sp["target_url"]}},
                "fields": "bold,link",
            }
        })

    if args.dry_run:
        common.emit({
            "ok": True,
            "dry_run": True,
            "text_to_insert": text_to_insert,
            "spans": spans,
            "requests": requests,
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
            f"Chèn đoạn mới thất bại (có thể Doc vừa bị sửa đúng lúc submit): {e}",
            expected_revision=current_revision,
        )

    after = svc.documents().get(documentId=doc_id, fields="revisionId").execute()

    common.emit({
        "ok": True,
        "inserted_text": text_to_insert,
        "spans": spans,
        "revision_before": current_revision,
        "revision_after": after.get("revisionId"),
        "doc_url": f"https://docs.google.com/document/d/{doc_id}/edit",
    }, out=args.out)


if __name__ == "__main__":
    main()

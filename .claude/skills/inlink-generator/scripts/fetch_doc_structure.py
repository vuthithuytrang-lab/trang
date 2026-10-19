"""Đọc cấu trúc 1 Google Doc qua Docs API — trả list đoạn văn kèm heading/link/index,
để match_anchors.py tìm vị trí và apply_links.py ghi lại đúng range. Dùng
suggestionsViewMode=PREVIEW_WITHOUT_SUGGESTIONS để lấy index của bản đã chốt (bỏ suggestion
đang treo) — index chuẩn để ghi; suggestion đang treo (nếu có) chỉ được phát hiện qua 1 lần
fetch phụ (view mặc định), không dùng để tính index."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common
from auth import find_credential


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc-id", required=True, help="Link Google Doc hoặc ID trần")
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

    from googleapiclient.errors import HttpError

    try:
        doc = svc.documents().get(
            documentId=doc_id, suggestionsViewMode="PREVIEW_WITHOUT_SUGGESTIONS"
        ).execute()
    except HttpError as e:
        msg = str(e)
        if "SERVICE_DISABLED" in msg or "accessNotConfigured" in msg:
            common.fail(
                "Docs API chưa được bật cho Google Cloud project này. Bật tại: "
                "https://console.cloud.google.com/apis/library/docs.googleapis.com rồi thử lại.",
                doc_id=doc_id,
            )
        status = getattr(e.resp, "status", None)
        if status == 404:
            common.fail(f"Không tìm thấy Doc với ID '{doc_id}'. Kiểm tra lại link.", doc_id=doc_id)
        if status == 403:
            common.fail(
                f"Không có quyền đọc Doc này. Share quyền Editor cho account đã OAuth ({label}).",
                doc_id=doc_id,
            )
        common.fail(f"Lỗi Docs API: {msg}", doc_id=doc_id)

    has_pending_suggestions = False
    try:
        raw = svc.documents().get(documentId=doc_id).execute()
        has_pending_suggestions = common.has_suggestions(raw.get("body", {}))
    except Exception:
        pass  # check phụ, không chặn luồng chính nếu lỗi

    paragraphs = common.flatten_document(doc)
    links = common.existing_links_from(paragraphs)

    common.emit({
        "ok": True,
        "doc_id": doc_id,
        "title": doc.get("title", ""),
        "revision_id": doc.get("revisionId"),
        "has_pending_suggestions": has_pending_suggestions,
        "paragraphs": paragraphs,
        "existing_links": links,
    }, out=args.out)


if __name__ == "__main__":
    main()

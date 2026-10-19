"""Quét mọi tab trong Google Sheet kế hoạch content, tìm dòng nào tham chiếu tới link
Google Doc đầu vào (so cả giá trị hiển thị và hyperlink của từng cell — không đoán trước
cột nào chứa link). KHÔNG diễn giải cấu trúc cột — nhiệm vụ đó để Claude làm ở bước sau,
vì mỗi tab trong sheet này trình bày anchor/URL theo cách khác nhau."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common
from auth import find_credential


def get_tabs(svc, sheet_id: str) -> list[dict]:
    meta = svc.spreadsheets().get(
        spreadsheetId=sheet_id,
        fields="sheets.properties(sheetId,title,gridProperties)",
    ).execute()
    return meta.get("sheets", [])


def fetch_grids(svc, sheet_id: str, tabs: list[dict]) -> list[dict]:
    """1 batch call kéo formattedValue + hyperlink của mọi cell, mọi tab đưa vào."""
    ranges = []
    for t in tabs:
        props = t["properties"]
        title = props["title"]
        grid = props.get("gridProperties", {})
        rows = grid.get("rowCount", 1000)
        cols = grid.get("columnCount", 50)
        ranges.append(f"'{title}'!A1:{common.col_letter(cols)}{rows}")

    result = svc.spreadsheets().get(
        spreadsheetId=sheet_id,
        ranges=ranges,
        includeGridData=True,
        fields="sheets(properties(title,sheetId),data(rowData(values(formattedValue,hyperlink))))",
    ).execute()
    return result.get("sheets", [])


def _grid_values(sheet: dict) -> list[list[dict]]:
    row_data = (sheet.get("data") or [{}])[0].get("rowData", [])
    grid = []
    for row in row_data:
        cells = row.get("values", [])
        grid.append([
            {"value": c.get("formattedValue", "") or "", "hyperlink": c.get("hyperlink")}
            for c in cells
        ])
    return grid


def find_matches(sheets: list[dict], doc_id: str, context_before: int = 15,
                  context_after: int = 2, header_rows: int = 3) -> list[dict]:
    matches = []
    for sheet in sheets:
        title = sheet["properties"]["title"]
        gid = sheet["properties"]["sheetId"]
        grid = _grid_values(sheet)

        for r_idx, row in enumerate(grid):
            for c_idx, cell in enumerate(row):
                if doc_id in cell["value"] or (cell["hyperlink"] and doc_id in cell["hyperlink"]):
                    win_start = max(0, r_idx - context_before)
                    win_end = min(len(grid), r_idx + context_after + 1)
                    matches.append({
                        "tab_title": title,
                        "sheet_gid": gid,
                        "matched_row_number": r_idx + 1,
                        "matched_cell": {
                            "column_letter": common.col_letter(c_idx + 1),
                            "value": cell["value"],
                            "hyperlink": cell["hyperlink"],
                        },
                        "header_hint_rows": {
                            "start_row": 1,
                            "rows": [[c["value"] for c in r] for r in grid[:header_rows]],
                        },
                        "window_rows": {
                            "start_row": win_start + 1,
                            "rows": [[c["value"] for c in r] for r in grid[win_start:win_end]],
                        },
                    })
    return matches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc-url", required=True, help="Link hoặc ID của Google Doc cần tìm anchor")
    parser.add_argument("--sheet-id", default=common.DEFAULT_SHEET_ID,
                        help="ID Google Sheet kế hoạch content (mặc định lấy từ biến môi trường INLINK_SHEET_ID)")
    parser.add_argument("--full-tab", default=None, help="Bỏ qua tìm match, dump toàn bộ 1 tab theo tên")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    if not args.sheet_id:
        common.fail(
            "Chưa có Sheet kế hoạch content. Truyền --sheet-id <ID> hoặc đặt biến môi trường INLINK_SHEET_ID."
        )

    found = find_credential()
    if not found:
        common.fail(
            "Chưa có credential đủ quyền (Sheets + Docs). Chạy auth.py (auto_oauth) trước."
        )
    label, creds = found
    svc = common.sheets_service(creds)

    try:
        doc_id = common.extract_doc_id(args.doc_url)
    except ValueError as e:
        common.fail(str(e))

    tabs = get_tabs(svc, args.sheet_id)

    if args.full_tab:
        target = next((t for t in tabs if t["properties"]["title"] == args.full_tab), None)
        if not target:
            common.fail(
                f"Không tìm thấy tab '{args.full_tab}' trong sheet.",
                available_tabs=[t["properties"]["title"] for t in tabs],
            )
        sheets_data = fetch_grids(svc, args.sheet_id, [target])
        grid = _grid_values(sheets_data[0])
        common.emit({
            "ok": True,
            "tab_title": args.full_tab,
            "rows": [[c["value"] for c in row] for row in grid],
        }, out=args.out)
        return

    sheets_data = fetch_grids(svc, args.sheet_id, tabs)
    matches = find_matches(sheets_data, doc_id)

    common.emit({
        "ok": True,
        "credential": label,
        "doc_id": doc_id,
        "tabs_scanned": len(tabs),
        "matches": matches,
    }, out=args.out)


if __name__ == "__main__":
    main()

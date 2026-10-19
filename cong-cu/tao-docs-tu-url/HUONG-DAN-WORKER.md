# Worker brief — inserting internal links into Techcombank articles (Docs files)

You are an SEO + banking content expert. For each row assigned to you, produce one final HTML file with
**every** anchor from the sheet inserted. You do NOT upload, do NOT write to the sheet, do NOT edit the website.

## Your working directory
`$D` = the batch directory you are given (e.g. `.../pil/b08/`). It already has: `blocks.py chen.py soat.py prep.py
map.py fetch.sh build.py rows.json` and folders `raw-goc/ raw/ tgt/ out/ final/`. `tgt/` already holds cached target pages.
Always run Python with `python3 -I` and pass `$D/` (with trailing slash) as the first argument.

## Steps per batch
1. `rows.json` = list of rows: `row, B (source URL), F/G (exchange-rate anchor + URL), I (approved suggestion), pairs [[anchor, url], ...]`.
2. Write `$D/urls.txt`: one line per row `r<row> <B>`. Download each source: `bash $D/fetch.sh <B> $D/raw-goc/r<row>.html`,
   then `cp` into `raw/`. Download every target URL not already in `tgt/`: `bash $D/fetch.sh <url> $D/tgt/<last-path-segment>.html`.
   fetch.sh already rewrites to www + browser UA + retries. A 403/404/"Không tìm thấy" → report the row as an error, skip it.
3. `python3 -I $D/prep.py $D/raw/r*.html` then `cd <repo>/cong-cu/tao-docs-tu-url && SP=$D/ python3 build.py`
   (build.py reads `$D/urls.txt`; ignore its keyword output). A row printed as `product` (no article body) → report, skip.
4. Read target pages (title, meta, H2s) to know what each target is about. `python3 -I $D/map.py $D/ $D/out/r<row>.html`
   prints numbered blocks with body-% position and existing links. Block indices `i` in the plan refer to THIS numbering.
5. Write `$D/plan.json` = `{ "r<row>": [ops...] }` and `$D/targets.json` = `{ "r<row>": [[anchor, url-last-segment], ...] }`
   (all pairs, NOT including the F-G exchange-rate pair). Run `python3 -I $D/chen.py $D/` (must print OK for every op) and
   `python3 -I $D/soat.py $D/`. Fix and re-run until clean.
6. Coverage check — every sheet URL (G and every pair URL) must have a link in `final/r<row>.html` (new or pre-existing).

## Op types (see examples in `$D/example-plan.json`)
- `tygia` — the F-G pair when column I has text after "Sau khi chèn:". Apply VERBATIM: `before` = text after "Trước khi chèn:",
  `after` = text after "Sau khi chèn:", `anchor` = F, `url` = G (always G, even if the link inside cell I differs → mention it).
  `i` = the block containing the before-text (it may be only part of a paragraph/bullet). If not found → do NOT insert elsewhere;
  report "không tìm thấy câu gốc". If column I has no suggestion → treat the F-G pair like any other pair (rules below).
- `phrase` — link an exact existing phrase in block `i` (`anchor` exactly as in the sheet; only proper-name capitalisation may change).
- `sentence` — append ONE short sentence (containing the anchor) to existing paragraph `i`.
- `xemthem` — new line after block `i`: `sentence` must start with ">>> " (rendered bold+italic, TCB style).
- `doanmoi` — new paragraph (≥2 sentences) after block `i`.
- `vietlai` — LIGHTLY rewrite ONE existing sentence so the anchor sits naturally inside it (same format as `tygia`:
  `before` = exact existing sentence/clause, `after` = rewritten version containing the anchor, `anchor`, `url`, `i`).
  Keep the original meaning, facts and length (± a few words). Use this when the article already talks about the topic
  but not with the exact anchor wording — it reads far more naturally than bolting on a new sentence.
- `dacolink` — the source article ALREADY links to that exact target URL in block `i` AND the link text is EXACTLY the sheet anchor:
  keep it, `slug` = url last segment; chen.py highlights it and adds a red note.
- `chuyenlink` — the article links to the target URL but with DIFFERENT link text: chen.py removes that link and links the exact
  anchor instead (`anchor`, `url`, `slug`; add `sentence` containing the anchor if the phrase is not already in block `i`).
- ANCHOR TEXT MUST BE THE SHEET TEXT VERBATIM (only proper-name capitalisation may change). Final check: each sheet anchor is the
  exact text of a link pointing to its URL.
  (If `i` is a bullet, xemthem/doanmoi are placed after the whole list automatically.)

## Placement rules (priority order)
1. Every sheet anchor gets exactly one link. Prefer `phrase` > `sentence` > `xemthem` > `doanmoi`.
2. Never in headings; never in the first 25% of the body (check soat.py % AFTER all inserts — added text shifts %;
   the approved `tygia` position is exempt); never inside step-by-step instructions or definitions.
3. Choose sentences that genuinely talk about the target topic; not passing mentions or comparisons.
4. Spread links: avoid two links in one paragraph or in adjacent paragraphs (count pre-existing links). If impossible, allow it
   and list it under "gần nhau". Good xemthem/doanmoi spots: after an image caption at the end of a section, after a list,
   after a section's last paragraph. A sentence about receiving money "bằng USD" is a natural spot for USD-related anchors.
5. Longer phrases first; match whole words only; one link per anchor; keep all original links.
6. Wording: professional, serious, banking tone, Vietnamese with full diacritics. NO numbers, rates, fees, promotions or
   promises that are not in the source article or the target page. Do not claim Techcombank supports a currency unless the
   article says so. Vary sentences — don't copy the same xemthem sentence across articles word for word.

## CONTENT QUALITY — the reviewer's #1 complaint was "chèn gượng ép, chưa tự nhiên"
Act as a senior Vietnamese banking content editor. Every inserted/rewritten text must read as if the original author wrote it.
1. Preference order for naturalness: `phrase` (existing words) > `vietlai` (light rewrite of an existing sentence) >
   `sentence` that CONTINUES the paragraph's own idea > `xemthem` > `doanmoi`. Don't add a sentence when an existing one can carry the anchor.
2. Context fit: put the anchor where the paragraph is ALREADY discussing that need. The inserted sentence must follow logically
   from the sentence before it (cause → consequence, problem → next step, general → specific). If you have to change topic
   to mention the anchor, the spot is wrong — find another one.
3. Reader value: the sentence must tell the reader WHY the linked page helps at this moment (what they will learn/do there),
   in concrete terms tied to the paragraph — not a generic "tham khảo thêm".
4. BANNED formula phrases (they make text sound like ads/SEO filler): "Bên cạnh đó, bạn cũng có thể tham khảo", "Ngoài ra, bạn có
   thể tìm hiểu thêm", "để có thêm thông tin", "để hiểu rõ hơn", "một cách hiệu quả", "vô cùng", "hữu ích", "tham khảo ngay",
   "đừng quên", "chắc chắn", "tại đây". Don't start two inserts in one article with the same words. Max one ">>>" line per section.
5. Match the article's voice: same pronoun (bạn / khách hàng / doanh nghiệp / chủ hộ), same register, same sentence length.
   No exclamation marks, no rhetorical questions, no marketing superlatives.
6. Anchor grammar: the anchor must be a natural grammatical part of the sentence (object/complement), never a dangling label.
   Avoid awkward stacking like "tìm hiểu về tỷ giá USD hôm nay để biết tỷ giá".
7. `xemthem` lines: specific and short, e.g. ">>> Xem thêm: Cách tính thuế thu nhập cá nhân cho người làm tự do" — the anchor
   inside a meaningful title-like phrase, not a full sales sentence.
8. SELF-REVIEW before finishing: for every op, print the sentence before + your text + the sentence after, read it as an editor,
   and ask "would a reader notice this was inserted?". If yes, rewrite or move it. Do this pass for real; mention in notes any
   insert you still find weak.

## File name (title)
Main keyword from the URL slug, rewritten with diacritics to match the article title/H1, first letter upper-case, proper names
capitalised. E.g. `1-man-bang-bao-nhieu-tien-viet` → "1 Man bằng bao nhiêu tiền Việt"; `tien-lao` → "Tiền Lào".

## Report (your final message) — JSON only
```
[{"row": 8, "file": "r8.html", "title": "...", "status": "ok|error",
  "error": "", "tygia": "applied|not_found|no_suggestion", "anchors": N_sheet, "linked": N_in_file,
  "dacolink": ["anchor", ...], "gan_nhau": ["short reason", ...], "notes": ["e.g. link in I differs from G", ...]}]
```

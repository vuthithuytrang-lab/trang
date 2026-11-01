# Brief: draft keyword-density (MĐTK) insertions for ONE Google Doc

You only DRAFT. Never call update_doc, update_values, create_file, or any write tool on Google. Only create files inside the scratchpad folder below.

Scratchpad: /tmp/claude-0/-home-user-trang/2aa864ed-822b-5c26-8a57-8c769aa55fea/scratchpad
Helper scripts there (run with `python3 -I`):
- dump.py <raw.json>            -> prints each paragraph as [start-end] STYLE | text (tables indented)
- count.py <raw.json> <start> kw1 kw2 ...  -> counts each keyword (lowercase exact match, overlapping phrases counted separately) from paragraph index <start> (use the index of the Title line, i.e. skip the "URL:" / "Key tối ưu:" header lines)
- build.py <raw.json> <spec.json> <out.json> -> validates your spec (each `old` must occur exactly once in its paragraph) and builds requests. Must run without error.
Example spec format: see spec3.json / spec5.json in the scratchpad (these are finished, approved examples for other articles — read them to match the style).

## Steps
1. Call mcp__Google_Docs__read_doc (load via ToolSearch "select:mcp__Google_Docs__read_doc") on your doc id. The result is too big and gets saved to a file; copy that file to <scratchpad>/raw<N>.json.
2. dump.py it, read the whole article. The first lines are: URL line, optional "Key tối ưu" lines, then Title line, Meta description line, then the Sapo (intro paragraph), then body. The conclusion ("Kết bài") is the summary paragraph(s) right before the "Khách hàng lưu ý"/contact list.
3. count.py existing occurrences of each keyword (Title+Meta+body).
4. Write <scratchpad>/spec<N>.json: {"keywords":[...all ticked keywords...], "edits":[{"para":<paragraph startIndex>,"old":"<exact unique snippet in that paragraph>","new":"<same snippet with the keyword woven in>"}]}. Several edits may target the same paragraph if their `old` snippets don't overlap.
5. Run build.py to validate. Then re-check final counts mentally.

## Rules the user (an SEO specialist) set — follow strictly
- **RULE 7c (read /home/user/trang/.claude/skills/toi-uu-mdtk/references/7c-sapo-ket-bai.md, it overrides anything conflicting):** in the Sapo paragraph and in the Kết bài paragraph, at most 1–2 keywords may appear as EXACT matches; other keywords there must be expressed in expanded/dispersed form (shared stem stated once, distinguishing parts listed, max 3 list items, each a distinct real section of the article, sentence must carry real information, Sapo and Kết bài must not reuse the same list structure). Everywhere else: max 1 keyword per sentence. The MAIN keyword must always be an exact match (never dispersed) and gets priority for an exact slot. Secondary keywords that don't get an exact slot in Sapo/Kết bài must still appear there in expanded/dispersed form; their remaining exact insertions go to the next positions (Heading 2, Nội dung).
- **NEWEST RULE (overrides target/total rules below):** the target is the number of NEW insertions to make, not a total. Skip a keyword only if it already appears 4+ times. Occurrences that only exist inside a longer keyword phrase do not count as a separate insertion. The task prompt tells you exactly how many MORE insertions each keyword needs and which positions were already used — honour those numbers.
- **POSITION PRIORITY (newest rule, overrides older ones):** the "Vị trí" list is ordered by priority, left = highest. Fill positions in that order until the target total (existing + inserted) is reached, then STOP — do not add to later positions. If a higher position has no factual basis/natural fit, skip it and move to the next. If the keyword already meets the target, insert nothing.
- Exception to the old rule: Kết bài is no longer mandatory; only use it when it comes up in priority order.
- Target = "Số lần" column is the TOTAL. If already >= target, do not insert that keyword.
- Positions ("Vị trí"), in priority order as above (Sapo, Nội dung = body, Kết bài = conclusion summary paragraph, Heading 2, Title, Meta Description). Heading 2: ONLY if an existing H2 section genuinely matches the keyword's meaning; otherwise skip and report it. Never invent a new section.
- INSERT SHORT. Weave the exact keyword phrase into an existing sentence by adding a few words (or replacing 2-3 words). No new long sentences/paragraphs. A short added clause (<= ~12 words) only when weaving is impossible. Long insertions force a costly approval process for the user.
- Exact keyword phrase must appear verbatim (case-insensitive) in `new`.
- NO fabrication: an inserted phrase may only state what the article already says or directly implies. If a keyword has no basis in the article, insert at most where it is a neutral framing (e.g. a question that the next sentence already answers) or skip and report.
- Do not touch: legal quotes (text citing Điều/Khoản/Nghị định/Thông tư, quoted law), numbers/fee figures/formulas/tables of rates, CTA lines, "Khách hàng lưu ý"/"Bạn đọc lưu ý" notes, contact lists, the "(*)" footnote disclaimers, the header lines (URL/Key tối ưu).
- Spread: same keyword's insertions in different sections, roughly 250+ words apart; prefer beginning/middle/end; always include the conclusion when Kết bài is a required position.
- Don't change existing keyword occurrences. Keep Vietnamese diacritics; capitalize proper nouns (Techcombank, Việt Nam).
- Title/Meta: edit the Title line / Meta line paragraphs themselves (keep " | Techcombank" suffix; keep Title roughly ≤ 65 chars and Meta ≤ ~160 chars if possible).

## Report back (concise, plain text)
- also a one-line Vietnamese note (plain words, for the user's sheet) for every keyword that was NOT inserted or is below target, explaining why (e.g. 'Không chèn: bài đã có sẵn 3 lần (cần 2).')
- raw/spec file paths, build.py output line
- per keyword: before count -> after count, positions you inserted into, using ONLY these labels: Title, Meta Description, Sapo, Heading 2, Heading 3, Nội dung, Kết bài
- each edit: old -> new (short)
- anything skipped and why (esp. Heading 2 or no factual basis)

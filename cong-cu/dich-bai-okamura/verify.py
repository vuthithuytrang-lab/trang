"""Soát tab bản dịch sau khi ghi.
Dùng: python3 verify.py DOC.json EN.txt --tab TAB_ID [--src-tab t.0]
Kiểm tra: chữ từng đoạn 2 cột khớp bản dự kiến, số ảnh, link còn /vi/, heading in đậm, dòng trống thừa.
"""
import argparse, json, re, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from build_requests import load, vn_blocks, en_blocks, read_tr


def flat_expected(blocks):
    out = []
    for b in blocks:
        if b['type'] == 'p':
            out.append((''.join(r.get('t', '') for r in b['runs']), sum('img' in r for r in b['runs'])))
        else:
            for row in b['rows']:
                for c in row: out += flat_expected(c)
    return out


def flat_actual(content, issues, side):
    out = []
    for el in content:
        if 'paragraph' in el:
            p = el['paragraph']; t, n = '', 0
            named = p.get('paragraphStyle', {}).get('namedStyleType', '')
            for e in p['elements']:
                if 'textRun' in e:
                    t += e['textRun']['content'].replace('\n', '')
                    st = e['textRun'].get('textStyle', {})
                    url = st.get('link', {}).get('url', '')
                    if side == 'EN' and re.search(r'okamura\.com\.vn/vi(/|$)', url):
                        issues.append(f'[EN] link còn /vi/: {url}')
                    if side == 'EN' and named.startswith('HEADING') and st.get('bold') and e['textRun']['content'].strip():
                        issues.append(f'[EN] heading in đậm: {t[:60]}')
                elif 'inlineObjectElement' in e:
                    n += 1
            out.append((t, n))
        elif 'table' in el:
            for row in el['table']['tableRows']:
                for c in row['tableCells']: out += flat_actual(c['content'], issues, side)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('doc'); ap.add_argument('en')
    ap.add_argument('--tab', required=True); ap.add_argument('--src-tab', default='t.0')
    a = ap.parse_args()
    d = load(a.doc)
    def all_tabs(ts):
        for x in ts:
            yield x; yield from all_tabs(x.get('childTabs', []))
    tabs = {x['tabProperties']['tabId']: x['documentTab'] for x in all_tabs(d['tabs'])}
    src, dst = tabs[a.src_tab], tabs[a.tab]
    objs = src.get('inlineObjects', {})
    vn = vn_blocks(src['body']['content'], objs)
    uri = {k: (v['inlineObjectProperties']['embeddedObject']['imageProperties']['contentUri'],
               v['inlineObjectProperties']['embeddedObject'].get('size')) for k, v in objs.items()}
    en = en_blocks(vn, read_tr(a.en), uri)
    cells = [e for e in dst['body']['content'] if 'table' in e][0]['table']['tableRows'][0]['tableCells']
    issues = []
    for name, exp_blocks, cell in (('VN', vn, cells[0]), ('EN', en, cells[1])):
        exp = flat_expected(exp_blocks)
        act = flat_actual(cell['content'], issues, name)
        # bỏ đoạn trống do bảng con / cuối ô sinh ra
        act_n = [x for x in act if x[0].strip() or x[1]]
        exp_n = [x for x in exp if x[0].strip() or x[1]]
        if len(act_n) != len(exp_n):
            issues.append(f'[{name}] số đoạn: thực tế {len(act_n)} / dự kiến {len(exp_n)}')
        for i, (x, y) in enumerate(zip(act_n, exp_n)):
            if x[0].strip() != y[0].strip():
                issues.append(f'[{name}] đoạn {i} khác chữ:\n   có : {x[0][:120]}\n   cần: {y[0][:120]}')
            if x[1] != y[1]:
                issues.append(f'[{name}] đoạn {i} số ảnh {x[1]} / cần {y[1]}')
        print(f'{name}: {len(act_n)} đoạn, {sum(x[1] for x in act_n)} ảnh')
    if issues:
        print('\n'.join(issues)); sys.exit(1)
    print('OK — khớp hoàn toàn')


if __name__ == '__main__':
    main()

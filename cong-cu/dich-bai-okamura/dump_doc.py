"""In nội dung Google Doc (JSON từ read_doc) thành dạng chữ có đánh dấu định dạng.
Dùng: python3 dump_doc.py DOC.json [--tab TAB_ID]
Ký hiệu: **đậm**  _nghiêng_  [chữ](link)  [IMG id WxH]  {H1}{H2}{H3}  •(bullet)  <C>(căn giữa) <J>(đều 2 bên)
"""
import json, sys

def load(p):
    d = json.load(open(p))
    if 'content' in d and isinstance(d['content'], dict): d = d['content']
    return d

def runs(elems, objs):
    out = ''
    for e in elems:
        if 'textRun' in e:
            tr = e['textRun']; t = tr['content'].replace('\n', ''); st = tr.get('textStyle', {})
            if not t: continue
            if st.get('link'): t = f"[{t}]({st['link'].get('url', st['link'])})"
            if st.get('italic'): t = f"_{t}_"
            if st.get('bold'): t = f"**{t}**"
            out += t
        elif 'inlineObjectElement' in e:
            oid = e['inlineObjectElement']['inlineObjectId']
            emb = objs[oid]['inlineObjectProperties']['embeddedObject']
            sz = emb.get('size', {})
            out += f"[IMG {oid} {round(sz.get('width',{}).get('magnitude',0))}x{round(sz.get('height',{}).get('magnitude',0))}]"
        else:
            out += f"[{list(e.keys())[1] if len(e)>1 else e}]"
    return out

def dump(content, objs, ind=''):
    for el in content:
        if 'paragraph' in el:
            p = el['paragraph']; ps = p.get('paragraphStyle', {})
            nst = ps.get('namedStyleType', 'NORMAL_TEXT')
            tag = {'HEADING_1':'{H1}','HEADING_2':'{H2}','HEADING_3':'{H3}','HEADING_4':'{H4}','TITLE':'{T}'}.get(nst, '')
            al = {'CENTER':'<C>','JUSTIFIED':'<J>','END':'<R>'}.get(ps.get('alignment'), '')
            b = ''
            if 'bullet' in p: b = '  ' * p['bullet'].get('nestingLevel', 0) + '• '
            print(f"{ind}{el['startIndex']}: {tag}{al}{b}{runs(p['elements'], objs)}")
        elif 'table' in el:
            tb = el['table']; print(f"{ind}{el['startIndex']}: <TABLE {tb['rows']}x{tb['columns']}>")
            for ri, row in enumerate(tb['tableRows']):
                for ci, cell in enumerate(row['tableCells']):
                    print(f"{ind}  <cell {ri},{ci}>")
                    dump(cell['content'], objs, ind + '    ')
            print(f"{ind}</TABLE>")

if __name__ == '__main__':
    d = load(sys.argv[1]); want = sys.argv[3] if len(sys.argv) > 3 else None
    def tabs(ts):
        for t in ts:
            yield t; yield from tabs(t.get('childTabs', []))
    for t in tabs(d['tabs']):
        if want and t['tabProperties']['tabId'] != want: continue
        dt = t['documentTab']; print('=== TAB', t['tabProperties']['tabId'], t['tabProperties']['title'])
        dump(dt['body']['content'], dt.get('inlineObjects', {}))

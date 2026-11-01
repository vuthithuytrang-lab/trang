import json,sys
d=json.load(open(sys.argv[1]))
c=d.get('content',d)
print('REV',c['revisionId'],'TITLE',c['title'])
tabs=c.get('tabs')
body=tabs[0]['documentTab']['body'] if tabs else c['body']
def walk(content,pre=''):
    for el in content:
        if 'paragraph' in el:
            p=el['paragraph'];st=p.get('paragraphStyle',{}).get('namedStyleType','')
            t=''.join(r.get('textRun',{}).get('content','') for r in p['elements'])
            hl=any(r.get('textRun',{}).get('textStyle',{}).get('backgroundColor') for r in p['elements'])
            b='•' if 'bullet' in p else ''
            if t.strip(): print(f"{pre}[{el['startIndex']}-{el['endIndex']}] {st[:9]}{b}{' HL' if hl else ''} | {t.rstrip()}")
        elif 'table' in el:
            print(pre+'<TABLE>')
            for r in el['table']['tableRows']:
                for cell in r['tableCells']: walk(cell['content'],pre+'  ')
            print(pre+'</TABLE>')
walk(body['content'])

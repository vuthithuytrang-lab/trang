import json,sys
c=json.load(open(sys.argv[1]))['content'];b=c['tabs'][0]['documentTab']['body']
def w(cs):
  for el in cs:
    if 'paragraph' in el:
      for r in el['paragraph']['elements']:
        tr=r.get('textRun')
        if tr and tr.get('textStyle',{}).get('backgroundColor'): print('  HL',r['startIndex'],repr(tr['content'][:90]))
    elif 'table' in el:
      for r in el['table']['tableRows']:
        for cell in r['tableCells']: w(cell['content'])
w(b['content'])

import json,sys
c=json.load(open(sys.argv[1]))['content'];b=c['tabs'][0]['documentTab']['body'];out=[]
def w(cs):
  for el in cs:
    if 'paragraph' in el:
      for r in el['paragraph']['elements']:
        tr=r.get('textRun')
        if tr and tr.get('textStyle',{}).get('backgroundColor') and tr['content'].endswith('\n'): out.append(r['endIndex']-1)
    elif 'table' in el:
      for r in el['table']['tableRows']:
        for cell in r['tableCells']: w(cell['content'])
w(b['content'])
print(json.dumps([{'updateTextStyle':{'range':{'startIndex':i,'endIndex':i+1},'textStyle':{},'fields':'backgroundColor'}} for i in out]));print(c['revisionId'])

from bs4 import BeautifulSoup
def load(f):
    s=BeautifulSoup(open(f,encoding='utf-8').read(),'lxml')
    bl=[t for t in s.body.find_all(['p','h2','h3','h4','li','table']) if not t.find_parent(['li','table']) and not (t.name=='p' and t.find_parent('p'))]
    return s,bl
def bodypct(bl,start=6):
    body=bl[start:]; tot=sum(len(t.get_text()) for t in body); acc=0; out={}
    for i,t in enumerate(body,start=start):
        out[i]=acc*100/tot; acc+=len(t.get_text())
    return out

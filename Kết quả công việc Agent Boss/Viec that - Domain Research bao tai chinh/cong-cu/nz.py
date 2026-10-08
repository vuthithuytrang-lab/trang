import unicodedata,re
def nz(s):
    s=unicodedata.normalize('NFD',(s or '').lower().replace('đ','d'))
    return ' '.join(re.sub(r'[^a-z0-9%/.,-]',' ',''.join(c for c in s if unicodedata.category(c)!='Mn')).split())

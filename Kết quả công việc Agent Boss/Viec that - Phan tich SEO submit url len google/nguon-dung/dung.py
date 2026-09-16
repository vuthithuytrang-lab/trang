# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phan_a import HEAD, A
from phan_b import B
from phan_c import C
from phan_e import E
from phan_h import H
out = HEAD + A + B + C + E + H
p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'phan-tich-va-outline-submit-url.html')
open(p, 'w', encoding='utf-8').write(out)
print('Da ghi', p, len(out), 'ky tu')

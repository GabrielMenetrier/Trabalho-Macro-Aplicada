from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import *
start=json.loads((H/'cache/design.json').read_text())['common_start'];mask=dates>=pd.Period(start);rows=[]
for universe,ix in [('All',None),('NoBRL',[1,2,3,4,5]),('NoEUR',[0,2,3,4,5])]:
    for mode in ['absolute','relative','zero']:
        ws,_,_,_=make_policies(ix=ix,gate_mode=mode)
        for name in ['Carry','EJR_gate','Gate_price','Equal_modules','Core_satellite']:
            b,_,_=book(ws[name],start);rows.append(dict(universe=universe,gate=mode,name=name,**stats(b,mask)))
save(rows,'hurdle_refinement');print('Hurdle variants',len(rows))

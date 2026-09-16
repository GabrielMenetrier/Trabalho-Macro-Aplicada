from pathlib import Path
import json,re,sys,hashlib
from collections import Counter
import pymupdf as f
import pandas as pd
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;R=H.parent;Q=H/'qa';Q.mkdir(exist_ok=True)
doc=f.open(R/'output/pdf/relatorio_ejr_termos_troca.pdf');assert len(doc)==11
m=pd.read_csv(H/'tables/metrics.csv');checks=[]
def check(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
for i,p in enumerate(doc):
    txt=p.get_text()
    check(f'No broken table command page {i+1}','oprule' not in txt)
    check(f'Nonempty page {i+1}',len(txt)>500)
    for b in p.get_text('blocks'):
        if b[6]==0:check(f'Text within page {i+1}',b[0]>=18 and b[1]>=8 and b[2]<=p.rect.width-18 and b[3]<=p.rect.height-8)
    p.get_pixmap(matrix=f.Matrix(1.4,1.4)).save(Q/f'page-{i+1:02d}.png')
expected=Counter(f'{v:.3f}'.replace('.',',') for v in m[(m.scenario=='main')&(m.period=='all')&m.model.isin(['EJR','TOT_both','COM_both'])].rmse_rw)
actual=Counter(re.findall(r'\b\d+,\d{3}\b',doc[4].get_text()))
check('168 country/aggregate table cells exactly match metrics',actual==expected)
expected=Counter(f'{v:.3f}'.replace('.',',') for v in m[(m.scenario=='main')&(m.period=='all')&(m.country=='POOL')&m.model.isin(['EJR','TOT_both','COM_both'])].rmse_rw)
actual=Counter(re.findall(r'\b\d+,\d{3}\b',doc[0].get_text()))
check('24 executive table cells exactly match metrics',actual==expected)
hashes=json.loads((H/'input_hashes.json').read_text())
check('All frozen inputs preserved',all(hashlib.sha256((R/k).read_bytes()).hexdigest()==v for k,v in hashes.items()))
log=(R/'output/pdf/relatorio_ejr_termos_troca.log').read_text(errors='replace')
check('No missing characters','Missing character' not in log)
for start in range(0,len(doc),6):
    sheet=Image.new('RGB',(1200,1180),'#dfe4e8')
    for j in range(min(6,len(doc)-start)):
        im=Image.open(Q/f'page-{start+j+1:02d}.png');im.thumbnail((390,555));sheet.paste(im,(10+(j%3)*400,20+(j//3)*590))
    sheet.save(Q/f'contact-{start//6+1}.png')
(Q/'checks.json').write_text(json.dumps(dict(passed=True,count=len(checks),pages=len(doc),checks=checks),indent=2))
print('PDF:',len(doc),'pages;',len(checks),'checks passed. All 192 main numeric cells match results.')

from pathlib import Path
import pymupdf as f
import pandas as pd,numpy as np
import re,json,hashlib
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parent;Q=H/'qa';Q.mkdir(exist_ok=True)
doc=f.open(R/'output/pdf/relatorio_ejr_paises_selecionados.pdf');assert len(doc)==11
checks=[]
def check(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
for i,p in enumerate(doc):
    text=p.get_text();check(f'No malformed table commands page {i+1}','oprule' not in text)
    check(f'No empty page {i+1}',len(text)>350)
    for block in p.get_text('blocks'):
        if block[6]==0:check(f'Text contained on page {i+1}',block[0]>=14 and block[1]>=8 and block[2]<=p.rect.width-14 and block[3]<=p.rect.height-8)
    p.get_pixmap(matrix=f.Matrix(1.4,1.4)).save(Q/f'page-{i+1:02d}.png')
log=(R/'output/pdf/relatorio_ejr_paises_selecionados.log').read_text(errors='replace')
check('No missing glyphs','Missing character' not in log)
check('No overfull boxes','Overfull' not in log)
m=pd.read_csv(H/'tables/metrics.csv');gv=pd.read_csv(H/'tables/graph_values.csv')
for page,cc in [(3,'BRL'),(4,'CAD'),(5,'EUR')]:
    text=doc[page].get_text()
    for _,row in gv[gv.country==cc].iterrows():
        check(f'Graph labels reflect RMSE {cc} {row.model}',f'{row.rmse_rw:.3f}' in text)
        check(f'Graph labels reflect adjusted R2 {cc} {row.model}',f'{row.r2_adjusted:.3f}' in text)
        metric=m[(m.h==60)&(m.scenario=='fixed')&(m.country==cc)&(m.model==row.model)].iloc[0]
        check(f'Graph value matches metrics {cc} {row.model}',np.isclose(row.rmse_rw,metric.rmse_rw))
hashes=json.loads((H/'input_hashes.json').read_text())
check('Input files unchanged',all(hashlib.sha256((R/k).read_bytes()).hexdigest()==v for k,v in hashes.items()))
for start in range(0,len(doc),6):
    sheet=Image.new('RGB',(1200,1180),'#dfe4e8')
    for j in range(min(6,len(doc)-start)):
        im=Image.open(Q/f'page-{start+j+1:02d}.png');im.thumbnail((390,555));sheet.paste(im,(10+(j%3)*400,20+(j//3)*590))
    sheet.save(Q/f'contact-{start//6+1}.png')
(Q/'checks.json').write_text(json.dumps(dict(passed=True,count=len(checks),pages=len(doc),checks=checks),indent=2))
print(len(doc),'pages;',len(checks),'PDF checks passed')

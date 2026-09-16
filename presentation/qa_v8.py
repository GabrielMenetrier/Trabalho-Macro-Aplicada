from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E,hashlib
import numpy as np
import pymupdf as f
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];H=R/'presentation';Q=H/'build/qa_v8';Q.mkdir(exist_ok=True)
C=json.loads((H/'content_v8.json').read_text(encoding='utf-8'));D=json.loads((H/'data_v8.json').read_text(encoding='utf-8'))
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
ck('18 main slides plus 7 appendix',len(C['slides'])==25 and C['main_slides']==18)
ck('Under twenty minutes',sum(s['seconds'] for s in C['slides'])==1035)
ck('Appendix outside timing',all(s['seconds']==0 for s in C['slides'][18:]))
ck('Original sources preserved',all(hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256'] for s in D['new_sources']))
z=zipfile.ZipFile(R/'output/presentation/apresentacao_macro_aula_v8_final.pptx');ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
xml={i:E.fromstring(z.read(f'ppt/slides/slide{i}.xml')) for i in range(1,26)}
for i in range(1,26):
    tx=' '.join(t.text or '' for t in xml[i].findall('.//a:t',ns))
    ck(f'Notes slide {i}',f'ppt/notesSlides/notesSlide{i}.xml' in z.namelist())
    ck(f'No monthly-risk optimization or decomposition slide {i}','risco mensal' not in tx.lower() and 'decomposição' not in tx.lower())
    ck(f'Correct title {i}',C['slides'][i-1]['title'] in tx or i==1)
def cells(i):
    return [[[ ''.join(t.text or '' for t in c.findall('.//a:t',ns)) for c in r.findall('a:tc',ns)] for r in tbl.findall('a:tr',ns)] for tbl in xml[i].findall('.//a:tbl',ns)]
def num(v,n=3):return f'{v:.{n}f}'.replace('.',',')
def pct(v):return num(v*100,2)+'%'
palette={'Carry':'15354D','EJR':'0072B2','EJR_TOT_trio':'D55E00','TT_all':'D55E00'}
labels={'Carry':'Juros','EJR':'EJR','EJR_TOT_trio':'EJR + TT','TT_all':'EJR + TT'}
for universe,i in [('six',14),('three',16)]:
    sigs=['Carry','EJR','EJR_TOT_trio'] if universe=='six' else ['Carry','EJR','TT_all']
    entries=[]
    for met in ['Ranking','long60']:
        for sig in sigs:
            r=next(r for r in D[universe+'_table'] if r['scenario']=='Base' and
                (r['variant']==sig and r['metodo']==('Dois pares' if met=='Ranking' else 'Máximo Sharpe — risco de 60 meses') if universe=='six' else r['signal']==sig and r['method']==met))
            for h in [12,60]:entries.append((r['cagr_'+str(h)],met,sig,h,r))
    entries.sort(key=lambda e:-e[0])
    a=cells(i)[0];ck(f'Twelve ranked rows {i}',len(a)==13)
    tr=xml[i].findall('.//a:tbl/a:tr',ns)
    for j,(cagr,met,sig,h,r) in enumerate(entries,1):
        expected=[labels[sig],'Ranking' if met=='Ranking' else 'Máx. Sharpe',str(h)+' meses',pct(cagr),num(r['sharpe_'+str(h)]),pct(r['maxdd_'+str(h)])]
        ck(f'Ranked row {i} {j}',a[j]==expected)
        for col in [0,3]:
            tc=tr[j].findall('a:tc',ns)[col]
            ck(f'Color {i} {j} {col}',palette[sig] in [x.attrib['val'] for x in tc.findall('.//a:srgbClr',ns)])
for i in [13,14,15,16,17]:
    tx=' '.join(t.text or '' for t in xml[i].findall('.//a:t',ns))
    ck(f'Removed auxiliary variants {i}','controle' not in tx.lower() and 'combinado' not in tx.lower())
for row,cc in enumerate(['BRL','EUR','JPY','GBP','CAD','SEK','POOL'],1):
    for col,model in enumerate(['EJR','TOT_both'],1):
        r=next(r for r in D['tt_full'] if r['h']==60 and r['country']==cc and r['model']==model)
        ck(f'Forecast full table {cc} {model}',cells(8)[0][row][col]==num(r['rmse_rw']))
for r in json.loads((H/'build/evidence_audit_v7.json').read_text()):ck('Curve equals table '+str((r['universe'],r['method'],r['signal'],r['hold'])),r['passed'] and abs(r['cagr']-r['table_cagr'])<1e-10)
for i in [10,11,13,15]:
    chartns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
    count=len(xml[i].findall('.//c:chart',chartns));ck(f'Native charts slide {i}',count==(3 if i in [10,11] else 4))
for s in D['new_sources']:ck('Preserved '+s['path'],hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256'])
for name,count in [('apresentacao_macro_aula_v8',25),('guia_apresentacao_macro_v8',30)]:
    doc=f.open(R/f'output/pdf/{name}.pdf');ck(name+' page count',len(doc)==count)
    for i,p in enumerate(doc,1):
        for j,b in enumerate(p.get_text('blocks')):
            if b[6]==0:ck(f'Page bounds {name} {i} {j}',b[0]>=0 and b[1]>=0 and b[2]<=p.rect.width+.1 and b[3]<=p.rect.height+.1)
        p.get_pixmap(matrix=f.Matrix(1.25,1.25)).save(Q/f'{name}-{i:02d}.png')
    for start in range(0,count,4):
        sheet=Image.new('RGB',(1240,1770),'#e3e8eb');draw=ImageDraw.Draw(sheet)
        for j in range(min(4,count-start)):
            pic=Image.open(Q/f'{name}-{start+j+1:02d}.png');pic.thumbnail((610,840));x=5+j%2*620;y=25+j//2*885
            sheet.paste(pic,(x,y));draw.text((x,y-16),str(start+j+1),fill='#15354d')
        sheet.save(Q/f'contact-{name}-{start//4+1}.png')
G=json.loads((H/'build/guide_pages_v8.json').read_text());doc=f.open(R/'output/pdf/guia_apresentacao_macro_v8.pdf')
for i in range(1,26):ck('Guide correspondence '+str(i),f'Slide {i:02d}' in doc[G['mapping'][f'slide{i}']-1].get_text())
ck('Correct paper title',any('Monetary Policy and the Predictability of Nominal Exchange Rates' in p.get_text().replace('\n',' ') for p in doc))
(Q/'checks.json').write_text(json.dumps(dict(passed=True,count=len(checks),checks=checks),indent=2))
print('Passed:',len(checks),'checks; rendered 25 slides and 30 guide pages.')

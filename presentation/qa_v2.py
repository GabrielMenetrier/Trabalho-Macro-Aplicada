"""Check facts, artifact structure, slide/guide correspondence and PDF geometry."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np
import pymupdf as fitz
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];H=R/'presentation';Q=H/'build/qa_v2';Q.mkdir(exist_ok=True)
D=json.loads((H/'data_v2.json').read_text(encoding='utf-8'));C=json.loads((H/'content_v2.json').read_text(encoding='utf-8'))
G=json.loads((H/'build/guide_pages_v2.json').read_text(encoding='utf-8'))
checks=[]
def check(name,ok):
    checks.append({'check':name,'pass':bool(ok)})
    assert ok,name
check('19 minutes, 17 main slides and 2 backups',sum(x['seconds'] for x in C['slides'])==1140 and len(C['slides'])==19 and all(x['seconds']==0 for x in C['slides'][17:]))
for src in D['sources']:check('Source unchanged: '+src['path'],hashlib.sha256((R/src['path']).read_bytes()).hexdigest()==src['sha256'])
check('Carry example includes cross term',abs((1.10*.92-1.03)-(-.018))<1e-12)
check('Replication sample size',len(D['scatter']['x'])==280)
for name in ['Carry','Equal_modules','Cash']:
    rows=[x for x in D['returns'] if x['name']==name];met=next(x for x in D['best'] if x['name']==name)
    v=np.cumprod(1+np.array([x['net'] for x in rows]));peak=np.maximum.accumulate(np.r_[1,v])[1:]
    check('101 equal dates '+name,len(rows)==101 and rows[0]['month']=='2018-04' and rows[-1]['month']=='2026-08')
    check('Chart and reported CAGR '+name,abs(v[-1]**(12/101)-1-met['cagr'])<1e-8)
    check('Chart and reported drawdown '+name,abs(np.min(v/peak-1)-met['maxdd'])<1e-8)
for name in ['Carry','EJR + carry']:
    rows=[x for x in D['initial_returns'] if x['strategy']==name]
    met=next(x for x in D['initial'] if x['strategy']==name)
    v=np.cumprod(1+np.array([x['net'] for x in rows]))
    check('Initial chart dates '+name,len(rows)==198 and rows[0]['month']=='2010-03' and rows[-1]['month']=='2026-08')
    check('Initial chart CAGR '+name,abs(v[-1]**(12/198)-1-met['cagr'])<1e-8)
z=zipfile.ZipFile(R/'output/presentation/apresentacao_macro_aula_v2_final.pptx')
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
slides=[]
for i in range(1,20):
    a=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'));txt=' '.join(t.text or '' for t in a.findall('.//a:t',ns));slides.append(txt)
    check(f'Notes present for slide {i}',f'ppt/notesSlides/notesSlide{i}.xml' in z.namelist())
check('PPTX has 5 editable charts',len([n for n in z.namelist() if '/charts/chart' in n and n.endswith('.xml')])==5)
check('Native chart workbooks embedded',len([n for n in z.namelist() if n.startswith('ppt/embeddings/') and n.endswith('.xlsx')])==5)
check('Nine native tables',sum(z.read(f'ppt/slides/slide{i}.xml').count(b'<a:tbl>') for i in range(1,20))==9)
for num,tokens in {3:['-1,808','0,883'],4:['1,039','1,076','1,096','1,037','1,072','1,115','0,964','0,916','0,884','0,792','0,793','0,816'],6:['4,11%','2,73%','0,60','0,31','Markowitz','50 pb','out/1999'],9:['0,890','1,630','Origem ='],10:['2,20','2,08'],12:['5,78%','5,94%','48%','-1,43%'],13:['5,96%','5,94%','5,77%','6 meses','12 meses','24 meses','12m'],14:['out/1999–jan/2013','jan/2011–dez/2016'],19:['4,18%','2,04%','-4,02%']}.items():
    for t in tokens:check(f'Displayed evidence slide {num}: {t}',t in slides[num-1])
for name,count in [('apresentacao_macro_aula_v2',19),('guia_apresentacao_macro_v2',G['pages'])]:
    doc=fitz.open(R/f'output/pdf/{name}.pdf');check(name+' page count',len(doc)==count)
    for i,page in enumerate(doc,1):
        for b in page.get_text('blocks'):
            if b[6]==0:check(f'{name} page {i} text inside bounds',b[0]>=0 and b[1]>=0 and b[2]<=page.rect.width+.1 and b[3]<=page.rect.height+.1)
        page.get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(Q/f'{name}-{i:02d}.png')
    check(name+' bookmarks',len(doc.get_toc())>=17)
guide=fitz.open(R/'output/pdf/guia_apresentacao_macro_v2.pdf')
for i in range(19):
    start=G['mapping'][f'slide{i+1}']-1
    end=G['mapping'][f'slide{i+2}']-1 if i<18 else G['mapping']['glossario1']-1
    txt=' '.join(guide[j].get_text() for j in range(start,end));check(f'Guide aligns with slide {i+1}',f'Slide {i+1:02d}' in txt)
    for heading in ['Conceitos que','Como ler','Fala sugerida','Pergunta provável']:
        check(f'Guide slide {i+1}: {heading}',heading in txt)
for file in ['apresentacao_macro_aula_v2','guia_apresentacao_macro_v2']:
    ims=[Q/f'{file}-{i:02d}.png' for i in range(1,(19 if file.startswith('apresentacao') else G['pages'])+1)]
    for start in range(0,len(ims),6):
        sheet=Image.new('RGB',(1000,1440),'#e3e8eb');draw=ImageDraw.Draw(sheet)
        for j,im in enumerate(ims[start:start+6]):
            pic=Image.open(im).convert('RGB');pic.thumbnail((484,440))
            x=8+(j%2)*500;y=25+(j//2)*480
            sheet.paste(pic,(x,y));draw.text((x,y-16),im.stem,fill='#15354d')
        sheet.save(Q/f'contact-{file}-{start//6+1}.png')
(Q/'checks.json').write_text(json.dumps({'checks':checks,'count':len(checks),'passed':all(x['pass'] for x in checks)},ensure_ascii=False,indent=2),encoding='utf-8')
print(len(checks),'checks passed; all PDF pages rendered.')

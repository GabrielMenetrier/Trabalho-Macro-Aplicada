"""Render all report pages and contact sheets; collect text/layout diagnostics."""
from pathlib import Path
import json
import pymupdf
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'tmp/pdf_review';OUT.mkdir(exist_ok=True,parents=True)
doc=pymupdf.open(ROOT/'output/pdf/relatorio.pdf')
summary=[]; thumbs=[]
for i,page in enumerate(doc):
    p=OUT/f'page_{i+1:02}.png';page.get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(p)
    im=Image.open(p).convert('RGB');im.thumbnail((300,425))
    cell=Image.new('RGB',(320,455),'#dbe3eb');cell.paste(im,((320-im.width)//2,10))
    ImageDraw.Draw(cell).text((10,438),f'Page {i+1}',fill='black');thumbs.append(cell)
    text=page.get_text(); bounds=[]
    for block in page.get_text('dict')['blocks']:
        if 'lines' not in block:continue
        for line in block['lines']:
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<20 or x1>page.rect.width-15 or y0<10 or y1>page.rect.height-10:bounds.append(span['text'])
    summary.append({'page':i+1,'chars':len(text),'edge_violations':bounds,'replacement_chars':text.count('\ufffd')})
for start in range(0,len(thumbs),6):
    sheet=Image.new('RGB',(960,910),'white')
    for j,im in enumerate(thumbs[start:start+6]):sheet.paste(im,((j%3)*320,(j//3)*455))
    sheet.save(OUT/f'contact_{start//6+1}.png')
(OUT/'qa.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
(OUT/'full_text.txt').write_text('\n\n'.join(p.get_text() for p in doc),encoding='utf-8')
print(json.dumps(summary,indent=2))

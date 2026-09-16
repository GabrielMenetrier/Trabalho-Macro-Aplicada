from pathlib import Path
import json
import pymupdf
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];D=R/'tmp/pdfs/trade_extension';D.mkdir(parents=True,exist_ok=True)
doc=pymupdf.open(R/'output/pdf/relatorio_termos_troca.pdf');summary=[];thumbs=[]
for i,p in enumerate(doc):
    path=D/f'page_{i+1:02d}.png';p.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(path)
    im=Image.open(path);im.thumbnail((397,562));thumb=Image.new('RGB',(417,595),'#e7eced');thumb.paste(im,((417-im.width)//2,10));ImageDraw.Draw(thumb).text((15,577),str(i+1),fill='black');thumbs.append(thumb)
    bad=[list(b[:4]) for b in p.get_text('blocks') if b[0]<35 or b[2]>p.rect.width-35 or b[1]<15 or b[3]>p.rect.height-15]
    txt=p.get_text();summary.append(dict(page=i+1,chars=len(txt),top=txt[:110],edge_violations=bad))
for j in range(0,len(thumbs),6):
    canvas=Image.new('RGB',(1251,1190),'white')
    for k,im in enumerate(thumbs[j:j+6]):canvas.paste(im,((k%3)*417,(k//3)*595))
    canvas.save(D/f'contact_{j//6+1}.png')
(D/'qa.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf8')
print('Pages:',len(doc),'Edge issues:',sum(bool(x['edge_violations']) for x in summary))
for x in summary:print(x['page'],x['chars'],x['top'].replace('\n',' ').encode('ascii','replace').decode()[:100])

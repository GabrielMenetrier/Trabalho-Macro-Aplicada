from pathlib import Path
import json
import pymupdf
from PIL import Image, ImageOps, ImageDraw
R=Path(__file__).resolve().parents[1]; P=R/'output/pdf/relatorio_secundario.pdf'; D=R/'tmp/pdfs/secondary';D.mkdir(parents=True,exist_ok=True)
doc=pymupdf.open(P); summary=[];thumbs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False); name=D/f'page_{i+1:02d}.png';pix.save(name)
    img=Image.open(name);img.thumbnail((397,562));thumb=Image.new('RGB',(417,595),'#e7eced');thumb.paste(img,((417-img.width)//2,10));ImageDraw.Draw(thumb).text((15,577),f'{i+1}',fill='black');thumbs.append(thumb)
    blocks=page.get_text('blocks');bad=[list(b[:4]) for b in blocks if b[0]<35 or b[2]>page.rect.width-35 or b[1]<15 or b[3]>page.rect.height-15]
    txt=page.get_text();summary.append(dict(page=i+1,chars=len(txt),top=txt[:120],bottom=txt[-150:],edge_violations=bad))
for j in range(0,len(thumbs),6):
    canvas=Image.new('RGB',(1251,1190),'white')
    for k,thumb in enumerate(thumbs[j:j+6]):canvas.paste(thumb,((k%3)*417,(k//3)*595))
    canvas.save(D/f'contact_{j//6+1}.png')
(D/'qa.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('Pages:',len(doc),'Edge violations:',sum(bool(x['edge_violations']) for x in summary))
for x in summary:print(x['page'],x['chars'],x['top'].replace('\n',' ')[:95].encode('ascii','replace').decode())

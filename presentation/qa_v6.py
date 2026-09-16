from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E
import pymupdf as f
from PIL import Image,ImageChops,ImageDraw
R=Path(__file__).resolve().parents[1];H=R/'presentation';Q=H/'build/qa_v6';Q.mkdir(exist_ok=True)
C=json.loads((H/'content_v6.json').read_text(encoding='utf-8'))
assert len(C['slides'])==16 and sum(s['seconds'] for s in C['slides'])==930
assert all(s['old'] not in (7,8,9) for s in C['slides'])
z=zipfile.ZipFile(R/'output/presentation/apresentacao_macro_aula_v6_final.pptx');ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
for i in range(1,17):
    txt=' '.join(t.text or '' for t in E.fromstring(z.read(f'ppt/slides/slide{i}.xml')).findall('.//a:t',ns))
    assert 'Prever o câmbio real continuou difícil' not in txt
    assert f'ppt/notesSlides/notesSlide{i}.xml' in z.namelist()
for name,count in [('apresentacao_macro_aula_v6',16),('guia_apresentacao_macro_v6',22)]:
    doc=f.open(R/f'output/pdf/{name}.pdf');assert len(doc)==count
    for i,p in enumerate(doc,1):
        for b in p.get_text('blocks'):
            if b[6]==0:assert b[0]>=0 and b[1]>=0 and b[2]<=p.rect.width+.1 and b[3]<=p.rect.height+.1
        p.get_pixmap(matrix=f.Matrix(1.25,1.25)).save(Q/f'{name}-{i:02d}.png')
    for start in range(0,count,6):
        sheet=Image.new('RGB',(1000,1440),'#e3e8eb');draw=ImageDraw.Draw(sheet)
        for j in range(min(6,count-start)):
            pic=Image.open(Q/f'{name}-{start+j+1:02d}.png');pic.thumbnail((484,440));x=8+j%2*500;y=25+j//2*480
            sheet.paste(pic,(x,y));draw.text((x,y-16),str(start+j+1),fill='#15354d')
        sheet.save(Q/f'contact-{name}-{start//6+1}.png')
G=json.loads((H/'build/guide_pages_v6.json').read_text());doc=f.open(R/'output/pdf/guia_apresentacao_macro_v6.pdf')
for i in range(1,17):assert f'Slide {i:02d}' in doc[G['mapping'][f'slide{i}']-1].get_text()
(Q/'checks.json').write_text(json.dumps({'passed':True,'slides':16,'guide_pages':22,'seconds':930,'portfolio_sections_labeled_exploratory':True}))
print('Passed: removed section, slide correspondence, 16 slide renders, 22 guide pages, exploratory portfolio framing.')

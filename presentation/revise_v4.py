"""Remove real exchange-rate forecasting section from classroom materials."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];H=R/'presentation'
C=json.loads((H/'content_v3.json').read_text(encoding='utf-8'))
C['slides']=[s for s in C['slides'] if s['old']!=9]
C['main_count']=16
for s in C['slides']:
    if s['old']==8:s['transition']='A previsão nominal ampliada é instável. A próxima pergunta é se a informação ajuda a controlar a exposição ao carry.'
    if s['old']==15:
        s['concepts']=s['concepts'].replace(', e prever a mudança real continua difícil','')
        s['caution']='Encerre no slide 16. Os slides 17 e 18 são apoio para perguntas e ficam fora dos 17 minutos e 55 segundos.'
(H/'content_v4.json').write_text(json.dumps(C,ensure_ascii=False,indent=2),encoding='utf-8')
(H/'data_v4.json').write_bytes((H/'data_v3.json').read_bytes())
t=(H/'build/deck_v3.mjs').read_text(encoding='utf-8').replace('_v3','_v4')
start=t.index('{\n const s=slide(9,');end=t.index('{\n const s=slide(10,',start)
t=t[:start]+t[end:]
t=t.replace('physical>17','physical>16').replace('mainSlides:17','mainSlides:16')
(H/'build/deck_v4.mjs').write_text(t,encoding='utf-8')
t=(H/'build_pdfs_v3.py').read_text(encoding='utf-8').replace('_v3','_v4')
replacements={
 '17 slides principais':'16 slides principais',
 '19 minutos':'17 minutos e 55 segundos',
 'aproximadamente um minuto de margem':'aproximadamente dois minutos de margem',
 'slides 8–10':'slides 8–9',
 'slides 11–16':'slides 10–15',
 'conclusão do slide 17':'conclusão do slide 16',
 'slides 18 e 19':'slides 17 e 18',
 "'Previsão real ampliada',":'',
 "C['slides'][:17]":"C['slides'][:16]",
 'No 12, priorize':'No 11, priorize',
 'No 13, compare':'No 12, compare',
 'No 15, explique':'No 14, explique',
 'slides 6, 11 e 16':'slides 6, 10 e 15',
 "['10','Extensão comercial: relatorio_termos_troca.pdf. Tabelas em trade_extension/tables.'],":'',
 "['11–16 e 19'":"['10–15 e 18'",
 "['18','Equações":"['17','Equações",
 'PDF slides: 19 pages.':'PDF slides: 18 pages.',
}
for a,b in replacements.items():t=t.replace(a,b)
(H/'build_pdfs_v4.py').write_text(t,encoding='utf-8')

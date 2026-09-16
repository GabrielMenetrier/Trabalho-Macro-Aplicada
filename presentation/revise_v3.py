"""Expand slide 4 to every currency; preserve the remaining presentation."""
from pathlib import Path
import csv,json
R=Path(__file__).resolve().parents[1]; H=R/'presentation'
D=json.loads((H/'data_v2.json').read_text(encoding='utf-8'))
with (R/'output/tables/forecast_accuracy.csv').open(encoding='utf-8',newline='') as f:
    D['horizons']=[{**r,'h':int(r['h']),'rmse_ratio':float(r['rmse_ratio'])} for r in csv.DictReader(f) if r['model']=='ejr']
(H/'data_v3.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
C=json.loads((H/'content_v2.json').read_text(encoding='utf-8')); s=C['slides'][3]
s['reading']='A tabela mostra cada moeda e o agregado das seis moedas, usando a mesma especificação EJR agrupada. BRL é real, EUR euro, JPY iene, GBP libra, CAD dólar canadense e SEK coroa sueca. Todas são avaliadas contra USD. Valores abaixo de 1 aparecem em verde e indicam menor RMSE que prever nenhuma mudança. O agregado reúne os erros do painel; não é uma soma nem uma média simples das razões individuais. Em cinco anos, o Brasil tem 0,792 e o agregado 1,037. Em oito anos, 0,816 e 1,115. Os períodos de origem de cada horizonte estão no rodapé e são diferentes entre as linhas.'
s['speech']=s['speech'].replace('As janelas da última coluna são diferentes.','As janelas indicadas no rodapé são diferentes.')
s['training']='Treino expansivo desde out/1999; mínimo de 60 origens maduras por moeda e alvos de treino até t−1. Origens avaliadas: 1 ano jan/2010–ago/2025; 2 anos jan/2010–ago/2024; 3 anos jan/2010–ago/2023; 5 anos jan/2010–ago/2021; 7 anos nov/2011–ago/2019; 8 anos nov/2012–ago/2018. Alvos realizados até ago/2026.'
(H/'content_v3.json').write_text(json.dumps(C,ensure_ascii=False,indent=2),encoding='utf-8')
deck=(H/'build/deck_v2.mjs').read_text(encoding='utf-8').replace('_v2','_v3')
start=deck.index(" const ranges=",deck.index("const s=slide(4,"))
end=deck.index('\n}\n{',start)
deck=deck[:start]+''' const currencies=['BRL','EUR','JPY','GBP','CAD','SEK','POOL'];
 const values=[['Horizonte','BRL','EUR','JPY','GBP','CAD','SEK','Agregado'],...[12,24,36,60,84,96].map(h=>[`${h/12} ano${h===12?'':'s'}`,...currencies.map(c=>num(data.horizons.find(x=>x.h===h&&x.country===c).rmse_ratio,3))])];
 const tab=table(s,values,{y:212,h:321,widths:[190,130,130,130,130,130,130,182],font:26});
 tab.cells.block({row:0,column:0,rowCount:7,columnCount:8}).assign({margins:{left:12,right:8,top:5,bottom:5}});
 for(let r=1;r<7;r++)for(let c=1;c<8;c++){
  const value=data.horizons.find(x=>x.h===[12,24,36,60,84,96][r-1]&&x.country===currencies[c-1]).rmse_ratio;
  tab.getCell(r,c).text.style={typeface:F,fontSize:26,bold:value<1||c===7,color:value<1?teal:navy};
 }
 method(s,'Origens — 1 ano: jan/2010–ago/2025; 2 anos: jan/2010–ago/2024; 3 anos: jan/2010–ago/2023.\\n5 anos: jan/2010–ago/2021; 7 anos: nov/2011–ago/2019; 8 anos: nov/2012–ago/2018.\\nTreino expansivo desde out/1999; mínimo 60 origens maduras por moeda; alvos de treino até t−1.\\nAlvos avaliados até ago/2026. Inclinação comum às moedas; agregado reúne os erros do painel.',548,97,19);
 foot(s,'Fonte: forecast_accuracy.csv e timing_audit.csv. EJR agrupado; moedas contra USD. Erro relativo = RMSE / RMSE de nenhuma mudança.');'''+deck[end:]
(H/'build/deck_v3.mjs').write_text(deck,encoding='utf-8')
for source,target in [('build_pdfs_v2.py','build_pdfs_v3.py'),('qa_v2.py','qa_v3.py')]:
    t=(H/source).read_text(encoding='utf-8').replace('_v2','_v3')
    (H/target).write_text(t,encoding='utf-8')

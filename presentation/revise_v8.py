"""Editorial revision: rank final portfolios by CAGR, remove auxiliary signals."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent
C=json.loads((H/'content_v7.json').read_text(encoding='utf-8'))
D=json.loads((H/'data_v7.json').read_text(encoding='utf-8'))
for s in C['slides']:
    key=s['old']
    if key in ['six_wealth','six_table','three_wealth','three_table']:
        six=key.startswith('six')
        specific=('Nas seis moedas, EJR usa estimação nas seis. EJR + TT substitui as previsões de BRL/EUR/CAD pela extensão estimada no trio. JPY/GBP/SEK mantêm EJR original. A comparação também muda a amostra de estimação dessas três previsões.' if six else 'Só BRL, EUR e CAD entram nas posições. Tanto EJR quanto EJR + TT são estimados no trio. O teto é 50% por moeda.')
        s['core']=('Juros apresenta os maiores retornos das alternativas exibidas.' if six else 'O maior retorno é 3,29% a.a.: EJR, máximo Sharpe e nova escolha a cada 12 meses.')
        s['concepts']=specific+' Todos os sinais incluem o diferencial de juros. Ranking usa pesos iguais nas moedas escolhidas pelo retorno esperado. Máximo Sharpe otimiza pesos usando também a covariância dos retornos acumulados em 60 meses. Ambos permitem nova escolha a cada 12 ou 60 meses, com manutenção mensal dos pesos-alvo.'
        if key.endswith('table'):
            s['reading']='As 12 alternativas estão ordenadas do maior para o menor retorno anual composto. Cada linha é uma combinação de sinal, método e intervalo entre escolhas. As colunas separam retorno, Sharpe e queda máxima. A cor identifica o sinal, igual aos gráficos.'
            s['speech']='Primeiro leio o sinal, depois o método e o intervalo entre escolhas. Ranking seleciona moedas por retorno esperado e usa pesos iguais. Máximo Sharpe ajusta os pesos pelo retorno esperado e pelo risco em cinco anos. A coluna de escolha informa quando recalculamos a carteira. O retorno anual composto determina a ordem das linhas.'
        else:
            s['speech']=('Nas seis moedas, acrescentar a previsão não supera os juros nas alternativas mostradas.' if six else 'No trio, EJR com máximo Sharpe e escolha anual tem o maior retorno. Termos de troca não transformam a melhora da previsão brasileira em melhor carteira.')+' Azul escuro representa juros, azul claro acrescenta EJR, laranja acrescenta termos de troca. Cinza é caixa USD.'
    if key=='book_rules':
        s['qa']='Por que ranking com escolha em 60 meses difere de máximo Sharpe com risco de 60 meses e escolha em 60 meses? O ranking usa pesos iguais e ordena o retorno esperado. O máximo Sharpe usa também o risco e as correlações para escolher pesos. O calendário de escolha é igual, mas o método é diferente.'
(H/'content_v8.json').write_text(json.dumps(C,ensure_ascii=False,indent=2),encoding='utf-8')
(H/'data_v8.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
src=(H/'build/new_slides_v7.mjs').read_text(encoding='utf-8')
src=src.replace("['Carry','EJR','EJR_trio','EJR_TOT_trio']:['Carry','EJR','TT_all','Matched']", "['Carry','EJR','EJR_TOT_trio']:['Carry','EJR','TT_all']")
src=src.replace("Controle e TT substituem só BRL/EUR/CAD. No ranking, EJR e controle coincidem.","TT entra em BRL/EUR/CAD, com estimação no trio. JPY/GBP/SEK mantêm EJR original.")
src=src.replace("Combinado: TT no BRL, EJR em EUR/CAD. No ranking 60m, Juros e EJR coincidem.","EJR e TT estimados no trio. No ranking com escolha a cada 60m, Juros e EJR coincidem.")
start=src.index('function portfolioTable(universe){')
end=src.index("wealthSlides('six');",start)
src=src[:start]+'''function portfolioTable(universe){
 const six=universe==='six';const s=slide(universe+'_table','Ordem: maior para menor retorno anual composto. Retornos em USD, líquidos dos custos assumidos.');
 const sigs=six?['Carry','EJR','EJR_TOT_trio']:['Carry','EJR','TT_all'];
 const entries=[];
 for(const met of ['Ranking','long60'])for(const sig of sigs){
  const r=six?data.six_table.find(r=>r.scenario==='Base'&&r.metodo===(met==='Ranking'?'Dois pares':'Máximo Sharpe — risco de 60 meses')&&r.variant===sig):data.three_table.find(r=>r.scenario==='Base'&&r.method===met&&r.signal===sig);
  for(const h of [12,60])entries.push({met,sig,h,cagr:r['cagr_'+h],sharpe:r['sharpe_'+h],dd:r['maxdd_'+h]});
 }
 entries.sort((a,b)=>b.cagr-a.cagr);
 const rows=[['Sinal','Método','Nova escolha','Retorno a.a.','Sharpe','Queda máx.'],...entries.map(e=>[labs[e.sig],e.met==='Ranking'?'Ranking':'Máx. Sharpe',e.h+' meses',fmt(e.cagr),num(e.sharpe,3),fmt(e.dd)])];
 const t=table(s,rows,{y:207,h:377,widths:[193,230,193,190,151,195],font:21});
 t.cells.block({row:0,column:0,rowCount:13,columnCount:6}).assign({margins:{left:10,right:6,top:2,bottom:2}});
 for(let i=1;i<13;i++)for(let c of [0,3])t.getCell(i,c).text.style={typeface:F,fontSize:21,color:pal[entries[i-1].sig],bold:true};
 method(s,'Ranking: pesos iguais. Máx. Sharpe: pesos otimizados pelo risco dos retornos acumulados em 60m.\\n'+(six?'TT no trio, reestimado. Demais moedas: EJR original. Teto 25%, 2 compras e 2 vendas no ranking.':'Modelos estimados no trio. Teto 50%, 1 compra e 1 venda no ranking.'),594,49,18);
 foot(s,commonFoot+'\\nFonte: horizon_tests/tables/'+(six?'with_terms_of_trade.csv':'restricted_table.csv')+'. Nova escolha = recalcular moedas e pesos.');
}
'''+src[end:]
src=src.replace("...['Carry','EJR','TT_all','Matched'].map", "...['Carry','EJR','TT_all'].sort((a,b)=>get(b,'Base').cagr_12-get(a,'Base').cagr_12).map")
src=src.replace('rowCount:5,columnCount:3','rowCount:4,columnCount:3')
# Match the remaining signal colors in the cost comparison too.
needle="t.cells.block({row:0,column:0,rowCount:4,columnCount:3}).assign({margins:{left:16,right:12,top:4,bottom:4}});"
src=src.replace(needle,needle+"\n for(let i=1;i<4;i++)t.getCell(i,0).text.style={typeface:F,fontSize:26,color:pal[['EJR','Carry','TT_all'][i-1]],bold:true};")
(H/'build/new_slides_v8.mjs').write_text(src,encoding='utf-8')
builder=(H/'build_builder_v7.py').read_text(encoding='utf-8').replace('_v7','_v8').replace("??'v7'","??'v8'")
(H/'build_builder_v8.py').write_text(builder,encoding='utf-8')
pdf=(H/'build_pdfs_v7.py').read_text(encoding='utf-8').replace('_v7','_v8')
pdf=pdf.replace(' Violeta, nas seis moedas: EJR controle, com reestimação no trio. Verde, no trio: TT no Brasil e EJR no euro/Canadá.','')
pdf=pdf.replace('Cada célula traz uma tripla: retorno anual composto / Sharpe / queda máxima. Exemplo: 3,29% / 0,393 / −13,31% significa retorno composto de 3,29% ao ano, Sharpe de 0,393 e pior queda desde um pico de 13,31%.','As linhas estão ordenadas do maior para o menor retorno anual composto. Sinal, método e intervalo entre escolhas aparecem em colunas próprias, seguidos por retorno, Sharpe e queda máxima. Exemplo: EJR, máximo Sharpe, escolha a cada 12 meses, retorno 3,29% a.a., Sharpe 0,393 e queda máxima de 13,31%.')
pdf=pdf.replace('explique a tripla e destaque uma linha','explique as colunas e destaque a primeira linha')
(H/'build_pdfs_v8.py').write_text(pdf,encoding='utf-8')
print('Prepared v8 sources without changing research outputs.')

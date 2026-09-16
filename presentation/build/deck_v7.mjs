import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile,FileBlob} from '@oai/artifact-tool';
const root=path.resolve('../..');
const skill='C:/Users/Pichau/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations';
const runtime='C:/Users/Pichau/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const data=JSON.parse(await fs.readFile('../data_v7.json','utf8'));
const content=JSON.parse(await fs.readFile('../content_v7.json','utf8'));
const entry=n=>content.slides.find(s=>s.old===n);
const tableOwners=new Set(),chartOwners=new Set();
const p=Presentation.create({slideSize:{width:1280,height:720}});
const F='Arial', navy='#15354D',teal='#007F7B',gray='#5B6770',red='#A14338', light='#E8EEF2';
const fmt=(x,n=2)=>(100*x).toLocaleString('pt-BR',{minimumFractionDigits:n,maximumFractionDigits:n})+'%';
const num=(x,n=2)=>x.toLocaleString('pt-BR',{minimumFractionDigits:n,maximumFractionDigits:n});
const b=name=>data.best.find(x=>x.name===name);
function text(s,t,x,y,w,h,size=28,color=navy,bold=false){
 const a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 a.text=t;a.text.style={typeface:F,fontSize:size,color,bold,autoFit:'none',verticalAlignment:'middle'};
 return a;
}
function slide(n,sub=''){
 const s=p.slides.add();s.background.fill='#FFFFFF';
 const physical=p.slides.items.length;
 text(s,entry(n).title,64,40,1152,104,39,navy,true);
 if(sub)text(s,sub,64,141,1152,55,23,gray);
 text(s,String(physical).padStart(2,'0')+(physical>18?' apoio':''),1120,670,120,26,16,gray);
 const c=entry(n);
 s.speakerNotes.textFrame.setText(`Tempo sugerido: ${c.seconds} segundos.\nIdeia central: ${c.core}\n\nFALA\n${c.speech}\n\nCONCEITOS\n${c.concepts}\n\nLEITURA\n${c.reading}\n\nTREINO E AVALIAÇÃO\n${c.training??'Conceito ou síntese dos testes apresentados.'}\n\nCUIDADO\n${c.caution}\n\nPERGUNTA\n${c.qa}\n\nTRANSIÇÃO\n${c.transition}\n\nFONTES\n${c.sources.join('\n')}\nEJR: https://doi.org/10.1093/restud/rdaa024`);
 return s;
}
function foot(s,t){text(s,t,64,651,1070,46,16,gray);}
function method(s,t,y=565,h=78,size=20){text(s,t,64,y,1152,h,size,gray);}
function takeaway(s,t,y=577){text(s,t,64,y,1152,64,28,teal,true);}
function table(s,values,{x=64,y=225,w=1152,h=290,widths,font=27}={}){
 tableOwners.add(p.slides.items.indexOf(s)+1);
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,columnWidths:widths});
 t.borders.assign({fill:'#FFFFFF',width:0});
 t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({textStyle:{typeface:F,fontSize:27,color:navy},fill:'#FFFFFF',margins:{left:16,right:12,top:10,bottom:10},anchor:'center'});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
  const cell=t.getCell(r,c);
  cell.text.style={typeface:F,fontSize:r===0?Math.min(25,font):font,color:r===0?'#FFFFFF':navy,bold:r===0||c===0};
  cell.fill=r===0?navy:(r%2===0?light:'#FFFFFF');
 }
 return t;
}
function chart(s,type,c){
 chartOwners.add(p.slides.items.indexOf(s)+1);
 // Excel stores 15 significant digits. Keep display data at 12; raw evidence stays in data.json.
 c.series=c.series.map(v=>({...v,values:v.values?.map(x=>Number(x.toPrecision(12))),xValues:v.xValues?.map(x=>Number(x.toPrecision(12))),valuesFormatCode:v.valuesFormatCode??'0.00'}));
 const axis={textStyle:{typeface:F,fontSize:22,fill:gray},line:{fill:'#AAB6BE',width:1},majorGridlines:{fill:'#E6EBEF',width:1}};
 const ch=s.charts.add(type,{chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF',chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},...c,
 xAxis:{...axis,majorGridlines:null,...c.xAxis},yAxis:{...axis,...c.yAxis},legend:{position:'bottom',textStyle:{typeface:F,fontSize:22,fill:navy},...c.legend}});
 applyPresentationChartFont(ch,{fontFamily:F});return ch;
}
// 1. Minimal academic cover.
{
 const s=p.slides.add();s.background.fill='#FFFFFF';
 text(s,'Câmbio real, termos de troca\ne carry trade',70,151,1130,180,58,navy,true);
 text(s,content.subtitle,74,354,1110,95,30,gray);
 text(s,'Macroeconomia Aplicada · EPGE/FGV · 2026',74,547,1100,50,25,teal);
 text(s,'01',1150,670,90,26,16,gray);
 const c=content.slides[0];s.speakerNotes.textFrame.setText(`Tempo: ${c.seconds}s\n${c.speech}\n\n${c.concepts}\nFontes: ${c.sources.join('; ')}\nhttps://doi.org/10.1093/restud/rdaa024`);
}
{
 const s=slide(2,'Eichenbaum, Johannsen e Rebelo (EJR, 2021), Review of Economic Studies');
 text(s,'Câmbio real = cotação × preços dos EUA / preços locais',64,215,1152,67,34,teal,true);
 text(s,'Uma moeda relativamente barata pode se ajustar pela cotação\nou pela inflação relativa.',64,312,1150,104,31);
 text(s,'Nos países com metas de inflação do artigo, o câmbio real\najuda a prever o nominal futuro e prevê pouco a inflação.',64,445,1150,104,31);
 foot(s,'EJR, seção 3.3: ganho agregado acima de 2 anos; destaque para 4 e 6 anos. Replicação parcial da relação preditiva, sem o DSGE.');
}
{
 const s=slide(3,'Brasil, horizonte de oito anos. Ajuste dentro da amostra.');
 const a=data.replication.find(x=>x.h===96),x=data.scatter.x,y=data.scatter.y;
 const n=x.length,mx=x.reduce((a,b)=>a+b)/n,my=y.reduce((a,b)=>a+b)/n;
 const beta=x.reduce((v,t,i)=>v+(t-mx)*(y[i]-my),0)/x.reduce((v,t)=>v+(t-mx)**2,0),alpha=my-beta*mx;
 const lo=Math.min(...x),hi=Math.max(...x);
 chart(s,'scatter',{position:{left:54,top:210,width:835,height:367},hasLegend:false,scatterOptions:{style:'lineWithMarkers'},
 series:[{name:'Origens mensais',xValues:x,values:y,fill:teal,line:{fill:'none',width:0},marker:{symbol:'circle',size:4}},
 {name:'Ajuste linear',xValues:[lo,hi],values:[alpha+beta*lo,alpha+beta*hi],line:{fill:red,width:3},marker:{symbol:'none'}}],
 xAxis:{title:'Desvio do câmbio real (log)',numberFormatCode:'0.0'},yAxis:{title:'Variação nominal (log)',min:-1,max:1.6,majorUnit:.5,numberFormatCode:'0.0'}});
 text(s,'Inclinação',931,235,275,42,25,gray);text(s,num(a.beta,3),931,280,275,70,50,navy,true);
 text(s,'R² do ajuste',931,382,275,42,25,gray);text(s,num(a.r2,3),931,427,275,70,50,navy,true);
 takeaway(s,'Replicar uma relação histórica ainda não prova capacidade de previsão.',585);
 foot(s,'Fonte: replicação da aula 8. 280 origens, jan/1995–abr/2018. Resultados até abr/2026. Horizontes sobrepostos.');
}
{
 const s=slide(4,'Erro relativo a nenhuma mudança. Abaixo de 1, a previsão melhora.');
 const currencies=['BRL','EUR','JPY','GBP','CAD','SEK','POOL'];
 const values=[['Horizonte','BRL','EUR','JPY','GBP','CAD','SEK','Agregado'],...[12,24,36,60,84,96].map(h=>[`${h/12} ano${h===12?'':'s'}`,...currencies.map(c=>num(data.horizons.find(x=>x.h===h&&x.country===c).rmse_ratio,3))])];
 const tab=table(s,values,{y:212,h:321,widths:[190,130,130,130,130,130,130,182],font:26});
 tab.cells.block({row:0,column:0,rowCount:7,columnCount:8}).assign({margins:{left:12,right:8,top:5,bottom:5}});
 for(let r=1;r<7;r++)for(let c=1;c<8;c++){
  const value=data.horizons.find(x=>x.h===[12,24,36,60,84,96][r-1]&&x.country===currencies[c-1]).rmse_ratio;
  tab.getCell(r,c).text.style={typeface:F,fontSize:26,bold:value<1||c===7,color:value<1?teal:navy};
 }
 method(s,'Origens — 1 ano: jan/2010–ago/2025; 2 anos: jan/2010–ago/2024; 3 anos: jan/2010–ago/2023.\n5 anos: jan/2010–ago/2021; 7 anos: nov/2011–ago/2019; 8 anos: nov/2012–ago/2018.\nTreino expansivo desde out/1999; mínimo 60 origens maduras por moeda; alvos de treino até t−1.\nAlvos avaliados até ago/2026. Inclinação comum às moedas; agregado reúne os erros do painel.',548,97,19);
 foot(s,'Fonte: forecast_accuracy.csv e timing_audit.csv. EJR agrupado; moedas contra USD. Erro relativo = RMSE / RMSE de nenhuma mudança.');
}
{
 const s=slide(5,'Aplicação própria: previsão de 60 meses convertida em sinal mensal. Não é uma carteira do artigo.');
 table(s,[['Carry por juros','Carry com previsão cambial'],['Diferencial de juros','Diferencial de juros\n+ valorização prevista']],{y:226,h:156,widths:[530,622]});
 text(s,'Retorno aproximado = diferencial de juros + valorização cambial − custos',64,414,1152,73,30,teal,true);
 text(s,'Exemplo: ativo +10%, financiamento 3%, moeda −8%.\nResultado exato antes de custos: 1,10 × 0,92 − 1,03 = −1,8%.',64,516,1152,98,29);
 foot(s,'Exemplo hipotético. Simulação com aplicações curtas e financiamento. O cálculo exato inclui interação entre juros e câmbio.');
}
{
 const s=slide(6,'Mar/2010–ago/2026. Este backtest testa a aplicação mensal; não rejeita a previsão de longo prazo.');
 const c=data.initial.find(x=>x.strategy==='Carry'),e=data.initial.find(x=>x.strategy==='EJR + carry');
 table(s,[['Métrica','Carry por juros','Carry + previsão'],['Retorno anual composto',fmt(c.cagr),fmt(e.cagr)],['Volatilidade anual',fmt(c.vol),fmt(e.vol)],['Sharpe',num(c.sharpe),num(e.sharpe)],['Queda máxima',fmt(c.maxdd),fmt(e.maxdd)]],{y:208,h:275,widths:[545,305,302]});
 method(s,'Ranking com 2 compras e 2 vendas, 25% por ponta. Sem otimização de Markowitz.\nPrevisão 60m; revisão mensal; execução t+1. Backtest: mar/2010–ago/2026.\nTreino inicial: origens out/1999–dez/2004, alvos até dez/2009. Depois, expansivo mensal.\nCustos: BRL 10 pb, SEK 3 pb, demais 2 pb por notional; spread extra na venda 50 pb a.a.',501,140,20);
 foot(s,'Fonte: portfolio_metrics.csv, timing_audit.csv e src/models.py. Custos em entrada, rebalanceamento e saída. Caixa USD incluído.');
}
// Inserted into the existing slide builder to retain its typography and native objects.
const pal={Carry:'#15354D',EJR:'#0072B2',EJR_trio:'#7B61A8',EJR_TOT_trio:'#D55E00',TT_all:'#D55E00',Matched:'#009E73',Cash:'#A0A8AE'};
const labs={Carry:'Juros',EJR:'EJR',EJR_trio:'EJR controle',EJR_TOT_trio:'EJR + TT',TT_all:'EJR + TT',Matched:'Combinado'};
const fmetric=(rows,h,country,model)=>rows.find(r=>r.h===h&&r.country===country&&r.model===model).rmse_rw;
const commonFoot='Backtest: mar/2010–fev/2025. Previsão: 60m. Treino inicial: out/1999–dez/2004, alvos até dez/2009; depois, expansivo.';
const ttFoot='Previsão: 60m. Origens: jan/2010–ago/2021. Alvos: jan/2015–ago/2026. Treino expansivo desde out/1999, alvos até t−1.';
{
 const s=slide('tt_model','A variável prevista continua sendo a mudança do câmbio nominal em cinco anos.');
 text(s,'Termos de troca = preços de exportação / preços de importação',64,211,1152,55,31,teal,true);
 text(s,'EJR: mudança nominal prevista = β × desvio do câmbio real',64,306,1152,59,30);
 text(s,'Extensão: EJR + γ × log(TT) + δ × mudança anual de log(TT)',64,394,1152,68,30,pal.TT_all,true);
 text(s,'Exemplo: preços exportados +20%, importados +10%. TT melhora 9,1%.',64,500,1152,60,27);
 method(s,'Índices centrados com história disponível. TT de bens e serviços do ano Y−2; CPI t−2.\nDados comerciais do euro: Alemanha como aproximação. Séries revisadas, sem vintages.',577,65,19);
 foot(s,'Fontes: contas nacionais WDI; ejr_trade/run.py e ejr_trade_selected/run.py. Esta extensão não usa a cesta de commodities.');
}
{
 const s=slide('tt_full','RMSE / erro de nenhuma mudança, em 60 meses. Abaixo de 1, a previsão melhora.');
 const cs=['BRL','EUR','JPY','GBP','CAD','SEK','POOL'];
 const v=[['Moeda','EJR','EJR + termos de troca'],...cs.map(c=>[c==='POOL'?'Agregado':c,num(fmetric(data.tt_full,60,c,'EJR'),3),num(fmetric(data.tt_full,60,c,'TOT_both'),3)])];
 const t=table(s,v,{y:210,h:346,widths:[382,385,385],font:25});
 t.cells.block({row:0,column:0,rowCount:8,columnCount:3}).assign({margins:{left:16,right:12,top:4,bottom:4}});
 for(let r=1;r<v.length;r++)for(let c=1;c<3;c++){const x=fmetric(data.tt_full,60,cs[r-1],c===1?'EJR':'TOT_both');t.getCell(r,c).text.style={typeface:F,fontSize:25,color:x<1?teal:navy,bold:x<1};}
 method(s,ttFoot+'\nCoeficientes estimados nas seis moedas. O filtro retrospectivo seleciona BRL, EUR e CAD.',572,69,19);
 foot(s,'Fonte: ejr_trade/tables/metrics.csv, main/all. TT = nível em log + mudança anual em log. Ganho pontual, sem prova de significância.');
}
{
 const s=slide('tt_selected','EJR e EJR + TT reestimados no mesmo trio. Horizonte de cinco anos.');
 table(s,[['Moeda','EJR','EJR + TT'],...['BRL','EUR','CAD','POOL'].map(c=>[c==='POOL'?'Agregado':c,num(fmetric(data.tt_selected,60,c,'EJR'),3),num(fmetric(data.tt_selected,60,c,'TOT_LOG_LD'),3)])],{x:64,y:219,w:651,h:284,widths:[251,195,205],font:26});
 text(s,'Transformações de TT\nNível + mudança anual',759,211,445,64,25,navy,true);
 table(s,[['Forma','Erro agregado'],['Log',num(fmetric(data.tt_transforms,60,'POOL','TOT_LOG_LD'),3)],['Desvio',num(fmetric(data.tt_transforms,60,'POOL','TOT_DEV_LD'),3)],['Log com sinal',num(fmetric(data.tt_transforms,60,'POOL','TOT_SLOG_LD'),3)]],{x:759,y:285,w:457,h:218,widths:[283,174],font:22});
 text(s,'A melhora agregada de 0,802 para 0,628 é dominada pelo Brasil.',64,517,1152,52,27,teal,true);
 method(s,ttFoot+'\nPaíses e forma de TT escolhidos na avaliação completa: resultado exploratório.',581,62,18);
 foot(s,'Fonte: ejr_trade_selected/tables/metrics.csv. Normalizando por país: EJR 0,810; TT 0,844. Agregado padrão soma erros em log.');
}
function scatterTT(key,inside){
 const s=slide(key,inside?'Ajustado versus realizado em 60m. Regressões individuais com intercepto, na amostra completa.':'Previsto versus realizado em 60m. Regressões agrupadas no trio, estimadas a cada origem.');
 for(const [j,cc] of ['BRL','EUR','CAD'].entries()){
  const a=data.tt_scatter.filter(r=>r.country===cc);const all=a.flatMap(r=>inside?[...r.fitted,...r.actual_fit]:[...r.predicted,...r.actual_oos]);
  const lo=Math.floor((Math.min(...all)-8)/25)*25,hi=Math.ceil((Math.max(...all)+8)/25)*25;
  const series=a.map(r=>({name:r.model==='EJR'?'EJR (azul)':'TT (laranja)',xValues:inside?r.fitted:r.predicted,values:inside?r.actual_fit:r.actual_oos,line:{fill:'none',width:0},fill:r.model==='EJR'?pal.EJR:pal.TT_all,marker:{symbol:r.model==='EJR'?'circle':'diamond',size:4}}));
  series.push({name:'Diagonal perfeita',xValues:[lo,hi],values:[lo,hi],line:{fill:'#A0A8AE',width:1.2},marker:{symbol:'none'}});
  text(s,cc,64+j*391,204,365,37,27,navy,true);
  chart(s,'scatter',{position:{left:50+j*393,top:243,width:390,height:309},series,scatterOptions:{style:'lineWithMarkers'},hasLegend:true,legend:{position:'bottom',textStyle:{typeface:F,fontSize:14,fill:navy}},
   xAxis:{min:lo,max:hi,majorUnit:hi-lo>150?50:25,numberFormatCode:'0',title:inside?'Ajustado (log × 100)':'Previsto (log × 100)',textStyle:{typeface:F,fontSize:16,fill:gray}},
   yAxis:{min:lo,max:hi,majorUnit:hi-lo>150?50:25,numberFormatCode:'0',title:'Realizado (log × 100)',textStyle:{typeface:F,fontSize:16,fill:gray}}});
  text(s,(inside?'R² ajustado: ':'Erro relativo: ')+a.map(r=>num(inside?r.r2:r.rmse,3)).join(' / '),64+j*391,550,374,44,21,navy,true);
 }
 method(s,inside?'Origens do ajuste: out/1999–ago/2021. Alvos: out/2004–ago/2026. Ajuste com toda a amostra.\nA ordem dos indicadores é EJR / EJR + TT. R² alto não demonstra previsão fora da amostra.':ttFoot+'\nOrdem dos indicadores: EJR / EJR + TT. Pontos são origens sobrepostas, não observações independentes.',598,47,17);
 foot(s,inside?'Fonte: ejr_trade_selected/figures.py e in_sample.csv. Diagnóstico individual com intercepto; a previsão seguinte usa coeficiente agrupado.':'Fonte: ejr_trade_selected/tables/predictions.csv.gz e metrics.csv. Seleção de países e transformação de TT retrospectiva.');
}
scatterTT('tt_fit',true);scatterTT('tt_oos',false);
{
 const s=slide('book_rules','Expectativa em 60m = diferencial mensal de juros × 60 − depreciação nominal prevista.');
 table(s,[['Decisão','Seis moedas','Trio selecionado'],['Ranking','2 compras + 2 vendas\n25% por moeda','1 compra + 1 venda\n50% por moeda'],['Máximo Sharpe','Pesos otimizados\nTeto 25% por moeda','Pesos otimizados\nTeto 50% por moeda']],{y:210,h:244,widths:[366,393,393],font:25});
 text(s,'50% comprado + 50% vendido. Risco do otimizador: retornos de 60m.',64,471,1152,50,28,teal,true);
 text(s,'Nova escolha a cada 12 ou 60 meses. Manutenção mensal dos pesos-alvo.',64,525,1152,50,27);
 method(s,'Risco: janela expansiva até t−1, regularização de 20% na diagonal. Sem saídas antecipadas.\nSinal jan/2010; execução fev/2010. Retornos mar/2010–fev/2025. Caixa e custos incluídos.',581,63,19);
 foot(s,'Fonte: horizon_tests. 60m de manutenção termina em t+61 pelo atraso de execução. Juros correntes extrapolados não são taxas contratadas.');
}
function wealthSlides(universe){
 const six=universe==='six';const s=slide(universe+'_wealth','Patrimônio em USD, base 100 em fev/2010. Mesmas cores nos quatro painéis.');
 const sigs=six?['Carry','EJR','EJR_trio','EJR_TOT_trio']:['Carry','EJR','TT_all','Matched'];
 const all=data.wealth[universe].flatMap(r=>r.nav),lo=Math.floor((Math.min(...all)-3)/10)*10,hi=Math.ceil((Math.max(...all)+3)/10)*10;
 for(let row=0;row<2;row++)for(let col=0;col<2;col++){
  const method=row===0?'Ranking':'long60',hold=col===0?12:60,x=54+col*602,y=204+row*210;
  text(s,(row===0?'Ranking':'Máximo Sharpe, risco 60m')+' · escolha '+hold+'m',x+8,y-4,585,34,23,navy,true);
  const series=sigs.map(sig=>{const r=data.wealth[universe].find(r=>r.method===method&&r.hold===hold&&r.signal===sig);return {name:labs[sig],xValues:r.x,values:r.nav,line:{fill:pal[sig],width:sig==='EJR_trio'?1.2:2.5},marker:{symbol:'none'}};});
  const r=data.wealth[universe].find(r=>r.method===method&&r.hold===hold);
  series.push({name:'Caixa USD',xValues:r.x,values:r.cash,line:{fill:pal.Cash,width:1.3},marker:{symbol:'none'}});
  chart(s,'scatter',{position:{left:x,top:y+31,width:588,height:174},series,hasLegend:true,legend:{position:'bottom',textStyle:{typeface:F,fontSize:14,fill:navy}},scatterOptions:{style:'line'},
   xAxis:{min:2010,max:2025.3,majorUnit:5,numberFormatCode:'0',textStyle:{typeface:F,fontSize:16,fill:gray}},yAxis:{min:lo,max:hi,majorUnit:20,numberFormatCode:'0',textStyle:{typeface:F,fontSize:16,fill:gray}}});
 }
 method(s,six?'Controle e TT substituem só BRL/EUR/CAD. No ranking, EJR e controle coincidem.':'Combinado: TT no BRL, EJR em EUR/CAD. No ranking 60m, Juros e EJR coincidem.',625,23,17);
 foot(s,commonFoot+'\nFonte: horizon_tests, retornos líquidos. Seleção retrospectiva de países e TT. Custos básicos; USD é numerário e caixa.');
}
function portfolioTable(universe){
 const six=universe==='six';const s=slide(universe+'_table','Cada célula: retorno anual composto / Sharpe / queda máxima. Líquidos dos custos assumidos.');
 const sigs=six?['Carry','EJR','EJR_trio','EJR_TOT_trio']:['Carry','EJR','TT_all','Matched'];
 const rows=[['Método e sinal','Escolha a cada 12m','Escolha a cada 60m']];let colors=[];
 for(const method of ['Ranking','long60'])for(const sig of sigs){
  const r=six?data.six_table.find(r=>r.scenario==='Base'&&r.metodo===(method==='Ranking'?'Dois pares':'Máximo Sharpe — risco de 60 meses')&&r.variant===sig):data.three_table.find(r=>r.scenario==='Base'&&r.method===method&&r.signal===sig);
  const trip=h=>`${fmt(r['cagr_'+h])} / ${num(r['sharpe_'+h],3)} / ${fmt(r['maxdd_'+h])}`;
  rows.push([(method==='Ranking'?'Ranking':'Máx. Sharpe 60m')+' · '+labs[sig],trip(12),trip(60)]);colors.push(pal[sig]);
 }
 const t=table(s,rows,{y:213,h:364,widths:[410,371,371],font:22});
 t.cells.block({row:0,column:0,rowCount:9,columnCount:3}).assign({margins:{left:12,right:8,top:3,bottom:3}});
 for(let i=1;i<9;i++)t.getCell(i,0).text.style={typeface:F,fontSize:21,color:colors[i-1],bold:true};
 method(s,six?'EJR controle: reestimação no trio. EJR + TT: extensão no trio. JPY/GBP/SEK mantêm EJR original.\nSeis moedas. Bruta 100%, líquida zero, teto 25%. Ranking compra duas e vende duas.':'Combinado: TT no BRL, EJR em EUR/CAD. Todos os modelos foram estimados no trio.\nTrês moedas. Bruta 100%, líquida zero, teto 50%. Ranking compra uma e vende uma.',592,52,18);
 foot(s,commonFoot+'\nFonte: horizon_tests/tables/'+(six?'with_terms_of_trade.csv':'restricted_table.csv')+'. 12m/60m = intervalo de escolha.');
}
wealthSlides('six');portfolioTable('six');wealthSlides('three');portfolioTable('three');
{
 const s=slide('costs','Trio selecionado. Máximo Sharpe com risco de 60m e escolha anual.');
 const get=(sig,sc)=>data.three_table.find(r=>r.signal===sig&&r.scenario===sc&&r.method==='long60');
 const rows=[['Sinal','Custos básicos\nRetorno / Sharpe','Estresse\nRetorno / Sharpe'],...['Carry','EJR','TT_all','Matched'].map(sig=>[labs[sig],fmt(get(sig,'Base').cagr_12)+' / '+num(get(sig,'Base').sharpe_12,3),fmt(get(sig,'Stress').cagr_12)+' / '+num(get(sig,'Stress').sharpe_12,3)])];
 const t=table(s,rows,{y:212,h:271,widths:[398,377,377],font:26});
 t.cells.block({row:0,column:0,rowCount:5,columnCount:3}).assign({margins:{left:16,right:12,top:4,bottom:4}});
 text(s,'EJR básico: volatilidade 5,45% a.a. e queda máxima de 13,31%.',64,493,1152,53,28,teal,true);
 method(s,'Base: BRL 10 pb, EUR/CAD 2 pb por negociação; financiamento extra 50 pb a.a. na venda.\nEstresse: negociação 4× e financiamento extra 150 pb a.a. Mesmos pesos.\nEntrada, manutenção mensal e liquidação cobradas. Custos assumidos, não cotações executáveis.',554,88,19);
 foot(s,commonFoot+'\nFonte: horizon_tests/tables/restricted_table.csv e restricted_metrics.csv.');
}
{
 const s=slide('conclusion');
 text(s,'EJR melhora a previsão em cinco anos em parte dos países.',64,198,1152,73,33,navy,true);
 text(s,'Termos de troca ajudam no Brasil, mas pioram as carteiras testadas.',64,306,1152,83,32,pal.TT_all,true);
 text(s,'No trio, EJR com escolha anual alcança 3,29% a.a. e Sharpe 0,393.',64,425,1152,81,32,pal.EJR,true);
 text(s,'Seleção retrospectiva e só três blocos de cinco anos.\nO resultado precisa de validação em dados novos.',64,547,1152,83,28,gray);
 foot(s,'Resultados finais: mar/2010–fev/2025. Países e forma de TT escolhidos na mesma história, com alvos até ago/2026.');
}
{
 const s=slide('transform_backup','Trio reestimado. Erro relativo a nenhuma mudança. Todas as extensões usam nível + mudança.');
 const hs=[12,24,36,60,84,96];
 const t=table(s,[['Horizonte','EJR','TT log','TT desvio','TT log com sinal'],...hs.map(h=>[h/12+' ano'+(h===12?'':'s'),...['EJR','TOT_LOG_LD','TOT_DEV_LD','TOT_SLOG_LD'].map(m=>num(fmetric(data.tt_selected,h,'POOL',m),3))])],{y:210,h:337,widths:[225,215,230,230,252],font:26});
 t.cells.block({row:0,column:0,rowCount:7,columnCount:5}).assign({margins:{left:16,right:12,top:4,bottom:4}});
 method(s,'Origens: 1a jan/2010–ago/2025; 2a até ago/2024; 3a até ago/2023; 5a até ago/2021.\n7a nov/2011–ago/2019; 8a nov/2012–ago/2018. Treino expansivo desde out/1999, alvos até t−1.\nLog do desvio negativo não existe nos reais. Log com sinal é outra transformação.',565,78,19);
 foot(s,'Fonte: ejr_trade_selected/tables/metrics.csv. Alvos até ago/2026. Forma escolhida retrospectivamente no teste de 60m.');
}
{
 const s=slide('pooling_backup','Horizonte 60m. A forma de agregar os erros altera a interpretação.');
 const r=(training,evaluation,model,col)=>data.pooling.find(x=>x.training===training&&x.evaluation===evaluation&&x.model===model)[col];
 const v=[['Comparação','EJR','EJR + TT'],['Trio, agregado padrão',...['EJR','TOT_LOG_LD'].map(m=>num(r('panel_3','BRL+EUR+CAD',m,'rmse_rw'),3))],['Trio, erro normalizado por país',...['EJR','TOT_LOG_LD'].map(m=>num(r('panel_3','BRL+EUR+CAD',m,'equal_country_rmse'),3))],['Sem BRL, reestimado em EUR/CAD',...['EJR','TOT_LOG_LD'].map(m=>num(r('without_BRL','EUR+CAD',m,'rmse_rw'),3))]];
 table(s,v,{y:229,h:259,widths:[650,251,251],font:26});
 text(s,'O ganho de TT não se distribui de forma uniforme entre países.',64,512,1152,62,29,teal,true);
 method(s,ttFoot,590,51,18);foot(s,'Fonte: ejr_trade_selected/tables/pooling_diagnostics.csv. Seleção de países e transformação retrospectiva.');
}

{
 const s=slide(10,'Regras próprias: decisões mensais e risco de 12m. Não validam a convergência prevista em 60m.');
 table(s,[['Decisão','Regra econômica'],['Quanto investir','Reduzir tamanho se a previsão for fraca.\nEvitar mudanças comerciais extremas.'],['Quando entrar','Exigir retorno previsto mínimo.\nEvitar preços comerciais adversos.'],['Quando sair','Abrir parcelas com prazo de até 12 meses.\nSair se o comércio indicar risco adicional.']],{y:210,h:324,widths:[312,840],font:26});
 method(s,'Treino expansivo: EJR desde out/1999; risco comercial desde jan/2011.\nHorizontes: câmbio nominal 60m; risco de consumo dos juros 12m. Backtest: abr/2018–ago/2026.\nRisco adicional compara modelo com comércio à base. Limiares usam só história passada.',552,89,20);
 foot(s,'Fonte: synthesis/model.py. Pesos 1/3 por módulo. Mínimos: 60 origens EJR, 36 risco e 36 meses de histórico dos limiares.');
}

{
 const s=slide(11,'Abr/2018–ago/2026. Resultado histórico das regras próprias; não é validação econômica do artigo.');
 const c=b('Carry'),e=b('Equal_modules');
 table(s,[['Métrica','Carry por juros','Combinação'],['Retorno anual composto',fmt(c.cagr),fmt(e.cagr)],['Volatilidade anual',fmt(c.vol),fmt(e.vol)],['Sharpe',num(c.sharpe),num(e.sharpe)],['Queda máxima',fmt(c.maxdd),fmt(e.maxdd)],['Exposição bruta média',fmt(c.exposure,0),fmt(e.exposure,0)]],{y:210,h:352,widths:[545,305,302]});
 method(s,'Primeiro sinal: fev/2018. Treino EJR: out/1999–jan/2013; risco: jan/2011–dez/2016.\nAlvos disponíveis até jan/2018. Depois, reestimação expansiva mensal.\nBacktest comum: abr/2018–ago/2026, 101 retornos mensais líquidos.',570,73,19);
 foot(s,'Fonte: síntese, metrics.csv, common/all. Exposição líquida zero. Resultado exploratório, sem prova de ganho de retorno médio.');
}

{
 const s=slide(12,'Abr/2018–ago/2026. Patrimônio líquido em USD. Referência das regras próprias de exposição.');
 const series=[],ddseries=[];
 for(const [name,label,color] of [['Carry','Carry por juros',pal.Carry],['Equal_modules','Combinação',pal.Matched],['Cash','Caixa USD','#9DA8AF']]){
  const rows=data.returns.filter(x=>x.name===name);let nav=100,peak=100;
  const xs=[2018+2/12],v=[100],dd=[0];
  for(const r of rows){nav*=1+r.net;peak=Math.max(peak,nav);const [yy,mm]=r.month.split('-').map(Number);xs.push(yy+(mm-1)/12);v.push(nav);dd.push(100*(nav/peak-1));}
  series.push({name:label,xValues:xs,values:v,line:{fill:color,width:name==='Cash'?2:3},marker:{symbol:'none'}});
  if(name!=='Cash')ddseries.push({name:label,xValues:xs,values:dd,line:{fill:color,width:2.7},marker:{symbol:'none'}});
 }
 chart(s,'scatter',{position:{left:55,top:195,width:1170,height:229},series,hasLegend:true,legend:{position:'top'},scatterOptions:{style:'line'},xAxis:{min:2018,max:2027,majorUnit:2,numberFormatCode:'0',tickLabelPosition:'none'},yAxis:{min:90,max:175,majorUnit:20,numberFormatCode:'0',title:'Patrimônio'}});
 chart(s,'scatter',{position:{left:55,top:429,width:1170,height:157},series:ddseries,hasLegend:false,scatterOptions:{style:'line'},xAxis:{min:2018,max:2027,majorUnit:2,numberFormatCode:'0'},yAxis:{min:-10,max:0,majorUnit:5,numberFormatCode:'0"%"',title:'Perda do pico'}});
 method(s,'Treino no 1º sinal (fev/2018): EJR out/1999–jan/2013; risco jan/2011–dez/2016.\nAlvos disponíveis até jan/2018. Janelas expansivas. Backtest: abr/2018–ago/2026.',590,55,19);
 foot(s,'Fonte: síntese, returns.csv.gz; timing_audit.csv e extensão comercial, audit.csv. Lotes de até 12m no módulo C.');
}

{
 const s=slide('tenure','Sensibilidade de regras próprias: lotes de 6–24m. Não é um teste de convergência em cinco anos.');
 const rows=[6,12,24].map(h=>{
  const r=data.tenure.find(x=>x.name==='Equal_modules'&&x.variant===(h===12?'Base':`Tenure${h}`));
  return [`${h} meses`,fmt(r.cagr),fmt(r.vol),num(r.sharpe),fmt(r.maxdd),fmt(r.exposure,0)];
 });
 table(s,[['Prazo máximo','Retorno a.a.','Vol. a.a.','Sharpe','Queda máx.','Exp. média'],...rows],{y:225,h:240,widths:[227,185,185,175,195,185],font:24});
 text(s,'A exposição é contínua. O prazo dos lotes muda quanto e por quanto tempo carregar.',64,482,1152,67,27,teal,true);
 method(s,'Mesmo backtest: abr/2018–ago/2026; custos e treinamento expansivo iguais ao resultado da combinação.\nMuda somente o máximo do lote e o orçamento mensal 1/H. Há saída antecipada.\nA previsão de risco continua em 12m. Estes testes não identificam um prazo ótimo.',554,89,20);
 foot(s,'Fonte: síntese, robustness.csv (Base, Tenure6, Tenure24), make_policies. Outros dois módulos continuam com revisão mensal.');
}

{
 const s=slide(17,'Comparação na mesma janela de 2018–2026. Controle de exposição retrospectivo.');
 const c=b('Carry'),e=b('Equal_modules'),z=data.controls.find(x=>x.control==='expost');
 table(s,[['Métrica','Carry','Carry a 48%','Combinação'],['Retorno anual',fmt(c.cagr),fmt(z.cagr),fmt(e.cagr)],['Volatilidade',fmt(c.vol),fmt(z.vol),fmt(e.vol)],['Queda máxima',fmt(c.maxdd),fmt(z.maxdd),fmt(e.maxdd)]],{y:222,h:276,widths:[435,239,239,239]});
 text(s,'Sinal no mês t. Execução em t+1. Primeiro retorno em t+2.\nCustos e financiamento entram nos retornos das duas regras.',64,539,1152,87,29,teal,true);
 foot(s,'A média de 48% só é conhecida ao final. Controle diagnóstico, sem regra executável ex ante. Fonte: exposure_controls.csv.');
}
const seconds=content.slides.reduce((a,s)=>a+s.seconds,0);
await fs.writeFile('timing_v7.json',JSON.stringify({mainSlides:18,backupSlides:7,seconds,minutes:seconds/60},null,2));
await fs.mkdir('rendered_v7',{recursive:true});
const candidate=path.join(root,'presentation/build/candidate_v7.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
console.log('Draft exported; '+seconds+' seconds of planned speech');
const tag=process.env.REVISION_TAG??'v7';
const final=path.join(root,`output/presentation/apresentacao_macro_aula_${tag}_final.pptx`);
const receipt=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,
 pythonExecutable:path.join(runtime,'python/python.exe'),
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[...tableOwners].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:[...tableOwners],requiredNativeChartOwnerSlides:[...chartOwners],
 materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[F]},verifyArtifactToolImport:true,
 receiptPath:path.join(root,`presentation/build/validation_${tag}_final.json`)});
console.log('Finalized:',final);
const imported=await PresentationFile.importPptx(await FileBlob.load(final));
for(let i=0;i<imported.slides.items.length;i++){
 const slide=imported.slides.items[i];
 const png=await imported.export({slide,format:'png',scale:1.5});
 await fs.writeFile(`rendered_v7/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await png.arrayBuffer()));
 console.log('Rendered slide',i+1);
}

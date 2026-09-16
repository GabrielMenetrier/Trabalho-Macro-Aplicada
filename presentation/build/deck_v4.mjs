import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile,FileBlob} from '@oai/artifact-tool';
const root=path.resolve('../..');
const skill='C:/Users/Pichau/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations';
const runtime='C:/Users/Pichau/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const data=JSON.parse(await fs.readFile('../data_v4.json','utf8'));
const content=JSON.parse(await fs.readFile('../content_v4.json','utf8'));
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
 text(s,entry(n).title,64,40,1152,104,42,navy,true);
 if(sub)text(s,sub,64,141,1152,55,23,gray);
 text(s,String(physical).padStart(2,'0')+(physical>16?' apoio':''),1120,670,120,26,16,gray);
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
 text(s,'Câmbio real, commodities\ne carry trade',70,151,1130,180,64,navy,true);
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
 foot(s,'Escopo deste trabalho: relação preditiva e exemplo da aula. O modelo estrutural completo do artigo fica fora da replicação.');
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
 const s=slide(5,'Mesmos tipos de ativos e custos. O que muda é o sinal para escolher as moedas.');
 table(s,[['Carry por juros','Carry com previsão cambial'],['Diferencial de juros','Diferencial de juros\n+ valorização prevista']],{y:226,h:156,widths:[530,622]});
 text(s,'Retorno aproximado = diferencial de juros + valorização cambial − custos',64,414,1152,73,30,teal,true);
 text(s,'Exemplo: ativo +10%, financiamento 3%, moeda −8%.\nResultado exato antes de custos: 1,10 × 0,92 − 1,03 = −1,8%.',64,516,1152,98,29);
 foot(s,'Exemplo hipotético. Simulação com aplicações curtas e financiamento. O cálculo exato inclui interação entre juros e câmbio.');
}
{
 const s=slide(6,'Retornos líquidos em dólar, março de 2010 a agosto de 2026.');
 const c=data.initial.find(x=>x.strategy==='Carry'),e=data.initial.find(x=>x.strategy==='EJR + carry');
 table(s,[['Métrica','Carry por juros','Carry + previsão'],['Retorno anual composto',fmt(c.cagr),fmt(e.cagr)],['Volatilidade anual',fmt(c.vol),fmt(e.vol)],['Sharpe',num(c.sharpe),num(e.sharpe)],['Queda máxima',fmt(c.maxdd),fmt(e.maxdd)]],{y:208,h:275,widths:[545,305,302]});
 method(s,'Ranking com 2 compras e 2 vendas, 25% por ponta. Sem otimização de Markowitz.\nPrevisão 60m; revisão mensal; execução t+1. Backtest: mar/2010–ago/2026.\nTreino inicial: origens out/1999–dez/2004, alvos até dez/2009. Depois, expansivo mensal.\nCustos: BRL 10 pb, SEK 3 pb, demais 2 pb por notional; spread extra na venda 50 pb a.a.',501,140,20);
 foot(s,'Fonte: portfolio_metrics.csv, timing_audit.csv e src/models.py. Custos em entrada, rebalanceamento e saída. Caixa USD incluído.');
}
{
 const s=slide('initial_wealth','Mesmas regras do slide anterior. Patrimônio líquido em USD, base 100.');
 const series=[];
 for(const [name,label,color] of [['Carry','Carry por juros',navy],['EJR + carry','Carry + previsão',teal],['Cash','Caixa USD','#9DA8AF']]){
  const rows=data.initial_returns.filter(r=>r.strategy===(name==='Cash'?'Carry':name));let nav=100;
  const xs=[2010+1/12],v=[100];
  for(const r of rows){const [yy,mm]=r.month.split('-').map(Number);xs.push(yy+(mm-1)/12);nav*=1+(name==='Cash'?r.cash:r.net);v.push(nav);}
  series.push({name:label,xValues:xs,values:v,line:{fill:color,width:name==='Cash'?2:3},marker:{symbol:'none'}});
 }
 chart(s,'scatter',{position:{left:55,top:205,width:1170,height:340},series,hasLegend:true,legend:{position:'top'},scatterOptions:{style:'line'},xAxis:{min:2010,max:2027,majorUnit:4,numberFormatCode:'0'},yAxis:{min:90,max:205,majorUnit:25,numberFormatCode:'0',title:'Patrimônio'}});
 method(s,'Backtest: mar/2010–ago/2026. Treino EJR expansivo desde out/1999, só com alvos maduros.\nHorizonte da previsão: 60 meses. Revisão das posições: mensal. Custos iguais aos do slide 6.',565,78,20);
 foot(s,'Fonte: portfolio_returns.csv. 198 retornos líquidos mensais. A previsão de cinco anos não fixa cinco anos de permanência.');
}
{
 const s=slide(7,'Etapa preditiva: sem carteiras de commodities.');
 text(s,'Termos de troca = preços das exportações / preços das importações',64,220,1152,83,33,teal,true);
 text(s,'Uma alta do petróleo pode favorecer um exportador líquido\ne prejudicar um importador líquido.',64,335,1152,105,32);
 text(s,'Hipótese: o comércio muda a referência do câmbio real,\ne a média histórica passa a contar apenas parte da história.',64,483,1152,102,31);
 foot(s,'Preços de commodities, termos de troca agregados e composição comercial são medidas distintas. Exemplo econômico ilustrativo.');
}
{
 const s=slide(8,'Origem = mês em que fazemos a previsão. Exemplo: jan/2010 prevê até jan/2015.');
 const all=data.commodity.find(x=>x.period==='all'),late=data.commodity.find(x=>x.period==='late');
 table(s,[['Modelo','Origens 2010–2021','Origens 2019–2021'],['Nenhuma mudança','1,000','1,000'],['EJR',num(data.oos.rmse_ratio,3),num(late.rmse_rw/late.rmse_ratio,3)],['EJR + commodities',num(all.rmse_rw,3),num(late.rmse_rw,3)]],{y:218,h:260,widths:[500,326,326]});
 text(s,'Erro relativo: abaixo de 1 melhora. O recorte recente perde para a referência.',64,489,1152,54,26,teal,true);
 method(s,'Treino expansivo: origens desde out/1999, com alvos encerrados até t−1. Previsão: 60m.\nAvaliação: 140 origens jan/2010–ago/2021 e 32 origens jan/2019–ago/2021.\nAlvos realizados: jan/2015–ago/2026 e jan/2024–ago/2026. Sem carteiras neste teste.',553,89,20);
 foot(s,'Fonte: terceiro relatório, REJR_Specific. Pesos comerciais de 1994–1996. Sem BRL, o ganho sobre nenhuma mudança desaparece.');
}
{
 const s=slide(10,'Três módulos, combinados em partes iguais. O carry continua orientando as pontas.');
 table(s,[['Decisão','Regra econômica'],['Quanto investir','Reduzir tamanho se a previsão for fraca.\nEvitar mudanças comerciais extremas.'],['Quando entrar','Exigir retorno previsto mínimo.\nEvitar preços comerciais adversos.'],['Quando sair','Abrir parcelas com prazo de até 12 meses.\nSair se o comércio indicar risco adicional.']],{y:210,h:324,widths:[312,840],font:26});
 method(s,'Treino expansivo: EJR desde out/1999; risco comercial desde jan/2011.\nHorizontes: câmbio nominal 60m; risco de consumo dos juros 12m. Backtest: abr/2018–ago/2026.\nRisco adicional compara modelo com comércio à base. Limiares usam só história passada.',552,89,20);
 foot(s,'Fonte: synthesis/model.py. Pesos 1/3 por módulo. Mínimos: 60 origens EJR, 36 risco e 36 meses de histórico dos limiares.');
}
{
 const s=slide(11,'Janela comum: abril de 2018 a agosto de 2026. Retornos líquidos em dólar.');
 const c=b('Carry'),e=b('Equal_modules');
 table(s,[['Métrica','Carry por juros','Combinação'],['Retorno anual composto',fmt(c.cagr),fmt(e.cagr)],['Volatilidade anual',fmt(c.vol),fmt(e.vol)],['Sharpe',num(c.sharpe),num(e.sharpe)],['Queda máxima',fmt(c.maxdd),fmt(e.maxdd)],['Exposição bruta média',fmt(c.exposure,0),fmt(e.exposure,0)]],{y:210,h:352,widths:[545,305,302]});
 method(s,'Primeiro sinal: fev/2018. Treino EJR: out/1999–jan/2013; risco: jan/2011–dez/2016.\nAlvos disponíveis até jan/2018. Depois, reestimação expansiva mensal.\nBacktest comum: abr/2018–ago/2026, 101 retornos mensais líquidos.',570,73,19);
 foot(s,'Fonte: síntese, metrics.csv, common/all. Exposição líquida zero. Resultado exploratório, sem prova de ganho de retorno médio.');
}
{
 const s=slide('tenure','Variação do prazo máximo dos lotes do módulo C. Resultados da combinação inteira.');
 const rows=[6,12,24].map(h=>{
  const r=data.tenure.find(x=>x.name==='Equal_modules'&&x.variant===(h===12?'Base':`Tenure${h}`));
  return [`${h} meses`,fmt(r.cagr),fmt(r.vol),num(r.sharpe),fmt(r.maxdd),fmt(r.exposure,0)];
 });
 table(s,[['Prazo máximo','Retorno a.a.','Vol. a.a.','Sharpe','Queda máx.','Exp. média'],...rows],{y:225,h:240,widths:[227,185,185,175,195,185],font:24});
 text(s,'A exposição é contínua. O prazo dos lotes muda quanto e por quanto tempo carregar.',64,482,1152,67,27,teal,true);
 method(s,'Mesmo backtest: abr/2018–ago/2026; custos e treinamento expansivo iguais ao slide anterior.\nMuda somente o máximo do lote e o orçamento mensal 1/H. Há saída antecipada.\nA previsão de risco continua em 12m. Estes testes não identificam um prazo ótimo.',554,89,20);
 foot(s,'Fonte: síntese, robustness.csv (Base, Tenure6, Tenure24), make_policies. Outros dois módulos continuam com revisão mensal.');
}
{
 const s=slide(12,'Patrimônio líquido em dólar, base 100 antes de abril de 2018.');
 const series=[],ddseries=[];
 for(const [name,label,color] of [['Carry','Carry por juros',navy],['Equal_modules','Combinação',teal],['Cash','Caixa USD','#9DA8AF']]){
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
 const s=slide(13,'Contribuição ao excesso médio anual, em pontos percentuais. Abril/2018–agosto/2026.');
 const annual=(name,component)=>100*data.attribution.find(x=>x.name===name&&x.component===component).annual;
 chart(s,'bar',{position:{left:63,top:213,width:770,height:338},categories:['Câmbio','Juros'],series:[{name:'Carry por juros',values:[annual('Carry','FX'),annual('Carry','Interest')],fill:navy},{name:'Combinação',values:[annual('Equal_modules','FX'),annual('Equal_modules','Interest')],fill:teal}],hasLegend:true,barOptions:{direction:'column',grouping:'clustered',gapWidth:130},dataLabels:{showValue:true,position:'outEnd',textStyle:{typeface:F,fontSize:24,fill:navy}},yAxis:{min:0,max:3.2,majorUnit:1,numberFormatCode:'0.0',title:'Pontos percentuais'},xAxis:{}});
 text(s,'Custo de ficar de fora',870,227,340,60,27,navy,true);
 text(s,'Em 2019, excesso anual:\n\nCarry: 3,83%\nCombinação: 0,40%',870,315,340,180,28,gray);
 method(s,'Atribuição do backtest abr/2018–ago/2026. Mesmos modelos e treino expansivo da combinação.\nO filtro protegeu em alguns episódios e deixou ganhos para trás em outros.',569,73,21);
 foot(s,'Fonte: attribution.csv e episodes.csv. Média aritmética anualizada. Componentes não somam o CAGR. Custos e interação completam a conta.');
}
{
 const s=slide(14,'Melhora histórica de risco não basta para estabelecer uma vantagem de mercado.');
 text(s,'Escolha das regras após muitos testes na mesma história.',64,228,1152,66,32);
 text(s,'Menor exposição explica parte da redução do risco.',64,321,1152,66,32);
 text(s,'Resultados dependem bastante de BRL e JPY.',64,414,1152,66,32);
 text(s,'Dados revisados e taxas aproximadas limitam a execução real.',64,507,1152,66,32);
 foot(s,'O teste corrigido para 14 alternativas principais não estabelece ganho de retorno médio. Calendário controlado não elimina seleção histórica.');
}
{
 const s=slide(15);
 text(s,'A relação histórica da aula se replica.',64,218,1152,77,37,navy,true);
 text(s,'Commodities ajudam em alguns testes, com instabilidade.',64,344,1152,77,34,navy);
 text(s,'Controlar a exposição ao carry foi a hipótese mais promissora\npara reduzir risco na amostra.',64,463,1152,111,34,teal,true);
 foot(s,'Próxima validação: regras congeladas, dados futuros e custos executáveis. Resultados exploratórios, sem arbitragem demonstrada.');
}
{
 const s=slide(16,'Regressões nominais. Índices de país omitidos para facilitar a leitura.');
 text(s,'Base: Δs(t, t+h) = β × desvio real + erro',64,225,1152,69,33,navy,true);
 text(s,'Extensão: base + γ × preços globais + δ × exposição específica',64,327,1152,80,31,teal,true);
 text(s,'Em t, o treinamento só inclui alvos terminados até t−1.\nCPI e preços comerciais entram defasados.\nA previsão de 60 meses / 60 é um ritmo médio aproximado.',64,449,1152,150,29);
 foot(s,'Fontes: src/models.py e third/engine.py. Regressão preditiva agrupada. Sem identificação causal ou estimação completa do DSGE do artigo.');
}
{
 const s=slide(17,'Comparação na mesma janela de 2018–2026. Controle de exposição retrospectivo.');
 const c=b('Carry'),e=b('Equal_modules'),z=data.controls.find(x=>x.control==='expost');
 table(s,[['Métrica','Carry','Carry a 48%','Combinação'],['Retorno anual',fmt(c.cagr),fmt(z.cagr),fmt(e.cagr)],['Volatilidade',fmt(c.vol),fmt(z.vol),fmt(e.vol)],['Queda máxima',fmt(c.maxdd),fmt(z.maxdd),fmt(e.maxdd)]],{y:222,h:276,widths:[435,239,239,239]});
 text(s,'Sinal no mês t. Execução em t+1. Primeiro retorno em t+2.\nCustos e financiamento entram nos retornos das duas regras.',64,539,1152,87,29,teal,true);
 foot(s,'A média de 48% só é conhecida ao final. Controle diagnóstico, sem regra executável ex ante. Fonte: exposure_controls.csv.');
}
const seconds=content.slides.reduce((a,s)=>a+s.seconds,0);
await fs.writeFile('timing_v4.json',JSON.stringify({mainSlides:16,backupSlides:2,seconds,minutes:seconds/60},null,2));
await fs.mkdir('rendered_v4',{recursive:true});
const candidate=path.join(root,'presentation/build/candidate_v4.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
console.log('Draft exported; '+seconds+' seconds of planned speech');
const final=path.join(root,'output/presentation/apresentacao_macro_aula_v4_final.pptx');
const receipt=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,
 pythonExecutable:path.join(runtime,'python/python.exe'),
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[...tableOwners].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:[...tableOwners],requiredNativeChartOwnerSlides:[...chartOwners],
 materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[F]},verifyArtifactToolImport:true,
 receiptPath:path.join(root,'presentation/build/validation_v4_final.json')});
console.log('Finalized:',final);
const imported=await PresentationFile.importPptx(await FileBlob.load(final));
for(let i=0;i<imported.slides.items.length;i++){
 const slide=imported.slides.items[i];
 const png=await imported.export({slide,format:'png',scale:1.5});
 await fs.writeFile(`rendered_v4/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await png.arrayBuffer()));
 console.log('Rendered slide',i+1);
}

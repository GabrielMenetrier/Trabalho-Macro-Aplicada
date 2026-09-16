from pathlib import Path
import sys,runpy,os
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];H=R/'ejr_trade_selected'
os.environ['MPLCONFIGDIR']=str(R/'tmp/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
e=runpy.run_path(str(H/'run.py'),run_name='selected_engine');CC=e['CC'];T=e['T'];Q=e['Q'];S=e['S'];dates=e['dates']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#15354d','text.color':'#15354d','axes.titleweight':'bold','savefig.bbox':'tight'})
COLORS=['#15354d','#c55d32','#007f7b'];MODELS=['EJR','TOT_LOG_LD','COM_DEV_LD'];LABELS=['EJR','EJR + termos de troca','EJR + cesta de commodities']
m=pd.read_csv(H/'tables/metrics.csv');pred=pd.read_csv(H/'tables/predictions.csv.gz');ins=pd.read_csv(H/'tables/in_sample.csv');X=e['designs'](T-1)
def save(fig,name):
 fig.savefig(H/f'figures/{name}.pdf');fig.savefig(H/f'figures/{name}.png',dpi=190);plt.close(fig)
fig,axs=plt.subplots(2,3,figsize=(11,6.5))
for row,h in enumerate([60,96]):
 for j,c in enumerate(CC):
  ax=axs[row,j];x=Q[:-h,j]-Q[:,j].mean();y=S[h:,j]-S[:-h,j];b=np.polyfit(x,y,1);fit=np.polyval(b,x);r2=1-np.sum((y-fit)**2)/np.sum((y-y.mean())**2)
  ax.scatter(100*x,100*y,color=COLORS[j],alpha=.28,s=12,edgecolors='none');xx=np.linspace(x.min(),x.max(),100);ax.plot(100*xx,100*np.polyval(b,xx),color=COLORS[j],lw=2)
  ax.set(title=f'{c} · {h//12} anos · R² = {r2:.3f}',xlabel='Desvio do log câmbio real × 100',ylabel='Mudança futura do log câmbio × 100');ax.grid(alpha=.15)
fig.tight_layout();save(fig,'relacao_ejr')
summ=[]
for j,c in enumerate(CC):
 fig,axs=plt.subplots(2,3,figsize=(11,7.2));h=60;yy=S[h:,j]-S[:-h,j]
 ob=pred[(pred.h==60)&(pred.country==c)].sort_values('origin')
 plotted=[]
 for k in MODELS:
  cols=['Q']+e['MODELS'][k];a=np.c_[np.ones(len(yy)),np.stack([X[z][:-h,j] for z in cols],axis=1)];b=np.linalg.lstsq(a,yy,rcond=None)[0];fitted=a@b;plotted.append(fitted)
 v=np.r_[yy,ob.actual,*plotted,*[ob[k] for k in MODELS]]*100
 lo=np.floor((v.min()-5)/10)*10;hi=np.ceil((v.max()+5)/10)*10
 for col,k in enumerate(MODELS):
  r2=ins[(ins.country==c)&(ins.h==60)&(ins.model==k)].iloc[0].adjusted_r2
  metric=m[(m.country==c)&(m.h==60)&(m.scenario=='fixed')&(m.model==k)].iloc[0]
  for row,xx,actual in [(0,plotted[col],yy),(1,ob[k].to_numpy(),ob.actual.to_numpy())]:
   ax=axs[row,col];ax.scatter(100*xx,100*actual,s=16,alpha=.42,edgecolors='none',color=COLORS[col]);ax.plot([lo,hi],[lo,hi],ls='--',color='#8b969e',lw=1)
   ax.set(xlim=(lo,hi),ylim=(lo,hi),xlabel=('Ajustado na amostra' if row==0 else 'Previsto fora da amostra')+' (log × 100)',ylabel='Realizado (log × 100)');ax.set_aspect('equal',adjustable='box');ax.grid(alpha=.15);ax.xaxis.set_major_locator(MaxNLocator(4));ax.yaxis.set_major_locator(MaxNLocator(4))
   ax.set_title((LABELS[col]+'\n' if row==0 else '')+(f'R² ajustado = {r2:.3f}' if row==0 else f'RMSE / nenhuma mudança = {metric.rmse_rw:.3f}'),fontsize=10)
  summ.append(dict(country=c,model=k,r2_adjusted=r2,rmse_rw=metric.rmse_rw))
 fig.suptitle(f'{c}: a mesma previsão de cinco anos, com e sem adições',fontsize=14,y=1.02)
 fig.tight_layout();save(fig,'comparacao_'+c)
pd.DataFrame(summ).to_csv(H/'tables/graph_values.csv',index=False)
fig,axs=plt.subplots(1,2,figsize=(10,3.8),sharey=True)
for ax,fam,title in zip(axs,['TOT','COM'],['Termos de troca','Cesta de commodities']):
 base=m[(m.h==60)&(m.scenario=='fixed')&(m.country=='POOL')].set_index('model')
 for j,content in enumerate(['L','D','LD']):
  ax.bar(np.arange(3)+(j-1)*.24,[base.loc[f'{fam}_{form}_{content}','rmse_rw'] for form in e['FORMS']],width=.23,label={'L':'Nível','D':'Mudança','LD':'Nível + mudança'}[content],color=COLORS[j])
 ax.axhline(base.loc['EJR','rmse_rw'],color='#99374d',ls='--',label='EJR base');ax.set(xticks=range(3),xticklabels=['Log','Desvio','Log com sinal'],ylim=(.55,.86),title=title,ylabel='RMSE / nenhuma mudança');ax.grid(axis='y',alpha=.15)
axs[0].legend(frameon=False,fontsize=9,ncol=2);fig.tight_layout();save(fig,'transformacoes')

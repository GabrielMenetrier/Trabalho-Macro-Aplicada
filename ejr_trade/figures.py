from pathlib import Path
import os
R=Path(__file__).resolve().parents[1]; H=R/'ejr_trade'
os.environ['MPLCONFIGDIR']=str(R/'tmp/matplotlib')
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#15354d','text.color':'#15354d','axes.titleweight':'bold','savefig.bbox':'tight'})
m=pd.read_csv(H/'tables/metrics.csv');g=pd.read_csv(H/'tables/global_diagnostics.csv')
z=m[(m.scenario=='main')&(m.period=='all')&(m.country=='POOL')]
fig,ax=plt.subplots(figsize=(9,3.6))
for model,label,color in [('EJR','EJR','#15354d'),('TOT_both','EJR + termos de troca','#c55d32'),('COM_both','EJR + cesta de commodities','#007f7b')]:
 a=z[z.model==model];ax.plot(a.h/12,a.rmse_rw,'o-',label=label,color=color,lw=2)
ax.axhline(1,color='#7c878f',ls='--',label='Nenhuma mudança');ax.set(xlabel='Horizonte da previsão (anos)',ylabel='RMSE / RMSE de nenhuma mudança',xticks=range(1,9),ylim=(.97,1.28));ax.legend(frameon=False,ncol=2,loc='upper left');ax.grid(alpha=.15)
fig.savefig(H/'figures/main.pdf');fig.savefig(H/'figures/main.png',dpi=170);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,4),sharey=True)
countries=['BRL','EUR','JPY','GBP','CAD','SEK']
for ax,model,title in zip(axs,['TOT_both','COM_both'],['Termos de troca observados','Cesta de commodities']):
 a=m[(m.scenario=='main')&(m.period=='all')&(m.model==model)&m.country.isin(countries)].pivot(index='country',columns='h',values='rmse_ejr').reindex(countries)
 v=100*(a.to_numpy()-1);im=ax.imshow(v,cmap='RdBu_r',vmin=-25,vmax=25,aspect='auto')
 for i in range(6):
  for j in range(8):ax.text(j,i,f'{v[i,j]:+.0f}',ha='center',va='center',fontsize=8,color='white' if abs(v[i,j])>17 else '#15354d')
 ax.set(xticks=range(8),xticklabels=range(1,9),yticks=range(6),yticklabels=countries,xlabel='Horizonte (anos)',title=title)
fig.colorbar(im,ax=axs,shrink=.8,label='Mudança percentual do RMSE frente ao EJR');fig.suptitle('Azul: melhora incremental. Vermelho: piora.',y=1.04)
fig.savefig(H/'figures/countries.pdf');fig.savefig(H/'figures/countries.png',dpi=170);plt.close(fig)
# Forecast errors as accumulated mean squared losses by origin, not portfolio wealth.
p=pd.read_csv(H/'tables/predictions.csv.gz');p=p[p.h==60]
fig,axs=plt.subplots(1,2,figsize=(10,3.6),sharex=True)
for ax,cc in zip(axs,['BRL','CAD']):
 a=p[p.country==cc].copy();dt=pd.to_datetime(a.origin)
 for model,label,col in [('TOT_both','Termos de troca','#c55d32'),('COM_both','Cesta de commodities','#007f7b')]:
  v=((a.actual-a[model])**2-(a.actual-a.EJR)**2).cumsum()/np.arange(1,len(a)+1)
  ax.plot(dt,10000*v,label=label,color=col,lw=2)
 ax.axhline(0,color='#15354d',lw=.8);ax.set(title=cc,ylabel='Diferença média acumulada de erro² × 10.000',xlabel='Mês de origem da previsão');ax.grid(alpha=.15)
axs[0].legend(frameon=False);fig.autofmt_xdate();fig.tight_layout();fig.savefig(H/'figures/errors.pdf');fig.savefig(H/'figures/errors.png',dpi=170);plt.close(fig)

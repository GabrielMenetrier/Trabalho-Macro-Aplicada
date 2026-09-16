from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR']=str(ROOT/'tmp/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import pandas as pd
OUT=ROOT/'output/figures'; TAB=ROOT/'output/tables'
CC=['BRL','EUR','JPY','GBP','CAD','SEK']
COLORS=['#164e63','#d97706','#0f766e','#a85568','#64748b','#7c3aed']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,
 'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#cbd5e1',
 'axes.labelcolor':'#334155','xtick.color':'#475569','ytick.color':'#475569',
 'grid.alpha':.4,'grid.color':'#cbd5e1','axes.axisbelow':True,'legend.frameon':False,
 'savefig.facecolor':'white','figure.facecolor':'white','pdf.fonttype':42})

def table(n): return pd.read_csv(TAB/f'{n}.csv')
def finish(fig,name):
    fig.savefig(OUT/f'{name}.pdf',bbox_inches='tight')
    fig.savefig(OUT/f'{name}.png',dpi=170,bbox_inches='tight'); plt.close(fig)
def times(index): return pd.PeriodIndex(index,freq='M').to_timestamp('M')
def line_nav(ax,r,label,color,ls='-'):
    nav=np.r_[1,np.cumprod(1+r.to_numpy())]
    t=times(r.index); prior=t[0]-pd.offsets.MonthEnd(1)
    ax.plot(pd.DatetimeIndex([prior]).append(t),100*nav,label=label,color=color,lw=1.7,ls=ls)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    a=table('classroom_replication'); a=a[a.spec=='SA_BLS']
    d=pd.read_csv(ROOT/'data/processed/classroom.csv',index_col=0).sort_index().loc['1995-01':'2026-04']
    q=np.log(d.S*d.P_US_SA/d.P_BR); q-=q.mean()
    fig,ax=plt.subplots(1,3,figsize=(8.1,2.8),layout='constrained')
    for i,h in enumerate([12,60,96]):
        y=np.log(d.S.shift(-h)/d.S); ok=q.notna()&y.notna()
        ax[i].scatter(q[ok],y[ok],s=7,alpha=.5,color=COLORS[0],edgecolors='none')
        beta,alpha=np.polyfit(q[ok],y[ok],1); xx=np.linspace(q.min(),q.max(),100)
        ax[i].plot(xx,alpha+beta*xx,color=COLORS[1],lw=1.8)
        ax[i].set(title=f'{h//12} anos | R² = {a[a.h==h].r2.iloc[0]:.3f}',xlabel='Desvio do câmbio real (log)')
        ax[i].grid(); ax[i].set_ylim(-1,1.6)
    ax[0].set_ylabel('Variação futura de log(R$/US$)')
    finish(fig,'classroom_scatter')
    fig,ax=plt.subplots(1,2,figsize=(8.1,3.05),layout='constrained')
    ax[0].plot(times(d.index),q,color=COLORS[0]); ax[0].axhline(0,color='#94a3b8',lw=.8)
    ax[0].set(title='Brasil: desvio real na amostra da aula',ylabel='Log, centrado na média'); ax[0].grid()
    ax[1].plot(a.h/12,a.beta,'o-',label='Replicação, calendário preservado',color=COLORS[0])
    ax[1].plot(a.h/12,a.slide_beta,'x',label='Slides',color=COLORS[1],ms=7)
    ax[1].fill_between(a.h/12,a.beta-1.96*a.se,a.beta+1.96*a.se,color=COLORS[0],alpha=.1)
    ax[1].set(title='Coeficiente por horizonte',xlabel='Anos',ylabel='Beta nominal'); ax[1].grid();ax[1].legend(fontsize=7,loc='lower left')
    finish(fig,'classroom_check')
    reg=table('horizon_regressions')
    fig,axes=plt.subplots(2,3,figsize=(8.1,4.65),sharex=True,sharey=True,layout='constrained')
    for c,ax in zip(CC,axes.flat):
        for k,lab,col in [('nominal','Nominal',COLORS[0]),('relative_prices','Preços relativos',COLORS[1])]:
            b=reg[(reg.country==c)&(reg.equation==k)]
            ax.plot(b.h/12,b.beta,'o-',ms=3,lw=1.5,label=lab,color=col)
            ax.fill_between(b.h/12,b.beta-1.96*b.se,b.beta+1.96*b.se,alpha=.1,color=col)
        ax.set_title(c,loc='left',fontweight='bold'); ax.axhline(0,color='#94a3b8',lw=.7); ax.grid()
    for ax in axes[-1]:ax.set_xlabel('Horizonte (anos)')
    axes[0,0].set_ylabel('Coeficiente'); axes[1,0].set_ylabel('Coeficiente'); axes[0,0].legend(fontsize=7)
    finish(fig,'country_betas')
    acc=table('forecast_accuracy'); a=acc[acc.model=='ejr'].pivot(index='country',columns='h',values='rmse_ratio').loc[CC+['POOL']]
    fig,ax=plt.subplots(figsize=(7.9,3.45),layout='constrained')
    im=ax.imshow(a.to_numpy(),cmap='RdBu_r',norm=TwoSlopeNorm(vmin=.5,vcenter=1,vmax=1.7),aspect='auto')
    for i in range(len(a)):
        for j in range(len(a.columns)):ax.text(j,i,f'{a.iloc[i,j]:.2f}',ha='center',va='center',fontsize=10,color='white' if abs(a.iloc[i,j]-1)>.43 else '#0f172a')
    ax.set_xticks(range(6),[str(h//12)+' anos' for h in a.columns]); ax.set_yticks(range(7),CC+['Agregado'])
    ax.set_title('Erro do EJR / erro do passeio aleatório',loc='left',pad=12,fontweight='bold')
    fig.colorbar(im,ax=ax,pad=.02,label='Menor que 1: EJR melhora a previsão')
    finish(fig,'forecast_heatmap')
    common=table('forecast_common_origins'); fig,ax=plt.subplots(1,2,figsize=(8.1,3.1),sharey=True,layout='constrained')
    for model,label,col in [('ejr','EJR',COLORS[0]),('fe','Painel com interceptos',COLORS[1]),('ols','OLS por país',COLORS[3]),('drift','Passeio com drift',COLORS[4]),('ppp','PPP meia-vida 5 anos',COLORS[2])]:
        for i,dd in enumerate([acc[acc.country=='POOL'],common]):
            b=dd[dd.model==model]; ax[i].plot(b.h/12,b.rmse_ratio,'o-',ms=3,label=label,color=col)
    for aa,title in zip(ax,['Todas as origens maduras','Mesmas origens: nov/2012–ago/2018']):
        aa.axhline(1,color='#64748b',lw=.9,ls='--'); aa.set(title=title,xlabel='Horizonte (anos)'); aa.grid()
    ax[0].set_ylabel('RMSE relativo ao passeio aleatório'); ax[1].legend(fontsize=6.8,loc='upper left')
    finish(fig,'forecast_models')
    ret=table('portfolio_returns'); pivot=ret.pivot(index='month',columns='strategy',values='net'); cash=ret[ret.strategy=='EJR + carry'].set_index('month').cash
    fig,ax=plt.subplots(2,1,figsize=(8.1,5.5),sharex=True,gridspec_kw={'height_ratios':[1.7,1]},layout='constrained')
    for name,col in [('EJR + carry',COLORS[0]),('Carry',COLORS[1]),('EJR cambial',COLORS[3]),('Coortes 60m',COLORS[2])]:
        rr=pivot[name]; line_nav(ax[0],rr,name,col)
        nav=np.r_[1,np.cumprod(1+rr)]; dd=nav/np.maximum.accumulate(nav)-1
        tt=times(rr.index); tt=pd.DatetimeIndex([tt[0]-pd.offsets.MonthEnd(1)]).append(tt)
        ax[1].plot(tt,dd,color=col,lw=1.2)
    line_nav(ax[0],cash,'Caixa USD',COLORS[4],'--')
    ax[0].set(ylabel='Patrimônio em USD | início = 100',title='Retornos líquidos de custos e spread de financiamento')
    ax[0].legend(ncol=3,fontsize=7.5,loc='upper left'); ax[1].set_ylabel('Queda desde o pico'); ax[1].yaxis.set_major_formatter(PercentFormatter(1))
    for aa in ax:aa.grid()
    finish(fig,'portfolio_wealth')
    w=pd.read_csv(TAB/'weights_main.csv',index_col=0)[CC]; contrib=pd.read_csv(TAB/'contributions_main.csv',index_col=0)[CC]
    fig,ax=plt.subplots(2,1,figsize=(8.1,4.9),gridspec_kw={'height_ratios':[1.2,1]},layout='constrained')
    im=ax[0].imshow(w.T,aspect='auto',cmap='RdBu',vmin=-.25,vmax=.25)
    ticks=np.arange(0,len(w),24);ax[0].set_xticks(ticks,[w.index[i][:4] for i in ticks]);ax[0].set_yticks(range(6),CC)
    ax[0].set_title('Posições efetivas: azul comprado, vermelho vendido',loc='left');fig.colorbar(im,ax=ax[0],pad=.02,label='Fração do patrimônio')
    value=contrib.mean()*12
    ax[1].bar(CC,value,color=[COLORS[0] if x>=0 else COLORS[3] for x in value],width=.6)
    ax[1].axhline(0,color='#94a3b8',lw=.8);ax[1].set_ylabel('Contribuição média anual');ax[1].yaxis.set_major_formatter(PercentFormatter(1));ax[1].grid(axis='y')
    finish(fig,'weights_contributions')
    sub=table('subperiods'); labels=['2010-2014','2015-2019','2020-2021','2022-2023','2024-2026']; x=np.arange(5)
    fig,ax=plt.subplots(1,2,figsize=(8.1,3.15),layout='constrained')
    for i,(name,col) in enumerate([('EJR + carry',COLORS[0]),('Carry',COLORS[1])]):
        values=sub[sub.strategy==name].set_index('period').loc[labels].mean_excess
        ax[0].bar(x+(i-.5)*.34,values,width=.34,label=name,color=col)
        rolling=(pivot[name]-cash).rolling(36).mean()*12
        ax[1].plot(times(rolling.index),rolling,label=name,color=col)
    ax[0].set_xticks(x,['2010–14','2015–19','2020–21','2022–23','2024–26'],rotation=25,fontsize=7)
    ax[0].set_title('Excesso sobre caixa USD por período'); ax[0].legend(fontsize=7)
    ax[1].set_title('Excesso médio: janela móvel de 36 meses')
    for aa in ax:aa.axhline(0,color='#94a3b8',lw=.8);aa.yaxis.set_major_formatter(PercentFormatter(1));aa.grid(axis='y')
    finish(fig,'performance_regimes')
    br=table('brl_returns').pivot(index='month',columns='strategy',values='net')
    er=table('etf_returns');fig,ax=plt.subplots(1,2,figsize=(8.1,3.5),layout='constrained')
    for name,col in [('Caixa BRL',COLORS[4]),('Caixa USD em BRL',COLORS[1]),('Alocacao USD/BRL',COLORS[0]),('Alocacao so cambio',COLORS[2])]:line_nav(ax[0],br[name],name,col)
    for (ticker,rule),a in er.groupby(['ticker','rule']):
        col=COLORS[1] if ticker=='SPY' else COLORS[0];ls='-' if rule=='Manter' else '--'
        line_nav(ax[1],a.set_index('month').net,ticker+' | '+('manter' if rule=='Manter' else 'sinal'),col,ls)
    line_nav(ax[1],br['Caixa BRL'],'Caixa BRL',COLORS[4],':')
    ax[0].set_title('Alocação entre caixa BRL e caixa USD');ax[1].set_title('O ativo em dólar muda o resultado')
    for aa in ax:aa.set_ylabel('Patrimônio em BRL | início = 100');aa.grid();aa.legend(fontsize=6.6,loc='upper left')
    finish(fig,'brl_assets')
    lat=table('latest_scenarios');b=lat[lat.h==60].set_index('country').loc[CC]
    fig,ax=plt.subplots(figsize=(7.9,2.9),layout='constrained');y=np.arange(6)
    v=np.expm1(b.pred_log);lo=b.band_low/b.spot-1;hi=b.band_high/b.spot-1
    ax.errorbar(v,y,xerr=np.stack([v-lo,hi-v]),fmt='o',color=COLORS[0],ecolor='#94a3b8',capsize=3)
    ax.axvline(0,color=COLORS[1],ls='--');ax.set_yticks(y,CC);ax.invert_yaxis();ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.set(xlabel='Variação da cotação moeda local / USD',title='Cenário de cinco anos e faixa baseada no erro histórico');ax.grid(axis='x')
    finish(fig,'latest_uncertainty')
    print('Saved 10 vector figures and PNG previews.')

if __name__=='__main__':main()

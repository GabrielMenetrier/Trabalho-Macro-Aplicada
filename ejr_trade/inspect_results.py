from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent
m=pd.read_csv(H/'tables/metrics.csv');g=pd.read_csv(H/'tables/global_diagnostics.csv');a=pd.read_csv(H/'tables/audit.csv');ins=pd.read_csv(H/'tables/in_sample.csv')
for title,t in [
 ('PRIMARY LONG COUNTRIES',m[(m.scenario=='main')&(m.period=='all')&m.country.isin(['BRL','CAD'])&m.model.isin(['TOT_both','COM_both'])][['h','country','model','rmse_rw','rmse_ejr']]),
 ('MERCHANDISE',m[(m.scenario=='merchandise')&(m.country=='POOL')][['h','model','first','last','n_dates','rmse_rw','rmse_ejr']]),
 ('GLOBAL 60',g[(g.h==60)&(g.country=='POOL')][['scenario','period','model','n_dates','rmse_rw','rmse_ejr']]),
 ('PRIMARY INFERENCE',m[(m.scenario=='main')&(m.period=='all')&(m.country=='POOL')&m.model.isin(['TOT_both','COM_both'])][['h','model','p_hac','p_holm']]),
 ('FIRST TRAIN',a[a.scenario=='main'].groupby('h').first().reset_index()[['h','origin','first_train','last_train','last_target','n_dates']]),
 ('IN SAMPLE 60',ins[ins.h==60].pivot(index='country',columns='model',values='adjusted_r2'))]:
 print('\n'+title+'\n'+t.to_string(index=False))

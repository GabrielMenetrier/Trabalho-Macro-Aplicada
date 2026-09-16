from pathlib import Path
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
H=Path(__file__).resolve().parent;m=pd.read_csv(H/'tables/metrics.csv');w=pd.read_csv(H/'tables/winners.csv');ins=pd.read_csv(H/'tables/in_sample.csv')
for title,v in [('BEST BY HORIZON',w[(w.country=='POOL')&(w.family.isin(['TOT','COM']))][['h','family','model','rmse_rw','rmse_ejr']]),
('FIXED 60',m[(m.h==60)&m.scenario.isin(['fixed','recent'])&m.model.isin(['EJR','TOT_LOG_LD','COM_DEV_LD'])][['scenario','country','model','rmse_rw','rmse_ejr']]),
('ADAPTIVE 60',m[(m.h==60)&(m.country=='POOL')&m.scenario.str.startswith('adaptive')&(m.model.isin(['EJR','TOT_LOG_LD','COM_DEV_LD'])|m.model.str.startswith('ADAPTIVE'))][['scenario','model','n_dates','first','last','rmse_rw','rmse_ejr']]),
('ALL FORMS AT 60',m[(m.h==60)&(m.country=='POOL')&(m.scenario=='fixed')&~m.model.str.startswith('JOINT')][['model','rmse_rw','rmse_ejr']])]:print('\n'+title+'\n'+v.to_string(index=False))

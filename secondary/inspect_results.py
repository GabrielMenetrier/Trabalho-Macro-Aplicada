from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent/'tables'
for file,cols in [
('variation_metrics',['name','period','cagr','vol','sharpe','maxdd','exposure']),
('hedge_variations',['asset','rule','cost','period','cagr','vol','sharpe','maxdd']),
('conditions',None),('timing_placebo',None),('hedge_intervals',None),
('horizon_agreement',None)]:
    a=pd.read_csv(H/(file+'.csv'))
    if file=='variation_metrics':a=a[a.name.isin(['Carry','Gate_0_ma1','Gate_0.02_ma6','Size_hist24_cap1','Size_fixed0.02','Rawq_coef0.5'])]
    if file=='hedge_variations':a=a[(a.rule.isin(['Fixed_0','Fixed_0.5','Fixed_1','FX_ma1_b0','Total_b0','Smooth_FX']))&(a.cost==2)&(a.period=='common')]
    print('\n'+file); print((a[cols] if cols else a).to_string(index=False))

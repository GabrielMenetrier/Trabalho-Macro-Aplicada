from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import strategies as st
from core import *
for quant in [.7,.8,.9]:
    for cost in [1,2]:st.add(f'Cohort_risk_q{quant}_cost{cost}','Carry','risk_increment',quant=quant,cost=cost,mode='cohort')
save(st.rows,'cohort_variations');save(st.intervals,'cohort_variation_intervals')
print('Cohort variants',len(st.weightcache))

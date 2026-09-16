from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import *
W,normal,full,_=make_policies();rows=[];choices=[];paths=[]
for family,members,start in [('long',['EJR_size','Size_structure','Gate_price','Commodity_blend'],'2013-03'),('common',['Size_structure','Gate_price','Cohort_risk','Commodity_blend'],'2018-04')]:
    books={n:book(W[n],start)[0] for n in members};net=np.stack([books[n].net.to_numpy() for n in members],axis=1);cash=books[members[0]].cash.to_numpy();exc=net-cash[:,None]
    first=np.flatnonzero(dates>=pd.Period(start))[0]
    for history in [36,60]:
        out=np.zeros((T,C));selection=-1;valid=np.zeros(T,bool)
        for t in range(first+history,T):
            # Complete returns through t-1. Choice applies to weights signalled at t.
            if selection<0 or dates[t].month==1:
                sample=exc[t-history:t];utility=12*(sample.mean(axis=0)-2.5*sample.var(axis=0,ddof=1));selection=int(np.argmax(utility));choices.append(dict(family=family,history=history,origin=str(dates[t]),last_return=str(dates[t-1]),chosen=members[selection]))
            out[t]=W[members[selection]][t];valid[t]=True
        begin=str(dates[np.flatnonzero(valid)[0]+2]);mask=dates>=pd.Period(begin)
        candidates={'Past_selection':out,'Equal_members':sum(W[n] for n in members)/len(members),'Carry':W['Carry']}
        # Hindsight best static member on this very window, explicitly non-investable selection.
        hist=[stats(book(W[n],begin)[0],mask)['ce5'] for n in members];oracle=members[int(np.argmax(hist))];candidates['Hindsight_static']=W[oracle]
        for name,w in candidates.items():
            b,_,_=book(w,begin);rows.append(dict(family=family,history=history,rule=name,first=begin,oracle=oracle if name=='Hindsight_static' else '',**stats(b,mask)))
            for t in np.flatnonzero(mask):paths.append(dict(family=family,history=history,rule=name,month=str(dates[t]),net=b.net[t],cash=b.cash[t]))
save(rows,'selection_metrics');save(choices,'selection_audit');save(paths,'selection_returns');print('Selection evaluations',len(rows))

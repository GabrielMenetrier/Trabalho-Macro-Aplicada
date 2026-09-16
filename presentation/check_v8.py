"""Validate the editorial revision against the preserved numerical sources."""
from pathlib import Path
H=Path(__file__).resolve().parent
s=(H/'qa_v7.py').read_text(encoding='utf-8').replace('_v7c','_v8').replace('_v7','_v8')
s=s.replace("H/'build/evidence_audit_v8.json'","H/'build/evidence_audit_v7.json'")
start=s.index("for universe,i in [('six',14),('three',16)]:")
end=s.index("for row,cc in enumerate",start)
s=s[:start]+'''palette={'Carry':'15354D','EJR':'0072B2','EJR_TOT_trio':'D55E00','TT_all':'D55E00'}
labels={'Carry':'Juros','EJR':'EJR','EJR_TOT_trio':'EJR + TT','TT_all':'EJR + TT'}
for universe,i in [('six',14),('three',16)]:
    sigs=['Carry','EJR','EJR_TOT_trio'] if universe=='six' else ['Carry','EJR','TT_all']
    entries=[]
    for met in ['Ranking','long60']:
        for sig in sigs:
            r=next(r for r in D[universe+'_table'] if r['scenario']=='Base' and
                (r['variant']==sig and r['metodo']==('Dois pares' if met=='Ranking' else 'Máximo Sharpe — risco de 60 meses') if universe=='six' else r['signal']==sig and r['method']==met))
            for h in [12,60]:entries.append((r['cagr_'+str(h)],met,sig,h,r))
    entries.sort(key=lambda e:-e[0])
    a=cells(i)[0];ck(f'Twelve ranked rows {i}',len(a)==13)
    tr=xml[i].findall('.//a:tbl/a:tr',ns)
    for j,(cagr,met,sig,h,r) in enumerate(entries,1):
        expected=[labels[sig],'Ranking' if met=='Ranking' else 'Máx. Sharpe',str(h)+' meses',pct(cagr),num(r['sharpe_'+str(h)]),pct(r['maxdd_'+str(h)])]
        ck(f'Ranked row {i} {j}',a[j]==expected)
        for col in [0,3]:
            tc=tr[j].findall('a:tc',ns)[col]
            ck(f'Color {i} {j} {col}',palette[sig] in [x.attrib['val'] for x in tc.findall('.//a:srgbClr',ns)])
for i in [13,14,15,16,17]:
    tx=' '.join(t.text or '' for t in xml[i].findall('.//a:t',ns))
    ck(f'Removed auxiliary variants {i}','controle' not in tx.lower() and 'combinado' not in tx.lower())
''' +s[end:]
(H/'qa_v8.py').write_text(s,encoding='utf-8')
exec(compile(s,str(H/'qa_v8.py'),'exec'),{'__file__':str(H/'qa_v8.py'),'__name__':'__main__'})

"""Run without changing Windows PowerShell execution policy."""
from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
for name in ['freeze','analyze','robustness','selection','inference','hedge','refinement','pair_risk','validate','build_report']:
    subprocess.run([sys.executable,str(R/'synthesis'/(name+'.py'))],cwd=R,check=True)
subprocess.run([str(R/'tools/tectonic.exe'),'synthesis/relatorio_sintese.tex','--outdir','output/pdf','--keep-logs'],cwd=R,check=True)
for name in ['qa_pdf','freeze']:
    subprocess.run([sys.executable,str(R/'synthesis'/(name+'.py'))],cwd=R,check=True)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    foreach ($script in @('freeze','analyze','robustness','selection','inference','hedge','refinement','pair_risk','validate','build_report')) {
        & './tools/python/python.exe' "synthesis/$script.py"
        if ($LASTEXITCODE -ne 0) { throw "Failed: $script" }
    }
    & './tools/tectonic.exe' synthesis/relatorio_sintese.tex --outdir output/pdf --keep-logs
    if ($LASTEXITCODE -ne 0) { throw 'PDF compilation failed' }
    & './tools/python/python.exe' synthesis/qa_pdf.py
    if ($LASTEXITCODE -ne 0) { throw 'PDF verification failed' }
    & './tools/python/python.exe' synthesis/freeze.py
} finally { Pop-Location }

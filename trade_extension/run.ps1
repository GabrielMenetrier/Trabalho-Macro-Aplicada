$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    foreach ($script in @('freeze','analyze','strategies','sensitivity','diagnostics','refine','risk_intervals','validate','build_report')) {
        & './tools/python/python.exe' "trade_extension/$script.py"
        if ($LASTEXITCODE -ne 0) { throw "Failed: $script" }
    }
    & './tools/tectonic.exe' trade_extension/relatorio_termos_troca.tex --outdir output/pdf --keep-logs
    if ($LASTEXITCODE -ne 0) { throw 'PDF compilation failed' }
    & './tools/python/python.exe' trade_extension/qa_pdf.py
    if ($LASTEXITCODE -ne 0) { throw 'PDF QA failed' }
    & './tools/python/python.exe' trade_extension/freeze.py
} finally { Pop-Location }

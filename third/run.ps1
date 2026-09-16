$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    foreach ($script in @('prepare','analyze','sensitivity','validate','build_report')) {
        & './tools/python/python.exe' "third/$script.py"
        if ($LASTEXITCODE -ne 0) { throw "Falha em $script" }
    }
    & './tools/tectonic.exe' third/relatorio_terciario.tex --outdir output/pdf --keep-logs
    if ($LASTEXITCODE -ne 0) { throw 'Falha na compilacao do PDF' }
    & './tools/python/python.exe' third/qa_pdf.py
    if ($LASTEXITCODE -ne 0) { throw 'Falha na verificacao do PDF' }
    & './tools/python/python.exe' third/freeze.py
    if ($LASTEXITCODE -ne 0) { throw 'Material anterior foi alterado' }
} finally { Pop-Location }

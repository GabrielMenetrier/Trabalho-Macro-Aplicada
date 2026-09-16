$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & './tools/python/python.exe' secondary/analyze.py
    if ($LASTEXITCODE -ne 0) { throw 'Análise falhou' }
    & './tools/python/python.exe' secondary/variations.py
    if ($LASTEXITCODE -ne 0) { throw 'Variações falharam' }
    & './tools/python/python.exe' secondary/validate.py
    if ($LASTEXITCODE -ne 0) { throw 'Auditoria falhou' }
    & './tools/python/python.exe' secondary/build_report.py
    if ($LASTEXITCODE -ne 0) { throw 'Relatório falhou' }
    & './tools/tectonic.exe' secondary/relatorio_secundario.tex --outdir output/pdf --keep-logs
    if ($LASTEXITCODE -ne 0) { throw 'Compilação falhou' }
} finally { Pop-Location }

param([switch]$Download, [switch]$Compile)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskPython = Join-Path $PSScriptRoot 'tools/python/python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { $taskPython = 'python' }
if ($Download) {
    & $taskPython 'src/download_data.py'
    if ($LASTEXITCODE -ne 0) { throw 'Falha no download' }
}
foreach ($taskScript in @('src/prepare_data.py','src/analyze.py')) {
    & $taskPython $taskScript
    if ($LASTEXITCODE -ne 0) { throw "Falha em $taskScript" }
}
& $taskPython -m pytest -q tests
if ($LASTEXITCODE -ne 0) { throw 'Testes falharam' }
foreach ($taskScript in @('src/make_figures.py','src/make_report_tables.py')) {
    & $taskPython $taskScript
    if ($LASTEXITCODE -ne 0) { throw "Falha em $taskScript" }
}
if ($Compile) {
    $taskTectonic = Join-Path $PSScriptRoot 'tools/tectonic.exe'
    if (-not (Test-Path -LiteralPath $taskTectonic)) { $taskTectonic = 'tectonic' }
    & $taskTectonic 'report/relatorio.tex' --outdir 'output/pdf' --keep-logs
    if ($LASTEXITCODE -ne 0) { throw 'Falha na compilacao LaTeX' }
    & $taskPython 'src/qa_pdf.py'
    if ($LASTEXITCODE -ne 0) { throw 'Falha na verificacao do PDF' }
}

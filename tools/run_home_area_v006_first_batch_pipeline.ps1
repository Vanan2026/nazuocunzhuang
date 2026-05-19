$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BundledPython = "C:\Users\23732\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (-not (Test-Path -LiteralPath $BundledPython)) {
    throw "Bundled Python not found: $BundledPython"
}

Push-Location $RepoRoot
try {
    & $BundledPython "tools\run_home_area_v006_first_batch_pipeline.py"
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}

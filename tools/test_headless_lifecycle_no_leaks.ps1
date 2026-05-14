param(
    [string]$GodotConsole = $env:GODOT_CONSOLE
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
if ([string]::IsNullOrWhiteSpace($GodotConsole)) {
    $GodotConsole = "C:\Users\23732\AppData\Local\Programs\Godot\4.6.1\Godot_v4.6.1-stable_win64_console.exe"
}

if (-not (Test-Path -LiteralPath $GodotConsole)) {
    throw "Godot console executable not found: $GodotConsole"
}

try {
    $ErrorActionPreference = "Continue"
    $output = & $GodotConsole --headless --verbose --path $ProjectRoot --script "res://tools/validate_scene_transition_spawn.gd" 2>&1
} finally {
    $ErrorActionPreference = "Stop"
}
$exitCode = $LASTEXITCODE
$text = $output -join "`n"

if ($exitCode -ne 0) {
    Write-Output $text
    throw "Godot validation exited with code $exitCode"
}

$forbiddenMarkers = @(
    "ObjectDB instances leaked",
    "resources still in use at exit",
    "Resource still in use:",
    "Leaked instance:"
)

$leaks = @($forbiddenMarkers | Where-Object { $text.Contains($_) })
if ($leaks.Count -gt 0) {
    Write-Output $text
    throw "headless lifecycle leaked resources: $($leaks -join ', ')"
}

Write-Output "OK: headless lifecycle leak test passed"

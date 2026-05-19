param(
    [string]$GodotConsole = $env:GODOT_CONSOLE
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
if ([string]::IsNullOrWhiteSpace($GodotConsole)) {
    $candidates = @(
        "D:\Godot\Godot_v4.6.1-stable_win64_console.exe",
        "C:\Users\23732\AppData\Local\Programs\Godot\4.6.1\Godot_v4.6.1-stable_win64_console.exe"
    )
    $GodotConsole = ($candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1)
}

if ([string]::IsNullOrWhiteSpace($GodotConsole) -or -not (Test-Path -LiteralPath $GodotConsole)) {
    throw "Godot console executable not found. Set GODOT_CONSOLE or update test_headless_lifecycle_no_leaks.ps1."
}

$cases = @(
    @{ Name = "transition_spawn"; Script = "res://tools/validate_scene_transition_spawn.gd"; Args = @("--watchdog-timeout=60") },
    @{ Name = "final_art_experience"; Script = "res://tools/validate_final_art_experience.gd"; Args = @() },
    @{ Name = "home_area_visual_contract"; Script = "res://tools/validate_region_home_area_visual_walkthrough.gd"; Args = @("--check-only", "--watchdog-timeout=60") },
    @{ Name = "save_load_boundary"; Script = "res://tools/validate_save_load_boundary.gd"; Args = @("--watchdog-timeout=60") }
)

$forbiddenMarkers = @(
    "ObjectDB instances leaked",
    "resources still in use at exit",
    "Resource still in use:",
    "Leaked instance:",
    "unclaimed string names at exit"
)

foreach ($case in $cases) {
    $commandArgs = @("--headless", "--path", $ProjectRoot, "--script", $case.Script)
    if ($case.Args.Count -gt 0) {
        $commandArgs += "--"
        $commandArgs += $case.Args
    }

    $safeName = [regex]::Replace([string]$case.Name, "[^A-Za-z0-9_-]", "_")
    $logPath = "C:\tmp\hl_${PID}_${safeName}.log"
    $quotedArgs = @()
    foreach ($argument in $commandArgs) {
        $quotedArgs += '"' + ([string]$argument).Replace('"', '\"') + '"'
    }
    $commandLine = '"' + $GodotConsole + '" ' + ($quotedArgs -join ' ') + ' > "' + $logPath + '" 2>&1'
    & cmd.exe /d /c $commandLine
    $exitCode = $LASTEXITCODE

    if (-not (Test-Path -LiteralPath $logPath)) {
        throw "Godot validation $($case.Name) did not create log file: $logPath"
    }
    $text = [System.IO.File]::ReadAllText($logPath, [System.Text.Encoding]::UTF8)

    if ($exitCode -ne 0) {
        Write-Output $text
        throw "Godot validation $($case.Name) exited with code $exitCode"
    }

    $leaks = @($forbiddenMarkers | Where-Object { $text.Contains($_) })
    if ($leaks.Count -gt 0) {
        Write-Output $text
        throw "headless lifecycle leaked resources in $($case.Name): $($leaks -join ', ')"
    }
}

Write-Output "OK: headless lifecycle leak test passed ($($cases.Count) validators)"

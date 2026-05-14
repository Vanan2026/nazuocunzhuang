param(
    [string]$ManifestPath = "docs/trailer/concept_trailer_2d_slice_2026-05-14.json",
    [string]$DocumentPath = "docs/trailer/concept_trailer_2d_slice_2026-05-14.md",
    [string]$CaptureScriptPath = "tools/capture_concept_trailer_frames.gd"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure([string]$Message) {
    $failures.Add($Message) | Out-Null
}

function Resolve-RepoPath([string]$Path) {
    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }
    return Join-Path $root $Path
}

$manifestFullPath = Resolve-RepoPath $ManifestPath
$documentFullPath = Resolve-RepoPath $DocumentPath
$captureScriptFullPath = Resolve-RepoPath $CaptureScriptPath

foreach ($path in @($manifestFullPath, $documentFullPath, $captureScriptFullPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        Add-Failure "missing required package file: $path"
    }
}

if ($failures.Count -eq 0) {
    $manifest = Get-Content -LiteralPath $manifestFullPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $document = Get-Content -LiteralPath $documentFullPath -Raw -Encoding UTF8
    $shots = @($manifest.shots)
    $targetDuration = [double]$manifest.target_duration_seconds
    $totalDuration = 0.0
    $shotIds = New-Object System.Collections.Generic.HashSet[string]
    $captureFiles = New-Object System.Collections.Generic.HashSet[string]
    $regions = New-Object System.Collections.Generic.HashSet[string]
    $poses = New-Object System.Collections.Generic.HashSet[string]

    if ($targetDuration -lt 15.0 -or $targetDuration -gt 20.0) {
        Add-Failure "target_duration_seconds is $targetDuration, expected 15-20"
    }
    if ($shots.Count -eq 0) {
        Add-Failure "manifest shots must be a non-empty list"
    }

    for ($index = 0; $index -lt $shots.Count; $index++) {
        $shot = $shots[$index]
        $shotId = [string]$shot.id
        $captureFile = [string]$shot.capture_file
        $duration = [double]$shot.duration_seconds
        $totalDuration += $duration

        if ($shotId -notmatch "^shot_\d{2}_[a-z0-9_]+$") {
            Add-Failure "shot $($index + 1) has invalid id: $shotId"
        }
        if (-not $shotIds.Add($shotId)) {
            Add-Failure "duplicate shot id: $shotId"
        }
        if ($document -notlike "*$shotId*") {
            Add-Failure "document does not mention shot id: $shotId"
        }
        if ($captureFile -notmatch "^\d{2}_[a-z0-9_]+\.png$") {
            Add-Failure "$shotId has invalid capture_file: $captureFile"
        }
        if (-not $captureFiles.Add($captureFile)) {
            Add-Failure "duplicate capture_file: $captureFile"
        }
        if ($duration -le 0.0) {
            Add-Failure "$shotId duration must be positive"
        }

        $regions.Add([string]$shot.region_id) | Out-Null
        $poses.Add([string]$shot.pose) | Out-Null
    }

    if ([Math]::Abs($totalDuration - $targetDuration) -gt 0.01) {
        Add-Failure "shot duration total $totalDuration does not match target $targetDuration"
    }
    if ($totalDuration -lt 15.0 -or $totalDuration -gt 20.0) {
        Add-Failure "shot duration total is $totalDuration, expected 15-20"
    }
    foreach ($region in @("Region_HomeArea", "Region_BackFarm")) {
        if (-not $regions.Contains($region)) {
            Add-Failure "manifest missing required region: $region"
        }
    }
    if (-not $poses.Contains("veranda_rest")) {
        Add-Failure "manifest missing veranda_rest pose"
    }
    if (-not ($poses | Where-Object { $_.StartsWith("farm_") })) {
        Add-Failure "manifest missing BackFarm farm interaction pose"
    }
    if (-not $poses.Contains("walk")) {
        Add-Failure "manifest missing protagonist walk pose"
    }

    foreach ($source in @($manifest.source_files)) {
        $sourcePath = Join-Path $root ([string]$source)
        if (-not (Test-Path -LiteralPath $sourcePath)) {
            Add-Failure "manifest source file does not exist: $source"
        }
    }

    foreach ($requiredText in @("shot_01_home_wakeup", "Godot", "HeyGen")) {
        if ($document -notlike "*$requiredText*") {
            Add-Failure "document missing required text: $requiredText"
        }
    }
}

if ($failures.Count -gt 0) {
    foreach ($failure in $failures) {
        Write-Error "FAIL: $failure"
    }
    exit 1
}

Write-Host "OK: concept trailer package validated"

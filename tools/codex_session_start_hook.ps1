Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-TextFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [int]$MaxChars = 4000
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return "[missing] $Path"
    }

    $text = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    if ($text.Length -gt $MaxChars) {
        return $text.Substring(0, $MaxChars) + "`n[truncated]"
    }
    return $text
}

function Get-Section {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Heading,
        [int]$MaxChars = 1200
    )

    $escaped = [regex]::Escape($Heading)
    $pattern = "(?ms)^##\s+$escaped\s*$\n(.*?)(?=^##\s+|\z)"
    $match = [regex]::Match($Text, $pattern)
    if (-not $match.Success) {
        return "[missing section] $Heading"
    }

    $section = $match.Groups[1].Value.Trim()
    if ($section.Length -gt $MaxChars) {
        return $section.Substring(0, $MaxChars) + "`n[truncated]"
    }
    return $section
}

$stdin = [Console]::In.ReadToEnd()
$cwd = (Get-Location).Path
try {
    if ($stdin.Trim().Length -gt 0) {
        $event = $stdin | ConvertFrom-Json
        if ($event.PSObject.Properties.Name -contains "cwd" -and $event.cwd) {
            $cwd = [string]$event.cwd
        }
    }
} catch {
    # Hook input is diagnostic only; continue from current working directory.
}

$statusPath = Join-Path $cwd ".codex/status.md"
$projectStatePath = Join-Path $cwd ".codex/context/project_state.md"
$roadmapPath = Join-Path $cwd ".codex/context/roadmap.md"
$decisionsPath = Join-Path $cwd ".codex/context/decisions.md"

$status = Read-TextFile -Path $statusPath -MaxChars 5000
$projectState = Read-TextFile -Path $projectStatePath -MaxChars 2500
$roadmap = Read-TextFile -Path $roadmapPath -MaxChars 2500
$decisions = Read-TextFile -Path $decisionsPath -MaxChars 2500

$message = @"
Nazuo Village session-start recovery capsule:

Required resume order:
1. Read AGENTS.md first.
2. Read .codex/status.md and continue from its 下一步 section.
3. Then read .codex/context/project_state.md, roadmap.md, and decisions.md as needed.
4. For Godot validation, probe http://127.0.0.1:8000/mcp via streamable-http before falling back to headless CLI.
5. Keep the project non-combat, cozy, data-driven, and fixed 3/4 top-down.

Current task:
$(Get-Section -Text $status -Heading "当前任务" -MaxChars 500)

Current phase:
$(Get-Section -Text $status -Heading "当前阶段" -MaxChars 700)

Next step:
$(Get-Section -Text $status -Heading "下一步" -MaxChars 1200)

Validation status:
$(Get-Section -Text $status -Heading "验证状态" -MaxChars 1200)

Known risks/blockers:
$(Get-Section -Text $status -Heading "风险 / 阻塞" -MaxChars 1200)

Project-state excerpt:
$projectState

Roadmap excerpt:
$roadmap

Decision excerpt:
$decisions
"@

$result = [ordered]@{
    continue = $true
    suppressOutput = $false
    systemMessage = $message.Trim()
}

$result | ConvertTo-Json -Depth 6 -Compress

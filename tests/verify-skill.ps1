$repoRoot = (Resolve-Path "$PSScriptRoot/..").Path
$skillPath = Join-Path $repoRoot ".agents/skills/remembrall/SKILL.md"

if (-not (Test-Path $skillPath)) {
    Write-Error "FAIL: $skillPath does not exist."
    exit 1
}

$content = Get-Content $skillPath -Raw

$requiredTokens = @(
    "name: remembrall",
    "description: Use when",
    "## Zero Re-scan Protocol",
    "## Update Protocol",
    "## Anti-Bloat & Pruning Policy",
    "## Sync Protocol"
)

foreach ($tok in $requiredTokens) {
    if (-not ($content -match [regex]::Escape($tok))) {
        Write-Error "FAIL: Required pattern '$tok' not found in $skillPath."
        exit 1
    }
}

Write-Output "PASS: .agents/skills/remembrall/SKILL.md passed all structural checks."
exit 0

$repoRoot = (Resolve-Path "$PSScriptRoot/..").Path
$rulePath = Join-Path $repoRoot ".agents/rules/remembrall.md"

if (-not (Test-Path $rulePath)) {
    Write-Error "FAIL: $rulePath does not exist."
    exit 1
}

$content = Get-Content $rulePath -Raw
$lines = Get-Content $rulePath

if ($lines.Count -gt 35) {
    Write-Error "FAIL: $rulePath has $($lines.Count) lines, exceeds token-saving limit of 35 lines."
    exit 1
}

$requiredTokens = @(
    "trigger: always_on",
    ".remembrall.md",
    "Pre-flight",
    "Post-flight"
)

foreach ($tok in $requiredTokens) {
    if (-not ($content -match [regex]::Escape($tok))) {
        Write-Error "FAIL: Required pattern '$tok' not found in $rulePath."
        exit 1
    }
}

Write-Output "PASS: .agents/rules/remembrall.md passed all structural checks."
exit 0

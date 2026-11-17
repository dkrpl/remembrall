$repoRoot = (Resolve-Path "$PSScriptRoot/..").Path
$manifestPath = Join-Path $repoRoot ".remembrall.md"

if (-not (Test-Path $manifestPath)) {
    Write-Error "FAIL: $manifestPath does not exist."
    exit 1
}

$content = Get-Content $manifestPath -Raw
$lines = Get-Content $manifestPath

if ($lines.Count -gt 120) {
    Write-Error "FAIL: .remembrall.md has $($lines.Count) lines, exceeds limit of 120."
    exit 1
}

$requiredSections = @(
    "# Project Overview",
    "## Feature Manifest",
    "## Technical Findings",
    "| ID | Fitur | Status | File Terkait | Catatan |"
)

foreach ($sec in $requiredSections) {
    if (-not ($content -match [regex]::Escape($sec))) {
        Write-Error "FAIL: Required section '$sec' not found in .remembrall.md."
        exit 1
    }
}

Write-Output "PASS: .remembrall.md passed all structural checks."
exit 0

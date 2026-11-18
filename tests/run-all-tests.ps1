Write-Output "=== RUNNING REMEMBRALL TEST SUITE ==="

$repoRoot = (Resolve-Path "$PSScriptRoot/..").Path

$psTests = @(
    "tests/verify-manifest.ps1",
    "tests/verify-skill.ps1",
    "tests/verify-rule.ps1"
)

$allPassed = $true

foreach ($test in $psTests) {
    Write-Output "Running $test..."
    & powershell -ExecutionPolicy Bypass -File (Join-Path $repoRoot $test)
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Test $test FAILED."
        $allPassed = $false
    }
}

Write-Output "`nRunning Python Unit Tests..."
& python -m unittest discover -s (Join-Path $repoRoot "tests") -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python unit test suite FAILED."
    $allPassed = $false
}

Write-Output "`nRunning Node.js Unit Tests..."
& node --test (Join-Path $repoRoot "tests/*.test.js")
if ($LASTEXITCODE -ne 0) {
    Write-Error "Node.js unit test suite FAILED."
    $allPassed = $false
}

Write-Output "`nTesting CLI Validation..."
& python (Join-Path $repoRoot ".agents/skills/remembrall/scripts/remembrall.py") validate
if ($LASTEXITCODE -ne 0) {
    Write-Error "CLI validation FAILED."
    $allPassed = $false
}

Write-Output "`nRunning Skill Leaderboard Evaluations..."
& python (Join-Path $repoRoot "evals/run_evals.py")
if ($LASTEXITCODE -ne 0) {
    Write-Error "Skill Leaderboard evals FAILED."
    $allPassed = $false
}

Write-Output "`n--- Verifying File Links & Consistency ---"
$manifestPath = Join-Path $repoRoot ".remembrall.md"
$lines = Get-Content $manifestPath

$missingFiles = @()
foreach ($line in $lines) {
    if ($line -match '^\|\s*(F-\d+)\s*\|\s*([^\|]+)\s*\|\s*(\w+)\s*\|\s*([^\|]+)\s*\|') {
        $fid = $matches[1]
        $feature = $matches[2].Trim()
        $status = $matches[3].Trim()
        $rawPaths = $matches[4].Trim()
        
        Write-Output "[$fid] $feature ($status) -> $rawPaths"
        $fileList = $rawPaths -split ','
        foreach ($f in $fileList) {
            $trimmed = $f.Trim()
            $resolvedPath = Join-Path $repoRoot $trimmed
            if (-not (Test-Path $resolvedPath)) {
                $missingFiles += "${fid}: $trimmed"
            }
        }
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Error "FAIL: The following files referenced in .remembrall.md do not exist:"
    $missingFiles | ForEach-Object { Write-Error "  - $_" }
    exit 1
}

if (-not $allPassed) {
    Write-Error "E2E SUITE FAILED."
    exit 1
}

Write-Output "`n=== ALL TESTS PASSED SUCCESSFULLY! ==="
exit 0

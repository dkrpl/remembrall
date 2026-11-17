# Remembrall Pre-Commit Hook (PowerShell)
Write-Output "🔮 Running Remembrall pre-commit health check..."

if (Test-Path ".remembrall.md") {
    python .agents/skills/remembrall/scripts/remembrall.py validate
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Commit rejected: .remembrall.md failed validation or exceeded 120-line budget."
        Write-Host "   Run 'python .agents/skills/remembrall/scripts/remembrall.py prune' to clean up."
        exit 1
    }
    Write-Output "✅ Remembrall manifest verified."
} else {
    Write-Warning "⚠️ .remembrall.md not found in project root."
}

exit 0

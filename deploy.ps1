param(
    [string]$msg = ""
)

if ($msg -eq "") {
    $msg = Read-Host "Descrivi le modifiche"
}

Write-Host "`nAggiunta file..." -ForegroundColor Cyan
git add -A

Write-Host "Commit: $msg" -ForegroundColor Cyan
git commit -m $msg

Write-Host "Push su GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host "`nDone! Vercel sta aggiornando l'app." -ForegroundColor Green
Write-Host "Controlla: https://uflow-woad.vercel.app" -ForegroundColor Green

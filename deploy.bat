@echo off

set MSG=%*

if "%MSG%"=="" (
    set /p MSG="Descrivi le modifiche: "
)

echo.
echo Aggiunta file...
git add -A

echo Commit: %MSG%
git commit -m "%MSG%"

echo Push su GitHub...
git push origin main

echo.
echo Done! Vercel sta aggiornando l'app.
echo Controlla: https://uflow-woad.vercel.app

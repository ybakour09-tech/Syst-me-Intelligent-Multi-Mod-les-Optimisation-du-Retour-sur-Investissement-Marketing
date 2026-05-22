@echo off
chcp 65001 > NUL
echo ===================================================
echo       LANCEMENT DE PRISMA - MARKETING ROI
echo ===================================================
echo.
echo 1. Demarrage du serveur d'Intelligence Artificielle...
start "Prisma API Backend" cmd /k "python -m uvicorn api:app --host 127.0.0.1 --port 8000"

echo Patientez pendant le chargement des modeles...
timeout /t 4 /nobreak > NUL

echo 2. Ouverture du Dashboard Prisma...
start "" "%~dp0\dashboard\index.html"

echo.
echo ===================================================
echo Le projet est en cours d'execution !
echo /!\ NE FERMEZ PAS la nouvelle fenetre noire (API).
echo /!\ Si le tableau de bord indique une erreur, verifiez 
echo     que la fenetre de l'API affiche "Application startup complete".
echo ===================================================
pause

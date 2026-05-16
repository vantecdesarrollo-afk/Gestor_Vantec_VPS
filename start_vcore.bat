@echo off
cd /d "%~dp0"
title VCore L6 - Motor de Arranque Dual (PERSISTENTE) [cite: 4]
color 0B

echo ===================================================
echo      INICIANDO SISTEMA VCORE L6 (PRODUCCION)
echo ===================================================
echo.
if exist venv\Scripts\activate.bat ( [cite: 5]
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] No hay entorno virtual. Corra install_vcore.bat primero.
    pause
    exit
)

echo [OK] Levantando Servidor Principal (API)...
start "VCore API Server" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000"

echo [OK] Levantando Motor de Ingesta (Watcher)...
start "VCore Watcher" cmd /k "python watcher.py"

echo.
echo =================================================== [cite: 6]
echo [EXITO] Motores lanzados. Acceda a: http://localhost:8000
echo ===================================================
pause
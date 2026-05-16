@echo off
title DETENER VCORE L6 - LIMPIEZA TOTAL
color 0C
echo -----------------------------------------------------------
echo   🛑 FINALIZANDO TODOS LOS MOTORES VCORE L6
echo -----------------------------------------------------------
echo.

:: Matamos python.exe (el nuevo motor) y pythonw.exe (el antiguo) [cite: 2]
echo [1/3] Finalizando procesos de Python (Visibles e Invisibles)...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1

:: Limpieza de residuos de red [cite: 2]
echo [2/3] Limpiando residuos de Uvicorn...
taskkill /F /IM uvicorn.exe /T >nul 2>&1

echo [3/3] Liberando puerto 8000...
echo.
echo ----------------------------------------------------------- [cite: 3]
echo [EXITO] El sistema se ha detenido y los puertos estan libres.
echo -----------------------------------------------------------
pause
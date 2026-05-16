@echo off
title VCore L6 - Empaquetador Maestro v6.3.1
color 0A
set "DESTINO=%USERPROFILE%\Desktop\VCORE_INSTALADOR_LIMPIO"

if exist "%DESTINO%" rmdir /s /q "%DESTINO%"
mkdir "%DESTINO%"

:: Archivo de exclusiones (SE ELIMINÓ .SQL DE ESTA LISTA) 
echo \storage\> excl.txt
echo \Operacion_CFDI\>> excl.txt
echo \venv\>> excl.txt
echo \__pycache__\>> excl.txt
echo \.git\>> excl.txt
echo \statics\>> excl.txt
echo \src\static\>> excl.txt
echo .log>> excl.txt
echo .db>> excl.txt
echo excl.txt>> excl.txt

echo [PROCESANDO] Creando paquete maestro incluyendo ADN SQL...
xcopy "%CD%\*" "%DESTINO%\" /E /I /Q /Y /EXCLUDE:excl.txt
del excl.txt

echo.
echo ===================================================
echo [EXITO] PAQUETE UNIVERSAL CON ADN SQL LISTO EN EL ESCRITORIO
echo ===================================================
pause
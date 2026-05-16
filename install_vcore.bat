@echo off
:: ANCLAJE DE RUTA: Garantiza ejecución en la carpeta del script (DINÁMICO)
cd /d "%~dp0"
setlocal enabledelayedexpansion
title INSTALADOR MAESTRO VANTEC VCORE v6.4.2 (EDICION ORO)

echo -----------------------------------------------------------
echo   🛡️ VCORE L6 - DESPLIEGUE FINAL (UNICODE + AUTO-START)
echo -----------------------------------------------------------
echo.

:: 1. Bóveda de Licencia
echo [1/7] Preparando Bóveda de Licenciamiento en src\license...
if not exist "src\license" mkdir "src\license"
powershell -NoProfile -Command "(Get-WmiObject -Class Win32_ComputerSystemProduct).UUID" > "src\license\machine_id.txt"

:: 2. Base de Datos - BUSQUEDA DE PROFUNDIDAD
echo [2/7] Localizando Motor PostgreSQL en el Servidor...
set "DB_NAME=vcore_blank_db"
set "DB_USER=postgres"
set "PGPASSWORD=postgres"
set "PSQL_CMD="

:: Intento 1: ¿Está en el PATH global?
where psql >nul 2>&1
if %errorlevel% equ 0 (
    set "PSQL_CMD=psql"
    goto :db_create
)

:: Intento 2: Buscar en Archivos de Programa (x64)
for /f "delims=" %%i in ('dir /b /s "C:\Program Files\PostgreSQL\psql.exe" 2^>nul') do (
    set "PSQL_CMD=%%i"
    goto :db_create
)

:: Intento 3: Buscar en Archivos de Programa (x86)
for /f "delims=" %%i in ('dir /b /s "C:\Program Files (x86)\PostgreSQL\psql.exe" 2^>nul') do (
    set "PSQL_CMD=%%i"
    goto :db_create
)

:db_create
if "%PSQL_CMD%"=="" (
    echo.
    echo ❌ [ERROR CRITICO] No se encontro psql.exe. 
    echo Verifique que PostgreSQL este instalado o agregue la carpeta /bin al PATH.
    pause
    exit /b
)

echo [+] Motor detectado en: "%PSQL_CMD%"
echo [+] Creando base de datos %DB_NAME%...
"%PSQL_CMD%" -h localhost -U %DB_USER% -c "CREATE DATABASE %DB_NAME%;" >nul 2>&1

:: 3. Entorno Virtual
echo [3/7] Instalando Dependencias (Pandas + Excel + Bcrypt Fix)...
if exist venv rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install bcrypt==4.0.1 passlib==1.7.4 pandas==2.2.1 openpyxl==3.1.2 pypdf >nul
pip install -r requirements.txt >nul

:: 4. Variables de Entorno (.env)
echo [4/7] Configurando variables de entorno dinamicas...
set "BASE_PATH=%CD%"
set "ESCAPED_PATH=%BASE_PATH:\=\\%"
(
echo WKHTMLTOPDF_PATH=%BASE_PATH%\wkhtmltopdf\bin\wkhtmltopdf.exe
echo DATABASE_URL=postgresql+asyncpg://%DB_USER%:%PGPASSWORD%@localhost:5432/%DB_NAME%
echo WATCHER_ZONES={"%ESCAPED_PATH%\\Operacion_CFDI\\Upload_Universal": null}
echo STORAGE_PATH=%ESCAPED_PATH%\\Operacion_CFDI\\Files
echo INVALID_ADN_PATH=%ESCAPED_PATH%\\Operacion_CFDI\\Invalid_ADN
echo ORPHANS_PATH=%ESCAPED_PATH%\\Operacion_CFDI\\Orphans
echo SESSION_INACTIVITY_TIMEOUT_MINUTES=15
echo SESSION_MAX_LIFETIME_MINUTES=30
) > .env

:: 5. Estructura de Operación e Inteligencia SQL
echo [5/7] Configurando Bóvedas e Inyectando ADN Maestro...

:: A. Creación de Carpetas Operativas (SE REPARÓ EL DESMADRE AQUÍ)
set "OP_DIR=Operacion_CFDI"
if not exist "%OP_DIR%\Upload_Universal" mkdir "%OP_DIR%\Upload_Universal"
if not exist "%OP_DIR%\Orphans" mkdir "%OP_DIR%\Orphans"
if not exist "%OP_DIR%\Invalid_ADN" mkdir "%OP_DIR%\Invalid_ADN"
if not exist "%OP_DIR%\logs" mkdir "%OP_DIR%\logs"
if not exist "%OP_DIR%\Files" mkdir "%OP_DIR%\Files"
:: Ejemplo piloto para forzar el aislamiento L6 de logs duplicados
if not exist "%OP_DIR%\Files\VCO1307234VA\logs\duplicates" mkdir "%OP_DIR%\Files\VCO1307234VA\logs\duplicates"

if not exist "tmp" mkdir "tmp"
if not exist "static" mkdir "static"

:: B. Inyección Automatizada del Esquema Maestro
echo [+] Inyectando 19 tablas y analitica desde master_schema_L6.sql...
"%PSQL_CMD%" -h localhost -U %DB_USER% -d %DB_NAME% -f "src\database\master_schema_L6.sql"

:: C. Usuario Semilla
echo [+] Creando Usuario Administrador Maestro...
venv\Scripts\python.exe seed_admin.py

:: 6. Motor Silencioso
echo [6/7] Inyectando Motor de Arranque Invisible...
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo strPath = CreateObject^("Scripting.FileSystemObject"^).GetParentFolderName^(WScript.ScriptFullName^)
echo WshShell.CurrentDirectory = strPath
echo WshShell.Run "venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000", 0, False
echo WshShell.Run "venv\Scripts\python.exe watcher.py", 0, False
) > arranque_silencioso.vbs

:: 7. Accesos Directos
echo [7/7] Configurando Persistencia...
powershell -NoProfile -Command ^
    "$wshell = New-Object -ComObject WScript.Shell; " ^
    "$desktop = [System.Environment]::GetFolderPath('Desktop'); " ^
    "$startup = [System.Environment]::GetFolderPath('Startup'); " ^
    "$sc1 = $wshell.CreateShortcut(\"$desktop\Iniciar_VCore.lnk\"); " ^
    "$sc1.TargetPath = '%BASE_PATH%\arranque_silencioso.vbs'; " ^
    "$sc1.WorkingDirectory = '%BASE_PATH%'; " ^
    "$sc1.IconLocation = 'C:\WINDOWS\System32\imageres.dll,11'; " ^
    "$sc1.Save(); " ^
    "$sc2 = $wshell.CreateShortcut(\"$startup\VCore_AutoStart.lnk\"); " ^
    "$sc2.TargetPath = '%BASE_PATH%\arranque_silencioso.vbs'; " ^
    "$sc2.WorkingDirectory = '%BASE_PATH%'; " ^
    "$sc2.Save();"

echo.
echo =======================================================
echo   ✅ INSTALACION BLINDADA: EL SISTEMA ESTA EN VIVO
echo =======================================================
echo.
pause
wscript.exe arranque_silencioso.vbs
start http://localhost:8000
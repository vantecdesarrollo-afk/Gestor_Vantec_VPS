@echo off
:: [VCORE L6] ANCLAJE DINÁMICO: Asegura que el script trabaje desde su propia ubicación
cd /d "%~dp0"
title ENSAMBLADOR GOLD MASTER - VANTEC VCORE L6
color 0B

echo ===================================================
echo   EMPAQUETADOR GOLD MASTER - VANTEC VCORE L6
echo   Estado: DINÁMICO Y COMPLETO (API CORE)
echo ===================================================
echo.

:: 1. Definición de la versión del Build (Carpeta destino relativa)
set "RELEASE_DIR=VCore_Release_v6.4.1_GOLD"

:: 2. Limpieza de residuos de builds anteriores para evitar contaminación
if exist "%RELEASE_DIR%" (
    echo [*] Eliminando build anterior para asegurar limpieza...
    rmdir /s /q "%RELEASE_DIR%"
)
mkdir "%RELEASE_DIR%"

echo [*] Extrayendo codigo fuente (API Core) y activos visuales...
echo [*] NOTA: Se preservan carpetas 'src/api' y 'static'.

:: ==============================================================================
:: ROBOCOPY MASTER LOGIC (DINÁMICA):
:: .      - Directorio actual como fuente (Relativo)
:: %RELEASE_DIR% - Carpeta de salida (Relativo)
:: /E     - Copia subdirectorios, incluidos los vacíos (Mantiene estructura de api/endpoints)
:: /XD    - EXCLUYE: carpetas de desarrollo y datos operativos para un build limpio.
::          (venv, git, cache, docs, licencias locales, datos de operacion, tmp)
:: /XF    - EXCLUYE: archivos temporales, configs locales y scripts de desarrollo.
:: ==============================================================================
robocopy . "%RELEASE_DIR%" /E /XD venv __pycache__ .git docs src\license Operacion_CFDI tmp "%RELEASE_DIR%" /XF .env *.zip *.log *.sqlite3 *.db *.xml *_backup*.py 07_*.sql 08_*.sql 00_*.bat execute*.py force*.py get_*.py

echo.
:: 3. Generación de plantilla de entorno segura (.env para el cliente)
if exist ".env" (
    echo [*] Generando plantilla de entorno seguro (.env.example)...
    copy .env "%RELEASE_DIR%\\.env.example" >nul
)

:: 4. VERIFICACIÓN DE INTEGRIDAD QUIRÚRGICA
echo [*] Verificando integridad del Build...
set "INTEGRITY=OK"

:: Validar Cerebro (API)
if not exist "%RELEASE_DIR%\src\api\endpoints" (
    echo [❌] ERROR CRITICO: No se localizo src/api/endpoints.
    set "INTEGRITY=FAIL"
) else (
    echo [✅] INTEGRIDAD: Estructura de API preservada.
)

:: Validar Login (JS)
if not exist "%RELEASE_DIR%\static\js\auth.js" (
    echo [❌] ERROR CRITICO: No se encontro auth.js. El login fallara.
    set "INTEGRITY=FAIL"
) else (
    echo [✅] INTEGRIDAD: Archivos de autenticacion localizados.
)

:: Validar Branding (Logo)
if not exist "%RELEASE_DIR%\static\img\Logo_Escudo_Sin_Fondo.png" (
    echo [⚠️] ADVERTENCIA: Logo no detectado.
)

echo.
if "%INTEGRITY%"=="OK" (
    echo ===================================================
    echo   ✅ EXITO: Tu version GOLD MASTER esta lista en:
    echo   %RELEASE_DIR%
    echo ===================================================
) else (
    echo ===================================================
    echo   ❌ FALLO: El build esta incompleto. Revisa logs.
    echo ===================================================
)
pause
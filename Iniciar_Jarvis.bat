@echo off
title JARVIS v3.1 - Intelligent AI Assistant
color 0A

cd /d "%~dp0"

echo =====================================================
echo    JARVIS v3.1 - Intelligent AI Assistant
echo    Launcher Unificado de 1-Clic
echo =====================================================
echo.

if not exist "%~dp0venv\Scripts\python.exe" (
    echo [ERROR] Entorno virtual no encontrado en: %~dp0venv
    pause
    exit /b 1
)

if not exist "%~dp0.env" (
    echo [ERROR] No se encontro el archivo .env en: %~dp0
    pause
    exit /b 1
)

:: Comprobar si el servidor ya esta activo en el puerto 5001
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 5001 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"
if %errorlevel% equ 0 (
    echo [INFO] JARVIS ya esta en ejecucion. Abriendo interfaz...
    start http://localhost:5001
    ping 127.0.0.1 -n 2 >nul
    exit /b 0
)

echo [INFO] Iniciando servidor JARVIS...
start "JARVIS Server" /min "%~dp0venv\Scripts\python.exe" -m uvicorn api.server:app --host 0.0.0.0 --port 5001 --reload

echo [INFO] Abriendo interfaz en http://localhost:5001 ...
ping 127.0.0.1 -n 3 >nul
start http://localhost:5001

echo.
echo [INFO] JARVIS iniciado con exito.
ping 127.0.0.1 -n 2 >nul


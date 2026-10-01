@echo off
chcp 65001 >nul
title JARVIS v3.1 — Neural AI Assistant
color 0B

cd /d "%~dp0"

echo ----------------------------------------------------
echo    ⚡ JARVIS v3.1 — Neural AI Assistant
echo    [Liquid Glass Arc Reactor Edition]
echo ----------------------------------------------------
echo.

if not exist "%~dp0venv\Scripts\python.exe" (
    echo [ERROR] Entorno virtual no encontrado en: %~dp0venv
    pause
    exit /b 1
)

if not exist "%~dp0.env" (
    echo [ERROR] Archivo de configuracion .env no encontrado en: %~dp0
    pause
    exit /b 1
)

:: Comprobacion ultra rapida de puerto activo (40ms)
netstat -ano | findstr :5001 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo [OK] JARVIS ya esta en ejecucion en el puerto 5001.
    echo [OK] Abriendo interfaz en el navegador...
    start http://localhost:5001
    exit /b 0
)

echo [1/2] Iniciando servidor JARVIS en segundo plano...
start "JARVIS Server" /min "%~dp0venv\Scripts\python.exe" -m uvicorn api.server:app --host 0.0.0.0 --port 5001 --reload

echo [2/2] Esperando conexion en http://localhost:5001...
set /a attempts=0

:WAIT_PORT
set /a attempts+=1
netstat -ano | findstr :5001 | findstr LISTENING >nul
if %errorlevel% equ 0 goto READY
if %attempts% geq 40 goto TIMEOUT_PORT
:: Espera no bloqueante de ~100ms
ping -n 1 -w 100 192.0.2.1 >nul
goto WAIT_PORT

:READY
echo.
echo [OK] Servidor activo y en linea.
echo [OK] Desplegando interfaz de usuario...
start http://localhost:5001
echo.
echo [OK] JARVIS listo. Disfruta de la experiencia.
ping -n 1 -w 500 192.0.2.1 >nul
exit /b 0

:TIMEOUT_PORT
echo.
echo [AVISO] El servidor se esta iniciando. Abriendo navegador...
start http://localhost:5001
exit /b 0

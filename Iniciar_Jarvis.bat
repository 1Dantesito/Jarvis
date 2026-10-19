@echo off
chcp 65001 >nul
title JARVIS v4.0 — Neural AI Assistant
color 0B

cd /d "%~dp0"

echo ----------------------------------------------------
echo    ⚡ JARVIS v4.0 — Neural AI Assistant
echo    [Liquid Glass Arc Reactor Edition - Mobile-Ready]
echo ----------------------------------------------------
echo.

:: 1. Si no existe venv pero hay python en el sistema, crearlo automaticamente (para nuevas computadoras)
if not exist "%~dp0venv\Scripts\python.exe" (
    echo [CONFIGURACION INICIAL] Creando entorno virtual local...
    python -m venv "%~dp0venv" 2>nul || py -m venv "%~dp0venv" 2>nul
    if exist "%~dp0venv\Scripts\python.exe" (
        echo [OK] Instalando dependencias de JARVIS...
        "%~dp0venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
    ) else (
        echo [ERROR] No se encontro Python para crear el entorno virtual.
        echo Instala Python 3.10+ marcando "Add python.exe to PATH" desde: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

:: 2. Asegurar archivo .env
if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" (
        copy "%~dp0.env.example" "%~dp0.env" >nul
    )
)

:: 3. Detectar puerto desde .env si existe, o usar 5001 por defecto
set "JARVIS_PORT=5001"
if exist "%~dp0.env" (
    for /f "usebackq tokens=1,2 delims==" %%A in ("%~dp0.env") do (
        if /i "%%A"=="PORT" set "JARVIS_PORT=%%B"
    )
)

:: 4. Comprobacion rapida de puerto activo
netstat -ano | findstr /C:":%JARVIS_PORT% " | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo [OK] JARVIS ya esta en ejecucion en el puerto %JARVIS_PORT%.
    echo [OK] Abriendo interfaz en el navegador...
    start http://localhost:%JARVIS_PORT%
    exit /b 0
)

echo [1/2] Iniciando servidor JARVIS en segundo plano...
start "JARVIS Server" /min "%~dp0venv\Scripts\python.exe" -m uvicorn api.server:app --host 0.0.0.0 --port %JARVIS_PORT%

echo [2/2] Esperando conexion en http://localhost:%JARVIS_PORT%...
set /a attempts=0

:WAIT_PORT
set /a attempts+=1
netstat -ano | findstr /C:":%JARVIS_PORT% " | findstr LISTENING >nul
if %errorlevel% equ 0 goto READY
if %attempts% geq 35 goto TIMEOUT_PORT
powershell -NoProfile -Command "Start-Sleep -Milliseconds 250" >nul 2>&1 || ping -n 1 -w 250 127.0.0.1 >nul
goto WAIT_PORT

:READY
echo.
echo [OK] Servidor activo y en linea.
echo [OK] Desplegando interfaz de usuario...
start http://localhost:%JARVIS_PORT%
echo.
echo [OK] JARVIS listo. Disfruta de la experiencia.
powershell -NoProfile -Command "Start-Sleep -Milliseconds 500" >nul 2>&1
exit /b 0

:TIMEOUT_PORT
echo.
echo [AVISO] El servidor se esta iniciando. Abriendo navegador...
start http://localhost:%JARVIS_PORT%
exit /b 0

@echo off
chcp 65001 > nul
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0\.."

if not exist logs mkdir logs
set "LOG_FILE=%CD%\logs\autostart-servidor.log"

echo ==================================================>> "%LOG_FILE%"
echo [%DATE% %TIME%] Iniciando rotina de autostart...>> "%LOG_FILE%"

if not exist ".\venv\Scripts\python.exe" (
    echo [%DATE% %TIME%] ERRO: Python nao encontrado em .\venv\Scripts\python.exe>> "%LOG_FILE%"
    exit /b 1
)

:start_loop
set "LOCAL_IP=127.0.0.1"
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "169.254"') do (
    set "LOCAL_IP=%%a"
    goto :ip_found
)

:ip_found
set "LOCAL_IP=!LOCAL_IP: =!"

echo [%DATE% %TIME%] LOCAL_IP=!LOCAL_IP!>> "%LOG_FILE%"

set "DJANGO_SETTINGS_MODULE=config.settings.localnetwork"
set "ALLOWED_HOSTS=localhost,127.0.0.1,!LOCAL_IP!"

echo [%DATE% %TIME%] Rodando collectstatic...>> "%LOG_FILE%"
.\venv\Scripts\python.exe manage.py collectstatic --noinput --clear >> "%LOG_FILE%" 2>&1

echo [%DATE% %TIME%] Rodando migrate...>> "%LOG_FILE%"
.\venv\Scripts\python.exe manage.py migrate >> "%LOG_FILE%" 2>&1

echo [%DATE% %TIME%] Subindo servidor waitress em 0.0.0.0:8080...>> "%LOG_FILE%"
.\venv\Scripts\python.exe -m waitress --host=0.0.0.0 --port=8080 --threads=6 config.wsgi:application >> "%LOG_FILE%" 2>&1

set "EXIT_CODE=!ERRORLEVEL!"
echo [%DATE% %TIME%] Servidor encerrou com codigo !EXIT_CODE!. Reiniciando em 10s...>> "%LOG_FILE%"
timeout /t 10 /nobreak > nul
goto :start_loop

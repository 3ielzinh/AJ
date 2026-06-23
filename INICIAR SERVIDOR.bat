AJ — Servidor de Producao
=========================
Clique duplo para iniciar o servidor na rede local.

@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo ==========================================
echo   AJ — Iniciando servidor de producao...
echo ==========================================

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "169.254"') do (
    set LOCAL_IP=%%a
    goto :found
)
:found
set LOCAL_IP=%LOCAL_IP: =%

echo.
echo   Esta maquina : http://localhost:8080
echo   Rede local   : http://%LOCAL_IP%:8080
echo.
echo   Ctrl+C para encerrar
echo.

set DJANGO_SETTINGS_MODULE=config.settings.production
.\venv\Scripts\python.exe manage.py collectstatic --noinput --clear 2>nul
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe -m waitress --host=0.0.0.0 --port=8080 --threads=6 config.wsgi:application
pause

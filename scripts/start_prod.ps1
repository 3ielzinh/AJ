# Script de inicialização — Produção (Waitress)
# Uso: .\scripts\start_prod.ps1
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$env:DJANGO_SETTINGS_MODULE = "config.settings.production"

$python = Join-Path $root "venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python nao encontrado em $python."
}

# Detecta IP local para exibir endereço de rede
$LOCAL_IP = (
    Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.*" } |
    Select-Object -First 1
).IPAddress
if (-not $LOCAL_IP) { $LOCAL_IP = "127.0.0.1" }

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AJ — Servidor de producao (Waitress)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Esta maquina : http://localhost:8080" -ForegroundColor Green
Write-Host "  Rede local   : http://${LOCAL_IP}:8080" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Ctrl+C para encerrar" -ForegroundColor Gray
Write-Host ""

# Coleta arquivos estáticos e aplica migrações pendentes
& $python manage.py collectstatic --noinput
& $python manage.py migrate

# Inicia Waitress
& $python -m waitress `
    --host=0.0.0.0 `
    --port=8080 `
    --threads=6 `
    --url-scheme=http `
    config.wsgi:application

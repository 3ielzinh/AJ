# Script de inicialização — Desenvolvimento
# Uso: .\scripts\start_dev.ps1
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$env:DJANGO_SETTINGS_MODULE = "config.settings.development"

$python = Join-Path $root "venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python nao encontrado em $python. Crie o venv com: python -m venv venv"
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  AJ — Ambiente de desenvolvimento" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Acesso: http://localhost:8000" -ForegroundColor Green
Write-Host "  Ctrl+C para encerrar" -ForegroundColor Gray
Write-Host ""

& $python manage.py migrate --run-syncdb
& $python manage.py runserver 0.0.0.0:8000

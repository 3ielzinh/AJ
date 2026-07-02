param(
    [string]$TaskName = "AJ-Servidor-Autostart"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$startupScript = Join-Path $root "scripts\start_server_autostart.bat"

if (-not (Test-Path $startupScript)) {
    throw "Script de autostart nao encontrado: $startupScript"
}

$taskAction = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$startupScript`""
$taskTrigger = New-ScheduledTaskTrigger -AtLogOn
$taskSettings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1)

$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $taskAction `
    -Trigger $taskTrigger `
    -Settings $taskSettings `
    -Principal $principal `
    -Description "Inicializa o servidor AJ automaticamente no logon." `
    -Force | Out-Null

Write-Host "Tarefa '$TaskName' criada/atualizada com sucesso." -ForegroundColor Green
Write-Host "Log do servidor: $root\logs\autostart-servidor.log"
Write-Host "Para iniciar agora: Start-ScheduledTask -TaskName '$TaskName'"

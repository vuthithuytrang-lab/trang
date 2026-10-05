# Dang ky lich chay tu dong 08:00 va 20:00 hang ngay trong Task Scheduler
param([Parameter(Mandatory = $true)][string]$PythonExe)
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
$tenLich = 'Theo doi publish Techcombank'

# pythonw.exe chay ngam, khong bat cua so den len man hinh
$pyw = Join-Path (Split-Path $PythonExe) 'pythonw.exe'
if (-not (Test-Path $pyw)) { $pyw = $PythonExe }

$action = New-ScheduledTaskAction -Execute $pyw -Argument "`"$dir\theo_doi.py`"" -WorkingDirectory $dir
$triggers = @(
    (New-ScheduledTaskTrigger -Daily -At '08:00'),
    (New-ScheduledTaskTrigger -Daily -At '20:00')
)
# StartWhenAvailable = may tat dung gio thi bat len se chay bu
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 1) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $tenLich -Action $action -Trigger $triggers -Settings $settings `
    -Description 'Kiem tra ngay publish cac URL techcombank.com, ghi Google Sheet, gui bao cao' -Force | Out-Null

Write-Host "Da bat lich '$tenLich': 08:00 va 20:00 hang ngay (co chay bu khi may tat)."
if ((Get-TimeZone).BaseUtcOffset -ne (New-TimeSpan -Hours 7)) {
    Write-Host "CANH BAO: may dang khong de mui gio Viet Nam (UTC+7). Lich se chay theo gio cua may." -ForegroundColor Yellow
}

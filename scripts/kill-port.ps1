param(
    [int[]]$Ports = @(8001, 8002, 8101),
    [switch]$Admin
)

$Commands = @()
foreach ($Port in $Ports) {
    $Commands += @("interface portproxy delete v4tov4 listenport=$Port listenaddress=0.0.0.0")
}

if ($Admin) {
    # Build argument string
    $Args = ($Commands | ForEach-Object { "netsh $_" }) -join " & "
    Start-Process -Verb RunAs -Wait -FilePath powershell -ArgumentList "-NoProfile -Command `"$Args`""
    return
}

foreach ($Cmd in $Commands) {
    $port = if ($Cmd -match 'listenport=(\d+)') { $matches[1] } else { "?" }
    $result = netsh $Cmd 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Porta $port removida do portproxy" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Nao foi possivel remover portproxy na porta $port (necessita admin)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Use -Admin para tentar com elevacao:" -ForegroundColor Cyan
Write-Host "  .\scripts\kill-port.ps1 -Admin" -ForegroundColor Cyan

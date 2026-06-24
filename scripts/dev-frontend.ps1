param(
    [string]$Port = "8101",
    [string]$BindHost = "0.0.0.0"
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$FrontendDir = Join-Path $ProjectRoot "apps\frontend-webapp"

# Remove conflicting portproxy rule (tolerates non-admin)
netsh interface portproxy delete v4tov4 listenport=$Port listenaddress=0.0.0.0 2>$null

# Start HTTP server
Write-Host "Iniciando Frontend na porta $Port..."
Set-Location $FrontendDir
python -m http.server $Port --directory $FrontendDir --bind $BindHost

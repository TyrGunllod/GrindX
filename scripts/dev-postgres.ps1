param(
    [string]$Port = "8002",
    [string]$BindHost = "0.0.0.0"
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ApiDir = Join-Path $ProjectRoot "apps\api-postgres"
$VenvPython = Join-Path $ApiDir ".venv\Scripts\python.exe"
$PythonPath = Join-Path $ProjectRoot "packages"

# Remove conflicting portproxy rule (tolerates non-admin)
netsh interface portproxy delete v4tov4 listenport=$Port listenaddress=0.0.0.0 2>$null

# Start uvicorn
Write-Host "Iniciando API Postgres na porta $Port..."
$env:PYTHONPATH = $PythonPath
Set-Location $ApiDir
& $VenvPython -m uvicorn app.main:app --reload --host $BindHost --port $Port

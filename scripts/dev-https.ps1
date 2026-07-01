param(
    [string]$ApiPort = "8002",
    [string]$FrontPort = "443",
    [string]$BindHost = "0.0.0.0"
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$CertsDir = Join-Path $ProjectRoot ".certs"
$KeyFile = Join-Path $CertsDir "dev-key.pem"
$CertFile = Join-Path $CertsDir "dev-cert.pem"

if (-not (Test-Path $KeyFile) -or -not (Test-Path $CertFile)) {
    Write-Host "Certificados não encontrados. Execute:" -ForegroundColor Red
    Write-Host "mkcert -key-file $KeyFile -cert-file $CertFile localhost 127.0.0.1 ::1" -ForegroundColor Yellow
    exit 1
}

$env:PYTHONPATH = Join-Path $ProjectRoot "packages"
$SslArgs = "--ssl-keyfile=$KeyFile", "--ssl-certfile=$CertFile"

Write-Host "=== Iniciando API PostgreSQL (porta $ApiPort, HTTPS) ===" -ForegroundColor Cyan
$apiJob = Start-Job -ScriptBlock {
    param($dir, $port, $hostBind, $sslArgs, $pp)
    $env:PYTHONPATH = $pp
    Set-Location $dir
    uvicorn app.main:app --host $hostBind --port $port $sslArgs
} -ArgumentList (Join-Path $ProjectRoot "apps\api-postgres"), $ApiPort, $BindHost, $SslArgs, $env:PYTHONPATH

Write-Host "=== Iniciando Frontend (porta $FrontPort, HTTPS) ===" -ForegroundColor Cyan
$frontJob = Start-Job -ScriptBlock {
    param($dir, $port, $cert, $key)
    Set-Location $dir
    python -c @"
import http.server, ssl
httpd = http.server.HTTPServer(('0.0.0.0', $port), http.server.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile='$cert', keyfile='$key', server_side=True)
print(f'Servindo HTTPS em https://localhost:$port')
httpd.serve_forever()
"@
} -ArgumentList (Join-Path $ProjectRoot "apps\frontend-webapp"), $FrontPort, $CertFile, $KeyFile

Write-Host "=== Pronto! ===" -ForegroundColor Green
Write-Host "Frontend: https://localhost:$FrontPort" -ForegroundColor Green
Write-Host "API Docs: https://localhost:$ApiPort/v1/docs" -ForegroundColor Green
Write-Host "Pressione qualquer tecla para parar..." -ForegroundColor Gray

try {
    Read-Host
} finally {
    Write-Host "Parando servidores..." -ForegroundColor Yellow
    $apiJob | Stop-Job -PassThru | Remove-Job
    $frontJob | Stop-Job -PassThru | Remove-Job
    Write-Host "Servidores parados." -ForegroundColor Green
}

param(
    [int[]]$Ports = @(8001, 8002, 8101),
    [switch]$Remove,
    [switch]$Admin
)

$ErrorActionPreference = "Stop"

function Get-WslIp {
    $ip = wsl -- hostname -I 2>$null
    if (-not $ip) {
        # fallback: tenta obter via wsl exec
        $ip = wsl -d (wsl -l -q | Select-Object -First 1) -- ip addr show eth0 2>$null
        if ($ip -match 'inet\s+(\d+\.\d+\.\d+\.\d+)') {
            $ip = $Matches[1]
        }
    }
    return ($ip -split '\s+')[0]
}

function Get-WindowsIp {
    $ifaces = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
        $_.IPAddress -notmatch '^127\.' -and $_.InterfaceAlias -notmatch 'Loopback|Virtual|Bluetooth|Hyper-V'
    }
    return ($ifaces | Sort-Object PrefixOrigin -Descending | Select-Object -First 1).IPAddress
}

function Ensure-Admin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        if (-not $Admin) {
            Write-Host "[!] Necessario administrador para gerenciar portproxy e firewall." -ForegroundColor Yellow
            Write-Host "    Execute como Administrador ou use o parametro -Admin." -ForegroundColor Yellow
            return $false
        }
        $args = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
        if ($Remove) { $args += " -Remove" }
        $args += " -Admin"
        $psi = New-Object Diagnostics.ProcessStartInfo
        $psi.FileName = "powershell.exe"
        $psi.Arguments = $args
        $psi.Verb = "runas"
        try {
            [Diagnostics.Process]::Start($psi) | Out-Null
        } catch {
            Write-Host "[ERRO] Falha ao elevar: $_" -ForegroundColor Red
        }
        exit
    }
    return $true
}

$wslIp = Get-WslIp
if (-not $wslIp) {
    Write-Host "[ERRO] Nao foi possivel detectar o IP do WSL." -ForegroundColor Red
    Write-Host "Certifique-se de que o WSL esta rodando: wsl -- true" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] IP WSL2:   $wslIp" -ForegroundColor Cyan
$windowsIp = Get-WindowsIp
if ($windowsIp) {
    Write-Host "[OK] IP Windows: $windowsIp" -ForegroundColor Cyan
}

if ($Remove) {
    Write-Host "`nRemovendo regras de portproxy..." -ForegroundColor Yellow
    $ok = $true
    foreach ($port in $Ports) {
        $r = netsh interface portproxy delete v4tov4 listenport=$port listenaddress=0.0.0.0 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Porta $port removida" -ForegroundColor Green
        } else {
Write-Host "  [WARN] Porta ${port}: $r" -ForegroundColor Yellow
            $ok = $false
        }
    }
    if (-not $ok) {
        Write-Host "`nExecute como Administrador para remocao completa: .\scripts\external-access.ps1 -Remove -Admin" -ForegroundColor Yellow
    }
    exit
}

if (-not (Ensure-Admin)) { return }

Write-Host "`nConfigurando portproxy para acesso externo..." -ForegroundColor Green

$ok = $true
foreach ($port in $Ports) {
    $r = netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIp 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Porta $port -> $wslIp`:$port" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Porta ${port}: $r" -ForegroundColor Yellow
        $ok = $false
    }
}

Write-Host "`nConfigurando firewall (liberar portas de entrada)..." -ForegroundColor Green
$ruleName = "GrindX Dev External Access"
$existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
if (-not $existing) {
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort $Ports -Action Allow | Out-Null
    Write-Host "  [OK] Regra de firewall criada: $ruleName" -ForegroundColor Green
} else {
    Write-Host "  [OK] Regra de firewall ja existe" -ForegroundColor Green
}

Write-Host "`n=== Acesso externo configurado ===" -ForegroundColor Cyan
Write-Host "Acesse de qualquer dispositivo na rede pelo IP do Windows:" -ForegroundColor White
Write-Host "  http://$windowsIp`:8101  (Frontend)" -ForegroundColor Green
Write-Host "  http://$windowsIp`:8002  (API Postgres)" -ForegroundColor Green
Write-Host "  http://$windowsIp`:8001  (API SQL Server)" -ForegroundColor Green
Write-Host "`nPara remover as regras:" -ForegroundColor Yellow
Write-Host "  .\scripts\external-access.ps1 -Remove" -ForegroundColor Yellow

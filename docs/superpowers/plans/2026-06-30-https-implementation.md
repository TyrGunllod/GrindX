# HTTPS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable HTTPS in dev environment (Windows) using mkcert + uvicorn SSL flags, and in production (WSL/server) via nginx TLS termination.

**Architecture:** mkcert generates trusted local CA and certificates. Uvicorn serves APIs with `--ssl-keyfile`/`--ssl-certfile`. Frontend served via custom HTTPS server script (Python). Frontend dynamic protocol in config.js. Nginx handles TLS in production.

**Tech Stack:** mkcert, uvicorn, Python http.server + SSL, nginx

---

### Task 1: Install mkcert and generate dev certificates (Windows)

**Files:**
- Create: `.certs/dev-key.pem`
- Create: `.certs/dev-cert.pem`
- Create: `.certs/.gitignore`

- [ ] **Step 1: Create certs directory and gitignore**

```powershell
New-Item -ItemType Directory -Path ".certs" -Force
@"
*.pem
*.crt
*.key
"@ | Set-Content -Path ".certs\.gitignore"
```

- [ ] **Step 2: Install mkcert (Windows)**

```powershell
# Via Chocolatey
choco install mkcert

# Ou via winget
winget install mkcert

# Ou manual: baixar mkcert-v*-windows-amd64.exe de https://github.com/FiloSottile/mkcert/releases
# Renomear para mkcert.exe e colocar no PATH
```

- [ ] **Step 3: Create local CA and generate certificates**

```powershell
mkcert -install
mkcert -key-file .certs/dev-key.pem -cert-file .certs/dev-cert.pem localhost 127.0.0.1 ::1
```

Expected output: `Created a new certificate valid for the following names 📜`

- [ ] **Step 4: Commit**

```bash
git add .certs/.gitignore
git commit -m "chore: add certs directory with gitignore"
```

---

### Task 2: Update frontend config.js for dynamic protocol

**Files:**
- Modify: `apps/frontend-webapp/shared/config.js`

- [ ] **Step 1: Change protocol from hardcoded http to dynamic**

Find the line:
```javascript
API_BASE_URL: window.__GRINDX_API_URL || `http://${window.location.hostname}:8002/v1`
```

Change to:
```javascript
API_BASE_URL: window.__GRINDX_API_URL || `${window.location.protocol}//${window.location.hostname}:8002/v1`
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/shared/config.js
git commit -m "feat: use dynamic protocol for API URL in config.js"
```

---

### Task 3: Create dev-https.ps1 script (Windows)

**Files:**
- Create: `scripts/dev-https.ps1`

- [ ] **Step 1: Create the HTTPS dev script**

```powershell
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
    param($dir, $port, $certFile, $keyFile)
    Set-Location $dir
    python -c @"
import http.server, ssl, sys
httpd = http.server.HTTPServer(('0.0.0.0', $port), http.server.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile='$certFile', keyfile='$keyFile', server_side=True)
httpd.serve_forever()
"@
} -ArgumentList (Join-Path $ProjectRoot "apps\frontend-webapp"), $FrontPort, $CertFile, $KeyFile

Write-Host "=== Pronto! Acesse: https://localhost:$FrontPort ===" -ForegroundColor Green
Write-Host "API: https://localhost:$ApiPort/v1/docs" -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Gray

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    $apiJob | Stop-Job | Remove-Job
    $frontJob | Stop-Job | Remove-Job
}
```

- [ ] **Step 2: Commit**

```bash
git add scripts/dev-https.ps1
git commit -m "feat: add dev-https.ps1 script for local HTTPS development on Windows"
```

---

### Task 4: Update nginx.conf for production HTTPS

**Files:**
- Modify: `apps/frontend-webapp/nginx.conf`

- [ ] **Step 1: Add HTTPS server block**

Add SSL server block on port 443 and redirect HTTP (80) to HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name grindx.local;

    ssl_certificate     /etc/nginx/certs/dev-cert.pem;
    ssl_certificate_key /etc/nginx/certs/dev-key.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /v1/ {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name grindx.local;
    return 301 https://$server_name$request_uri;
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/nginx.conf
git commit -m "feat: add HTTPS server block and HTTP redirect to nginx.conf"
```

---

### Task 5: Update compose.yaml for HTTPS

**Files:**
- Modify: `compose.yaml`

- [ ] **Step 1: Add port 443 and cert volume**

Add `"443:443"` to frontend ports and cert volume:
```yaml
ports:
  - "8101:80"
  - "443:443"
volumes:
  - ./.certs:/etc/nginx/certs:ro
```

- [ ] **Step 2: Commit**

```bash
git add compose.yaml
git commit -m "feat: add port 443 and cert volume to compose"
```

---

### Task 6: Update CSP connect-src for HTTPS

**Files:**
- Modify: `apps/api-sqlserver/app/core/config.py`

- [ ] **Step 1: Add HTTPS origins to CSP**

Add `https://localhost:8002`, `https://127.0.0.1:8002` to the `csp_connect_srcs` property.

- [ ] **Step 2: Commit**

```bash
git add apps/api-sqlserver/app/core/config.py
git commit -m "fix: add HTTPS origins to CSP connect-src"
```

---

### Task 7: Verify and format

- [ ] **Step 1: Format**

```bash
ruff format apps/ packages/
ruff check --fix . && ruff check .
```

- [ ] **Step 2: Test HTTPS access**

```powershell
scripts/dev-https.ps1
# In another terminal:
curl -k https://localhost:8002/health
```

Expected: return 200

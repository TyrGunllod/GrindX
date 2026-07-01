#!/usr/bin/env bash
# dev-https.sh — Inicia API + Frontend com HTTPS (Linux)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CERT="$ROOT/.certs/dev-cert.pem"
KEY="$ROOT/.certs/dev-key.pem"

if [ ! -f "$KEY" ] || [ ! -f "$CERT" ]; then
    echo "Certificados não encontrados. Execute:"
    echo "  mkcert -key-file $KEY -cert-file $CERT localhost 127.0.0.1 ::1 <seus_ips>"
    exit 1
fi

SSL_OPTS="--ssl-keyfile=$KEY --ssl-certfile=$CERT"

VENV_POSTGRES="$ROOT/apps/api-postgres/.venv/bin/python"
VENV_SQLSERVER="$ROOT/apps/api-sqlserver/.venv/bin/python"

echo "=== API SQL Server (porta 8001, HTTPS) ==="
if [ -f "$VENV_SQLSERVER" ]; then
    cd "$ROOT/apps/api-sqlserver"
    PYTHONPATH="$ROOT/packages" "$VENV_SQLSERVER" -m uvicorn app.main:app --host 0.0.0.0 --port 8001 $SSL_OPTS &
    SQL_PID=$!
    cd "$ROOT"
else
    echo "  Virtualenv sqlserver não encontrado — pulando" >&2
fi

echo "=== API PostgreSQL (porta 8002, HTTPS) ==="
if [ ! -f "$VENV_POSTGRES" ]; then
    echo "Virtualenv postgres não encontrado em $VENV_POSTGRES" >&2
    exit 1
fi
cd "$ROOT/apps/api-postgres"
PYTHONPATH="$ROOT/packages" "$VENV_POSTGRES" -m uvicorn app.main:app --host 0.0.0.0 --port 8002 $SSL_OPTS &
PG_PID=$!
cd "$ROOT"

echo "=== Frontend (porta 8443, HTTPS) ==="
python3 "$ROOT/scripts/serve-https.py" 8443 &
FRONT_PID=$!

echo "=== Pronto! ==="
echo "Frontend:  https://localhost:8443"
echo "API PG:    https://localhost:8002/v1/docs"
echo "API SQL:   https://localhost:8001/health"
echo ""
echo "Pressione ENTER para parar..."
read -r

kill $PG_PID $SQL_PID $FRONT_PID 2>/dev/null
echo "Servidores parados."

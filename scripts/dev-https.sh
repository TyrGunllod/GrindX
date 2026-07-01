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

echo "=== API PostgreSQL (porta 8002, HTTPS) ==="
cd "$ROOT/apps/api-postgres"
PYTHONPATH="$ROOT/packages" uvicorn app.main:app --host 0.0.0.0 --port 8002 $SSL_OPTS &
API_PID=$!
cd "$ROOT"

echo "=== Frontend (porta 8443, HTTPS) ==="
python3 "$ROOT/scripts/serve-https.py" 8443 &
FRONT_PID=$!

echo "=== Pronto! ==="
echo "Frontend: https://localhost:8443"
echo "API:      https://localhost:8002/v1/docs"
echo ""
echo "Pressione ENTER para parar..."
read -r

kill $API_PID $FRONT_PID 2>/dev/null
echo "Servidores parados."

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

API_POSTGRES_CONFIG = PROJECT_ROOT / "apps/api-postgres/app/core/config.py"
API_SQLSERVER_CONFIG = PROJECT_ROOT / "apps/api-sqlserver/app/core/config.py"
FRONTEND_VERSION_JSON = PROJECT_ROOT / "apps/frontend-webapp/version.json"

content = API_POSTGRES_CONFIG.read_text(encoding="utf-8")
match = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', content)
version = match.group(1) if match else "0.0.0"

# Sincroniza version.json
FRONTEND_VERSION_JSON.write_text(
    json.dumps({"version": f"v{version}"}, indent=2) + "\n",
    encoding="utf-8",
)
print(f"version.json atualizado: v{version}")

# Sincroniza api-sqlserver/app/core/config.py
sqlserver_content = API_SQLSERVER_CONFIG.read_text(encoding="utf-8")
sqlserver_content = re.sub(
    r'(APP_VERSION\s*=\s*)"([^"]+)"',
    lambda m: f'{m.group(1)}"{version}"',
    sqlserver_content,
)
API_SQLSERVER_CONFIG.write_text(sqlserver_content, encoding="utf-8")
print(f"api-sqlserver/config.py atualizado: {version}")

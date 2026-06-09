import json
import re
from pathlib import Path

# Resolve a raiz do projeto: scripts/update_frontend_version.py → ../
PROJECT_ROOT = Path(__file__).resolve().parent.parent

API_POSTGRES_CONFIG = PROJECT_ROOT / "apps/api-postgres/app/core/config.py"
FRONTEND_VERSION_JSON = PROJECT_ROOT / "apps/frontend-webapp/version.json"

content = API_POSTGRES_CONFIG.read_text(encoding="utf-8")
match = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', content)
version = match.group(1) if match else "0.0.0"

FRONTEND_VERSION_JSON.write_text(
    json.dumps({"version": f"v{version}"}, indent=2) + "\n",
    encoding="utf-8",
)

print(f"version.json generated: v{version}")

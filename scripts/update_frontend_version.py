import json
import re
from pathlib import Path

API_POSTGRES_CONFIG = Path("packages/api-postgres/app/core/config.py")
FRONTEND_VERSION_JSON = Path("packages/frontend-webapp/version.json")

content = API_POSTGRES_CONFIG.read_text(encoding="utf-8")
match = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', content)
version = match.group(1) if match else "0.0.0"

FRONTEND_VERSION_JSON.write_text(
    json.dumps({"version": f"v{version}"}, indent=2) + "\n",
    encoding="utf-8",
)

print(f"version.json generated: v{version}")

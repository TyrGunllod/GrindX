"""Extract APP_VERSION from api-postgres config.py."""
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
config = root / "apps" / "api-postgres" / "app" / "core" / "config.py"
match = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', config.read_text())
print(match.group(1) if match else "0.0.0")

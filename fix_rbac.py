"""
Corrige o RBAC_GUIDE.py: move o # noqa: F821 para fora dos parênteses.
Execute na raiz do projeto GrindX:
    python fix_rbac.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
guide = ROOT / "packages/shared/RBAC_GUIDE.py"

text = guide.read_text(encoding="utf-8")

# Remove o noqa que ficou dentro dos parênteses (erro do script anterior)
text = re.sub(r'\(get_current_user\)  # noqa: F821\)', '(get_current_user))', text)

# Recoloca corretamente: após o ):  da assinatura da função
text = re.sub(r'(Depends\(get_current_user\)\)):', r'\1:  # noqa: F821', text)

guide.write_text(text, encoding="utf-8")
print("✅ RBAC_GUIDE.py corrigido")

import subprocess
result = subprocess.run(
    ["ruff", "check", "packages/", "--select", "E,F,I", "--ignore", "E501"],
    cwd=ROOT, capture_output=True, text=True,
)
if result.returncode == 0:
    print("✅ Nenhum erro restante! CI deve passar agora.")
else:
    print("⚠️  Erros restantes:\n")
    print(result.stdout)

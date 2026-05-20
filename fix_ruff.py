"""
Script para corrigir erros do ruff que não são auto-corrigíveis.
Execute na raiz do projeto GrindX:
    python fix_ruff.py
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent  # ajuste se necessário


# ─── 1. Auto-fix (imports, unused, f-string) ────────────────────────────────
print("▶ Rodando ruff --fix (52 correções automáticas)...")
subprocess.run(
    ["ruff", "check", "packages/", "--select", "E,F,I", "--ignore", "E501", "--fix"],
    cwd=ROOT,
)
print("✅ Auto-fix concluído.\n")


# ─── Helpers ─────────────────────────────────────────────────────────────────
def patch(path: str, old: str, new: str):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    if old not in text:
        print(f"  ⚠️  Trecho não encontrado em {path} — pulando")
        return
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"  ✅ {path}")


# ─── 2. E712 – comparação com True ──────────────────────────────────────────
print("▶ Corrigindo E712 (== True) em portal_router.py...")
patch(
    "packages/api-postgres/app/routers/portal_router.py",
    "Aba.ativo == True",
    "Aba.ativo",
)

# ─── 3. E701 – múltiplos statements numa linha ──────────────────────────────
print("\n▶ Corrigindo E701 (inline if/raise) em portal_router.py...")

patch(
    "packages/api-postgres/app/routers/portal_router.py",
    "    if not aba: raise HTTPException(404, \"Aba não encontrada\")\n    aba.nome = nome",
    "    if not aba:\n        raise HTTPException(404, \"Aba não encontrada\")\n    aba.nome = nome",
)
patch(
    "packages/api-postgres/app/routers/portal_router.py",
    "    if not aba: raise HTTPException(404, \"Aba não encontrada\")\n    db.delete(aba)",
    "    if not aba:\n        raise HTTPException(404, \"Aba não encontrada\")\n    db.delete(aba)",
)
patch(
    "packages/api-postgres/app/routers/portal_router.py",
    "    if not mod: raise HTTPException(404, \"Módulo não encontrado\")\n    mod.nome = nome",
    "    if not mod:\n        raise HTTPException(404, \"Módulo não encontrado\")\n    mod.nome = nome",
)
patch(
    "packages/api-postgres/app/routers/portal_router.py",
    "    if not mod: raise HTTPException(404, \"Módulo não encontrado\")\n    db.delete(mod)",
    "    if not mod:\n        raise HTTPException(404, \"Módulo não encontrado\")\n    db.delete(mod)",
)

# ─── 4. E402 – imports fora do topo (conftest.py) ────────────────────────────
# A causa é o bloco sys.path antes dos imports. A solução padrão é usar
# noqa: E402 nas linhas problemáticas, pois mover os imports quebraria o path.
print("\n▶ Corrigindo E402 em conftest.py (adicionando # noqa: E402)...")

for conf in [
    "packages/api-postgres/tests/conftest.py",
    "packages/api-sqlserver/tests/conftest.py",
]:
    p = ROOT / conf
    if not p.exists():
        print(f"  ⚠️  {conf} não encontrado — pulando")
        continue
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    new_lines = []
    for line in lines:
        stripped = line.rstrip("\n")
        if (
            stripped.startswith("from app.database import")
            or stripped.startswith("from app.main import")
        ) and "# noqa" not in stripped:
            line = stripped + "  # noqa: E402\n"
        new_lines.append(line)
    p.write_text("".join(new_lines), encoding="utf-8")
    print(f"  ✅ {conf}")

# ─── 5. RBAC_GUIDE.py – E402, F821, F841 ────────────────────────────────────
# Este arquivo é um GUIA/EXEMPLO, não código de produção.
# Adiciona noqa nas linhas de import tardio e nas referências a get_current_user.
print("\n▶ Corrigindo RBAC_GUIDE.py (E402 / F821 / F841 com # noqa)...")
guide = ROOT / "packages/shared/RBAC_GUIDE.py"
if guide.exists():
    text = guide.read_text(encoding="utf-8")

    # E402: imports tardios
    for imp in [
        "from shared.schemas.auth import TokenPayload",
        "from shared.security.permissions import get_user_roles_hierarchy",
    ]:
        text = text.replace(imp, imp + "  # noqa: E402", 1)

    # F821: get_current_user não definido no arquivo (é import do módulo real)
    text = re.sub(
        r"(Depends\(get_current_user\))",
        r"\1  # noqa: F821",
        text,
    )

    # F841: variáveis locais usadas apenas como exemplo comentado
    for var in ["roles_do_admin", "roles_do_operador", "roles_da_leitura"]:
        text = re.sub(
            rf"(\s+{var} = get_user_roles_hierarchy\([^)]+\))",
            r"\1  # noqa: F841",
            text,
        )

    guide.write_text(text, encoding="utf-8")
    print("  ✅ packages/shared/RBAC_GUIDE.py")
else:
    print("  ⚠️  RBAC_GUIDE.py não encontrado — pulando")

# ─── 6. Verificação final ────────────────────────────────────────────────────
print("\n▶ Verificação final...")
result = subprocess.run(
    ["ruff", "check", "packages/", "--select", "E,F,I", "--ignore", "E501"],
    cwd=ROOT,
    capture_output=True,
    text=True,
)
if result.returncode == 0:
    print("✅ Nenhum erro restante! CI deve passar agora.")
else:
    print("⚠️  Erros restantes:\n")
    print(result.stdout)

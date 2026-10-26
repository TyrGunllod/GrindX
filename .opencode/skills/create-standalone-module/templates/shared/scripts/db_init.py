"""
scripts/db_init.py — aplica database.sql no banco do modulo standalone.

O repositorio standalone nao tem `alembic.ini`, entao a migration so roda dentro
do GrindX. Fora dele, database.sql e o caminho padrao: idempotente, sem DROP.

Equivale a `psql "$DATABASE_URL" -f database.sql`, mas usa o driver Python que o
modulo ja tem, entao funciona sem o psql instalado.

Uso:
    python scripts/db_init.py [--dry-run]
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

RAIZ = Path(__file__).resolve().parent.parent
SQL_FILE = RAIZ / "database.sql"
MANIFEST = RAIZ / "module.json"


def _url_do_banco() -> str | None:
    load_dotenv(RAIZ / ".env")
    return (os.getenv("DATABASE_URL") or "").strip() or None


def _schema_e_tabelas() -> tuple[str, list[str]]:
    if not MANIFEST.exists():
        return "public", []
    dados = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return dados.get("schema_name", "public"), list(dados.get("tables", []))


def main() -> int:
    parser = argparse.ArgumentParser(description="Aplica database.sql no banco do modulo")
    parser.add_argument("--dry-run", action="store_true", help="Apenas exibe o que seria feito")
    args = parser.parse_args()

    if not SQL_FILE.exists():
        print(f"Arquivo nao encontrado: {SQL_FILE}", file=sys.stderr)
        return 2

    url = _url_do_banco()
    if not url:
        print(
            "DATABASE_URL nao definida. Copie .env.example para .env e aponte para o "
            "PostgreSQL do modulo.",
            file=sys.stderr,
        )
        return 2
    if url.startswith("sqlite"):
        print(
            "database.sql e PostgreSQL; no SQLite os testes criam as tabelas sozinhos "
            "(create_all no conftest).",
            file=sys.stderr,
        )
        return 2

    schema, tabelas = _schema_e_tabelas()
    sql = SQL_FILE.read_text(encoding="utf-8")
    if args.dry_run:
        print(f"[DRY-RUN] Aplicaria {SQL_FILE.name} em {url} ({len(sql.splitlines())} linhas)")
        return 0

    engine = create_engine(url)
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql(sql)
        existentes = set(inspect(engine).get_table_names(schema=schema))
    except Exception as erro:  # noqa: BLE001 - queremos a mensagem do driver, nao o traceback
        print(f"Falha ao aplicar {SQL_FILE.name}: {erro}", file=sys.stderr)
        return 1

    faltando = [t for t in tabelas if t not in existentes]
    if faltando:
        print(f"Tabelas ausentes apos aplicar o SQL: {', '.join(faltando)}", file=sys.stderr)
        return 1

    print(f"Schema {schema} pronto: {', '.join(tabelas) or '(nenhuma tabela no manifest)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

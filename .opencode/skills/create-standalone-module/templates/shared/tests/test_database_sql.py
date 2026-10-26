"""Contrato do database.sql — o preparo do banco no standalone.

Se este arquivo falhar, o módulo "passa nos testes" e quebra no `make db-init` do
usuário: o SQL deixou de acompanhar o modelo (ou o contrário).
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from app.modules.{module_name}.base import PortalBase
import app.modules.{module_name}.models  # noqa: F401  (registra as tabelas no metadata)

RAIZ = Path(__file__).resolve().parents[4]
MANIFEST = json.loads((RAIZ / "module.json").read_text(encoding="utf-8"))
SCHEMA = MANIFEST["schema_name"]


def ler_sql() -> str:
    return (RAIZ / "database.sql").read_text(encoding="utf-8")


def colunas_do_sql(sql: str) -> dict[str, set[str]]:
    blocos = re.findall(
        rf"CREATE TABLE IF NOT EXISTS {SCHEMA}\.(\w+) \((.*?)\n\);", sql, re.DOTALL
    )
    return {
        tabela: {
            linha.split()[0]
            for linha in bloco.splitlines()
            if linha.strip() and not linha.strip().startswith(("CONSTRAINT", "--"))
        }
        for tabela, bloco in blocos
    }


class TestDatabaseSql:
    def test_cria_o_schema(self):
        assert f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};" in ler_sql()

    def test_cria_todas_as_tabelas_do_manifesto(self):
        sql = ler_sql()

        for tabela in MANIFEST["tables"]:
            assert f"CREATE TABLE IF NOT EXISTS {SCHEMA}.{tabela} (" in sql

    def test_e_idempotente_e_nunca_derruba_dados(self):
        sql = ler_sql().upper()

        assert "CREATE TABLE IF NOT EXISTS" in sql
        assert "CREATE INDEX IF NOT EXISTS" in sql
        assert "DROP" not in sql
        assert "TRUNCATE" not in sql

    def test_colunas_batem_com_os_modelos(self):
        colunas_sql = colunas_do_sql(ler_sql())
        tabelas = {t.name: t for t in PortalBase.metadata.tables.values()}

        assert set(colunas_sql) == set(tabelas)
        for nome, tabela in tabelas.items():
            assert colunas_sql[nome] == set(tabela.columns.keys()), nome

    def test_db_init_recusa_sqlite(self):
        resultado = subprocess.run(
            [sys.executable, "scripts/db_init.py"],
            cwd=RAIZ,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "DATABASE_URL": "sqlite:///:memory:"},
        )

        assert resultado.returncode == 2
        assert "PostgreSQL" in resultado.stderr

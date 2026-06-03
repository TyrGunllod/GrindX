"""
Validação do schema translate map.

Garante que _SCHEMA_TRANSLATE em conftest.py cobre todos os schemas
PostgreSQL usados pela aplicação (iam, portal, catalogo, org).
"""

from tests.conftest import _SCHEMA_TRANSLATE

# Schemas que a aplicação usa no PostgreSQL
EXPECTED_SCHEMAS = {"iam", "portal", "catalogo", "org"}


def test_schema_translate_covers_all_schemas():
    """Verifica que _SCHEMA_TRANSLATE mapeia todos os schemas PostgreSQL."""
    mapped_schemas = set(_SCHEMA_TRANSLATE.keys())

    for schema in EXPECTED_SCHEMAS:
        assert schema in mapped_schemas, (
            f"Schema '{schema}' não está em _SCHEMA_TRANSLATE. "
            f"Adicione '{schema}: None' ao dicionário em conftest.py."
        )


def test_schema_translate_maps_to_none_for_sqlite():
    """Verifica que todos os schemas mapeiam para None (SQLite compatível)."""
    for schema, target in _SCHEMA_TRANSLATE.items():
        assert target is None, (
            f"Schema '{schema}' mapeia para '{target}' em vez de None. "
            f"Para testes com SQLite, todos os schemas devem mapear para None."
        )


def test_expected_schemas_match_application_models():
    """Verifica que EXPECTED_SCHEMAS contém exatamente 4 schemas."""
    assert len(EXPECTED_SCHEMAS) == 4, (
        "Número inesperado de schemas. "
        "Atualize EXPECTED_SCHEMAS se novos schemas foram adicionados."
    )

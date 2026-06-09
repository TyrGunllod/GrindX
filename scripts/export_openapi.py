"""
Script para exportar a especificação OpenAPI da API.

Uso:
    python scripts/export_openapi.py

Gera:
    - docs/openapi.json — Especificação OpenAPI completa
    - docs/openapi.yaml — Versão YAML (opcional)
"""

import json
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar a app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


def export_openapi(output_dir: str = "docs") -> None:
    """Exporta a especificação OpenAPI da aplicação."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Obtém a especificação OpenAPI
    spec = app.openapi()

    # Salva em JSON
    json_path = output_path / "openapi.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print(f"✓ OpenAPI JSON exportado: {json_path}")

    # Estatísticas
    paths_count = len(spec.get("paths", {}))
    schemas_count = len(spec.get("components", {}).get("schemas", {}))
    print(f"  {paths_count} endpoints documentados")
    print(f"  {schemas_count} schemas definidos")


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "docs"
    export_openapi(output_dir)

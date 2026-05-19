"""
Fixtures globais para testes do projeto GrindX.

Fornece configuração compartilhada para testes que rodam
a partir da raiz do monorepo.
"""

import sys
from pathlib import Path

import pytest

# Adiciona packages ao sys.path para importar módulos compartilhados
_packages_dir = str(Path(__file__).resolve().parent.parent / "packages")
if _packages_dir not in sys.path:
    sys.path.insert(0, _packages_dir)


@pytest.fixture
def packages_dir():
    """Retorna o caminho absoluto do diretório packages."""
    return Path(_packages_dir)


@pytest.fixture
def shared_dir(packages_dir):
    """Retorna o caminho do diretório shared."""
    return packages_dir / "shared"

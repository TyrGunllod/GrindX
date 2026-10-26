"""Contrato da raiz do standalone — `/` abre a primeira aba, nao a listagem de pastas.

O `make dev-frontend` serve a raiz do modulo com `python -m http.server 7080`. Sem um
`index.html` na raiz, entrar em `http://localhost:7080/` mostra os diretorios
(`frontend/`, `shared/`, `app/`...) em vez do modulo.
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
MANIFEST = json.loads((RAIZ / "module.json").read_text(encoding="utf-8"))


def caminho_da_aba(aba: dict) -> str:
    """`modules/x/index.html` (GrindX) -> `frontend/x/index.html` (standalone)."""
    return aba["url"].replace("modules/", "frontend/", 1)


def ler_raiz() -> str:
    return (RAIZ / "index.html").read_text(encoding="utf-8")


class TestRaizDoStandalone:
    def test_existe_index_na_raiz(self):
        assert (RAIZ / "index.html").is_file()

    def test_redireciona_para_a_primeira_aba_do_manifesto(self):
        abas = MANIFEST["frontend_tabs"]
        primeira = min(abas, key=lambda aba: aba["order"])

        assert caminho_da_aba(primeira) in ler_raiz()

    def test_redireciona_sem_depender_de_js(self):
        html = ler_raiz()

        assert 'http-equiv="refresh"' in html
        # a raiz nao carrega os scripts das abas, so o CSS base
        assert "/shared/config.js" not in html
        assert "/shared/app.js" not in html

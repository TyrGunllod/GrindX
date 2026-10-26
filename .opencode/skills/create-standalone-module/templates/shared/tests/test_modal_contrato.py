"""Contrato dos modais — fecham só no Cancelar ou depois de salvar.

O botão de fechar (X) do cabeçalho, o `Escape` e o clique no overlay descartam o
formulário preenchido sem aviso. O padrão é: cabeçalho só com o título, rodapé com
`Cancelar` e `Salvar`, e o modal só some no cancelar ou quando o envio dá certo.
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
TELAS = sorted((RAIZ / "frontend").glob("*/index.html"))
ABERTURA_MODAL = '<div class="modal-overlay"'


def blocos_de_modal(html: str) -> list[str]:
    """De `<div class="modal-overlay"` até o `<footer>`, para checar os atributos."""
    blocos = []
    for trecho in html.split(ABERTURA_MODAL)[1:]:
        corte = trecho.find('<footer class="modal-footer')
        blocos.append(trecho if corte == -1 else trecho[:corte])
    return blocos


class TestModais:
    def test_existe_aba_com_modal(self):
        assert TELAS, "nenhuma aba em frontend/*/index.html"

    def test_modais_tem_aria(self):
        for tela in TELAS:
            for bloco in blocos_de_modal(tela.read_text(encoding="utf-8")):
                assert 'role="dialog"' in bloco, tela
                assert 'aria-modal="true"' in bloco, tela
                assert "aria-labelledby" in bloco, tela

    def test_nenhum_modal_tem_botao_de_fechar(self):
        for tela in TELAS:
            html = tela.read_text(encoding="utf-8")
            quantos = html.count(ABERTURA_MODAL)

            assert 'aria-label="Fechar"' not in html, tela
            assert "&times;" not in html, tela
            assert "close-modal" not in html, tela
            # `data-fechar` fica só no Cancelar: no máximo um por modal
            assert html.count("data-fechar=") <= quantos, tela

    def test_rodape_tem_cancelar_e_salvar(self):
        for tela in TELAS:
            html = tela.read_text(encoding="utf-8")
            quantos = html.count(ABERTURA_MODAL)

            assert html.count(">Cancelar</button>") >= quantos, tela
            assert html.count(">Salvar</button>") >= quantos, tela

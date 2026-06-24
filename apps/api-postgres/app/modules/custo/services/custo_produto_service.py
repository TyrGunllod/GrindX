import structlog
from app.modules.custo.exceptions import NenhumProdutoNoIntervalo, ProdutoNaoEncontrado
from app.modules.custo.repositories.custo_produto_repository import CustoProdutoRepository
from app.modules.custo.schemas.custo_produto import CustoProdutoResponse, CustoProdutoRangeResponse, ComponenteCusto

logger = structlog.get_logger(__name__)


class CustoProdutoService:
    def __init__(self, repository: CustoProdutoRepository) -> None:
        self.repository = repository

    def calcular_range(self, inicial: str, final: str) -> CustoProdutoRangeResponse:
        inicial = inicial.strip().upper()
        final = final.strip().upper()
        produtos_raw = self.repository.buscar_produtos_no_intervalo(inicial, final)
        if not produtos_raw:
            raise NenhumProdutoNoIntervalo(inicial, final)

        resultados: list[CustoProdutoResponse] = []
        for p in produtos_raw:
            try:
                resultados.append(self.calcular(p["B1_COD"]))
            except Exception:
                continue

        logger.info("Range calculado", inicial=inicial, final=final, total=len(resultados))
        return CustoProdutoRangeResponse(produtos=resultados, total_produtos=len(resultados))

    def calcular(self, codigo: str) -> CustoProdutoResponse:
        codigo = codigo.strip().upper()
        produto = self.repository.buscar_produto(codigo)
        if not produto:
            raise ProdutoNaoEncontrado(codigo)

        componentes_raw = self.repository.buscar_estrutura(codigo)
        componentes: list[ComponenteCusto] = []
        total = 0.0

        for comp in componentes_raw:
            cod_comp = comp["G1_COMP"].strip()
            qtd = float(comp["G1_QUANT"] or 0)
            custo = self.repository.buscar_custo_standard(cod_comp)
            total_comp = round(custo * qtd, 2)

            componentes.append(ComponenteCusto(
                codigo=cod_comp,
                descricao=comp.get("B1_DESC", "").strip() or "N/A",
                quantidade=qtd,
                custo_standard=custo,
                custo_total=total_comp,
            ))
            total += total_comp

        if not componentes:
            custo_produto = self.repository.buscar_custo_standard(codigo)
            total = custo_produto

        logger.info("Custo calculado", codigo=codigo, total=round(total, 2), componentes=len(componentes))
        return CustoProdutoResponse(
            codigo=codigo,
            descricao=produto["B1_DESC"].strip(),
            custo_total=round(total, 2),
            componentes=componentes,
        )

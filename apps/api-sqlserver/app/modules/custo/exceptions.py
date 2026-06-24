class ProdutoNaoEncontrado(Exception):
    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        super().__init__(f"Produto {codigo} não encontrado")


class NenhumProdutoNoIntervalo(Exception):
    def __init__(self, inicial: str, final: str) -> None:
        self.inicial = inicial
        self.final = final
        super().__init__(f"Nenhum produto encontrado no intervalo {inicial}-{final}")

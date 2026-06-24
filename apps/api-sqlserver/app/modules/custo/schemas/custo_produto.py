from pydantic import BaseModel, ConfigDict


class ComponenteCusto(BaseModel):
    codigo: str
    descricao: str
    quantidade: float
    custo_standard: float
    custo_total: float

    model_config = ConfigDict(from_attributes=True)


class CustoProdutoResponse(BaseModel):
    codigo: str
    descricao: str
    custo_total: float
    componentes: list[ComponenteCusto] = []

    model_config = ConfigDict(from_attributes=True)


class CustoProdutoRangeResponse(BaseModel):
    produtos: list[CustoProdutoResponse]
    total_produtos: int

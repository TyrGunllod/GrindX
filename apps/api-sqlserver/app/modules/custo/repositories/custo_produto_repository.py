from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional


class CustoProdutoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_produtos_no_intervalo(self, inicial: str, final: str) -> list[dict]:
        query = text("""
            SELECT B1_COD, B1_DESC
            FROM SB1010
            WHERE B1_COD BETWEEN :inicial AND :final AND D_E_L_E_T_ = ''
            ORDER BY B1_COD
        """)
        return [
            dict(r)
            for r in self.db.execute(query, {"inicial": inicial, "final": final})
            .mappings()
            .all()
        ]

    def buscar_produto(self, codigo: str) -> Optional[dict]:
        query = text("""
            SELECT B1_COD, B1_DESC
            FROM SB1010
            WHERE B1_COD = :code AND D_E_L_E_T_ = ''
        """)
        result = self.db.execute(query, {"code": codigo}).mappings().first()
        return dict(result) if result else None

    def buscar_estrutura(self, codigo: str) -> list[dict]:
        query = text("""
            SELECT G1_COMP, G1_QUANT, B1_DESC
            FROM SG1010 SG1
            INNER JOIN SB1010 SB1 ON SB1.B1_COD = SG1.G1_COMP AND SB1.D_E_L_E_T_ = ''
            WHERE G1_COD = :code AND SG1.D_E_L_E_T_ = ''
            ORDER BY G1_COMP
        """)
        return [
            dict(r) for r in self.db.execute(query, {"code": codigo}).mappings().all()
        ]

    def buscar_custo_standard(self, codigo: str) -> float:
        query = text("""
            SELECT B1_CUSTD
            FROM SB1010
            WHERE B1_COD = :code AND D_E_L_E_T_ = ''
        """)
        result = self.db.execute(query, {"code": codigo}).scalar()
        return float(result) if result is not None else 0.0

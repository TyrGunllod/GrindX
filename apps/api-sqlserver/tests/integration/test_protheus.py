"""Testes para o router de consulta de produtos Protheus."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


@pytest.mark.integration
class TestPorCodigo:
    def test_por_codigo_retorna_itens(self, client: TestClient, db_session: Session):
        db_session.execute(
            text("""
            CREATE TABLE SB1010 (
                B1_COD VARCHAR(20),
                B1_DESC VARCHAR(100),
                D_E_L_E_T_ VARCHAR(1),
                B1_MSBLQL VARCHAR(1)
            )
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_, B1_MSBLQL)
            VALUES ('ABCD01', 'Produto Teste', '', '2')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_, B1_MSBLQL)
            VALUES ('ABCD02', 'Outro Produto', '', '2')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_, B1_MSBLQL)
            VALUES ('ABCD03', 'Produto Deletado', '*', '2')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_, B1_MSBLQL)
            VALUES ('ABCD04', 'Produto Ativo', ' ', '2')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_, B1_MSBLQL)
            VALUES ('ABCD05', 'Produto Bloqueado', '', '1')
        """)
        )
        db_session.commit()

        resp = client.get("/v1/produtos/por-codigo?codigo=ABCD")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        assert data[0]["codigo"] == "ABCD01"
        assert data[0]["descricao"] == "Produto Teste"

    def test_por_codigo_minimo_4_caracteres(self, client: TestClient):
        resp = client.get("/v1/produtos/por-codigo?codigo=AB")
        assert resp.status_code == 422

    def test_por_codigo_sem_resultados(self, client: TestClient, db_session: Session):
        db_session.execute(
            text("""
            CREATE TABLE SB1010 (
                B1_COD VARCHAR(20),
                B1_DESC VARCHAR(100),
                D_E_L_E_T_ VARCHAR(1),
                B1_MSBLQL VARCHAR(1)
            )
        """)
        )
        db_session.commit()
        resp = client.get("/v1/produtos/por-codigo?codigo=ZZZZ")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.integration
class TestPorDescricao:
    def test_por_descricao_retorna_itens(self, client: TestClient, db_session: Session):
        db_session.execute(
            text("""
            CREATE TABLE SB1010 (
                B1_COD VARCHAR(20),
                B1_DESC VARCHAR(100),
                D_E_L_E_T_ VARCHAR(1),
                B1_MSBLQL VARCHAR(1)
            )
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_, B1_MSBLQL)
            VALUES ('001', 'Produto Teste Um', '', '2')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_, B1_MSBLQL)
            VALUES ('002', 'Produto Teste Dois', '', '2')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_, B1_MSBLQL)
            VALUES ('003', 'Outro Item', '', '2')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_, B1_MSBLQL)
            VALUES ('004', 'Produto Deletado', '*', '2')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_, B1_MSBLQL)
            VALUES ('005', 'Produto Ativo', ' ', '2')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_, B1_MSBLQL)
            VALUES ('006', 'Produto Bloqueado', '', '1')
        """)
        )
        db_session.commit()

        resp = client.get("/v1/produtos/por-descricao?descricao=Produto")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    def test_por_descricao_minimo_4_caracteres(self, client: TestClient):
        resp = client.get("/v1/produtos/por-descricao?descricao=AB")
        assert resp.status_code == 422

    def test_por_descricao_sem_resultados(
        self, client: TestClient, db_session: Session
    ):
        db_session.execute(
            text("""
            CREATE TABLE SB1010 (
                B1_COD VARCHAR(20),
                B1_DESC VARCHAR(100),
                D_E_L_E_T_ VARCHAR(1),
                B1_MSBLQL VARCHAR(1)
            )
        """)
        )
        db_session.commit()
        resp = client.get("/v1/produtos/por-descricao?descricao=ZZZZ")
        assert resp.status_code == 200
        assert resp.json() == []

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
                D_E_L_E_T_ VARCHAR(1)
            )
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_)
            VALUES ('ABCD01', 'Produto Teste', '')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_)
            VALUES ('ABCD02', 'Outro Produto', '')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_)
            VALUES ('ABCD03', 'Produto Deletado', '*')
        """)
        )
        db_session.commit()

        resp = client.get("/v1/produtos/por-codigo?codigo=ABCD")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
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
                D_E_L_E_T_ VARCHAR(1)
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
                D_E_L_E_T_ VARCHAR(1)
            )
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_)
            VALUES ('001', 'Produto Teste Um', '')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_)
            VALUES ('002', 'Produto Teste Dois', '')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_)
            VALUES ('003', 'Outro Item', '')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1010 (B1_COD, B1_DESC, D_E_L_E_T_)
            VALUES ('004', 'Produto Deletado', '*')
        """)
        )
        db_session.commit()

        resp = client.get("/v1/produtos/por-descricao?descricao=Produto")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

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
                D_E_L_E_T_ VARCHAR(1)
            )
        """)
        )
        db_session.commit()
        resp = client.get("/v1/produtos/por-descricao?descricao=ZZZZ")
        assert resp.status_code == 200
        assert resp.json() == []

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
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('ABCD01', 'Produto Teste')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('ABCD02', 'Outro Produto')
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
        assert "4" in resp.text or "mínimo" in resp.text.lower()

    def test_por_codigo_sem_resultados(self, client: TestClient, db_session: Session):
        db_session.execute(
            text("""
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """)
        )
        db_session.commit()
        resp = client.get("/v1/produtos/por-codigo?codigo=ZZZZ")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.integration
class TestPorDescricao:
    def test_por_descricao_modo_inicio(self, client: TestClient, db_session: Session):
        db_session.execute(
            text("""
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('001', 'Produto Teste Um')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('002', 'Produto Teste Dois')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('003', 'Outro Item')
        """)
        )
        db_session.commit()

        resp = client.get("/v1/produtos/por-descricao?descricao=Produto&modo=inicio")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    def test_por_descricao_modo_exato(self, client: TestClient, db_session: Session):
        db_session.execute(
            text("""
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('001', 'Produto Teste')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('002', 'Produto Teste Completo')
        """)
        )
        db_session.commit()

        resp = client.get(
            "/v1/produtos/por-descricao?descricao=Produto Teste&modo=exato"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["codigo"] == "001"

    def test_por_descricao_modo_trecho(self, client: TestClient, db_session: Session):
        db_session.execute(
            text("""
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('001', 'Este é um Produto Teste')
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('002', 'Outro Item Qualquer')
        """)
        )
        db_session.commit()

        resp = client.get("/v1/produtos/por-descricao?descricao=Produto&modo=trecho")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1

    def test_por_descricao_minimo_4_caracteres(self, client: TestClient):
        resp = client.get("/v1/produtos/por-descricao?descricao=AB&modo=inicio")
        assert resp.status_code == 422

    def test_por_descricao_modo_invalido(self, client: TestClient):
        resp = client.get("/v1/produtos/por-descricao?descricao=ABCD&modo=xpto")
        assert resp.status_code == 422

    def test_por_descricao_padrao_modo_inicio(
        self, client: TestClient, db_session: Session
    ):
        db_session.execute(
            text("""
            CREATE TABLE SB1 (B1_COD VARCHAR(20), B1_DESC VARCHAR(100))
        """)
        )
        db_session.execute(
            text("""
            INSERT INTO SB1 (B1_COD, B1_DESC) VALUES ('001', 'Produto Inicio')
        """)
        )
        db_session.commit()

        resp = client.get("/v1/produtos/por-descricao?descricao=Produto")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1

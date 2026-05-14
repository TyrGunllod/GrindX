"""Testes de integração dos endpoints de Cliente via TestClient."""


class TestClienteRouter:

    def test_listar_clientes_sem_dados(self, client, auth_headers):
        response = client.get("/v1/cadastro/clientes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] == 0
        assert data["items"] == []

    def test_buscar_cliente_inexistente_retorna_404(self, client, auth_headers):
        response = client.get("/v1/cadastro/clientes/9999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["error"] == "CLIENTE_NAO_ENCONTRADO"

    def test_buscar_por_cnpj_inexistente_retorna_404(self, client, auth_headers):
        response = client.get(
            "/v1/cadastro/clientes/cnpj/00.000.000/0000-00",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_listar_clientes_com_dados(self, client, auth_headers, db_session):
        from app.models.cliente import Cliente

        cliente = Cliente(
            id=1,
            razao_social="Empresa Teste Ltda",
            cnpj="12.345.678/0001-90",
            ativo=True,
        )
        db_session.add(cliente)
        db_session.commit()

        response = client.get("/v1/cadastro/clientes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["razao_social"] == "Empresa Teste Ltda"

    def test_buscar_cliente_por_id(self, client, auth_headers, db_session):
        from app.models.cliente import Cliente

        cliente = Cliente(
            id=42,
            razao_social="Empresa XYZ",
            cnpj="98.765.432/0001-10",
            ativo=True,
        )
        db_session.add(cliente)
        db_session.commit()

        response = client.get("/v1/cadastro/clientes/42", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["cnpj"] == "98.765.432/0001-10"

    def test_rota_sem_token_retorna_erro(self, client):
        response = client.get("/v1/cadastro/clientes")
        assert response.status_code == 401

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")

    def test_filtro_por_uf(self, client, auth_headers, db_session):
        from app.models.cliente import Cliente

        db_session.add(Cliente(id=1, razao_social="SP Ltda", cnpj="11.111.111/0001-11", uf="SP", ativo=True))
        db_session.add(Cliente(id=2, razao_social="RJ Ltda", cnpj="22.222.222/0001-22", uf="RJ", ativo=True))
        db_session.commit()

        response = client.get("/v1/cadastro/clientes?uf=SP", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["uf"] == "SP"

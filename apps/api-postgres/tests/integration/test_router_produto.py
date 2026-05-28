"""Testes de integração dos endpoints de Produto via TestClient."""


class TestProdutoRouter:
    def test_criar_produto(self, client, auth_headers):
        response = client.post(
            "/v1/produto/produtos",
            json={"nome": "Caneta", "preco": 2.50},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == "Caneta"
        assert data["id"] is not None

    def test_buscar_produto_por_id(self, client, auth_headers):
        criar = client.post(
            "/v1/produto/produtos",
            json={"nome": "Lápis", "preco": 1.00},
            headers=auth_headers,
        )
        produto_id = criar.json()["id"]
        response = client.get(
            f"/v1/produto/produtos/{produto_id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Lápis"

    def test_buscar_produto_inexistente_retorna_404(self, client, auth_headers):
        response = client.get("/v1/produto/produtos/9999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["error"] == "PRODUTO_NAO_ENCONTRADO"

    def test_listar_produtos(self, client, auth_headers):
        client.post(
            "/v1/produto/produtos",
            json={"nome": "Prod1", "preco": 5.00},
            headers=auth_headers,
        )
        response = client.get("/v1/produto/produtos", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1

    def test_atualizar_produto(self, client, auth_headers):
        criar = client.post(
            "/v1/produto/produtos",
            json={"nome": "Original", "preco": 10.00},
            headers=auth_headers,
        )
        produto_id = criar.json()["id"]
        response = client.put(
            f"/v1/produto/produtos/{produto_id}",
            json={"nome": "Atualizado"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Atualizado"

    def test_desativar_produto(self, client, auth_headers):
        criar = client.post(
            "/v1/produto/produtos",
            json={"nome": "Para Desativar", "preco": 5.00},
            headers=auth_headers,
        )
        produto_id = criar.json()["id"]
        response = client.delete(
            f"/v1/produto/produtos/{produto_id}", headers=auth_headers
        )
        assert response.status_code == 200

    def test_rota_sem_token_retorna_erro(self, client):
        response = client.get("/v1/produto/produtos")
        assert response.status_code == 401

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")

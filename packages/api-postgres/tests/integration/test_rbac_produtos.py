"""
Testes de integração para RBAC nas rotas de Produto.

Testa que cada endpoint respeita as permissões por role:
- GET: leitura, operador, admin
- POST: operador, admin
- PUT: operador, admin
- DELETE: admin
"""

from decimal import Decimal

import pytest
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from fastapi.testclient import TestClient
from shared.security.jwt import gerar_hash_senha


@pytest.fixture
def usuario_admin(db_session) -> tuple[Usuario, str]:
    """Cria usuário admin e retorna (usuario, password)."""
    repo = UsuarioRepository(db_session)
    usuario = Usuario(
        username="admin_user",
        email="admin@example.com",
        nome_completo="Admin User",
        senha_hash=gerar_hash_senha("senha_admin"),
        role="admin",
    )
    usuario_criado = repo.criar(usuario)
    return usuario_criado, "senha_admin"


@pytest.fixture
def usuario_operador(db_session) -> tuple[Usuario, str]:
    """Cria usuário operador e retorna (usuario, password)."""
    repo = UsuarioRepository(db_session)
    usuario = Usuario(
        username="operador_user",
        email="operador@example.com",
        nome_completo="Operador User",
        senha_hash=gerar_hash_senha("senha_operador"),
        role="operador",
    )
    usuario_criado = repo.criar(usuario)
    return usuario_criado, "senha_operador"


@pytest.fixture
def usuario_leitura(db_session) -> tuple[Usuario, str]:
    """Cria usuário leitura e retorna (usuario, password)."""
    repo = UsuarioRepository(db_session)
    usuario = Usuario(
        username="leitura_user",
        email="leitura@example.com",
        nome_completo="Leitura User",
        senha_hash=gerar_hash_senha("senha_leitura"),
        role="leitura",
    )
    usuario_criado = repo.criar(usuario)
    return usuario_criado, "senha_leitura"


@pytest.fixture
def token_admin(client: TestClient, usuario_admin: tuple):
    """Retorna token JWT para usuário admin."""
    _, password = usuario_admin
    response = client.post(
        "/v1/auth/token",
        json={"username": "admin_user", "password": password},
    )
    return response.json()["access_token"]


@pytest.fixture
def token_operador(client: TestClient, usuario_operador: tuple):
    """Retorna token JWT para usuário operador."""
    _, password = usuario_operador
    response = client.post(
        "/v1/auth/token",
        json={"username": "operador_user", "password": password},
    )
    return response.json()["access_token"]


@pytest.fixture
def token_leitura(client: TestClient, usuario_leitura: tuple):
    """Retorna token JWT para usuário leitura."""
    _, password = usuario_leitura
    response = client.post(
        "/v1/auth/token",
        json={"username": "leitura_user", "password": password},
    )
    return response.json()["access_token"]


@pytest.fixture
def produto_teste(db_session):
    """Cria um produto de teste."""
    produto = Produto(
        nome="Caneta Azul",
        descricao="Caneta esferográfica azul",
        preco=Decimal("2.50"),
        ativo=True,
    )
    db_session.add(produto)
    db_session.commit()
    return produto


class TestGetProdutosRbac:
    """Testes do endpoint GET /v1/estoque/produtos com RBAC."""

    def test_admin_consegue_listar_produtos(self, client: TestClient, token_admin: str):
        """Testa que admin consegue listar produtos."""
        response = client.get(
            "/v1/estoque/produtos",
            headers={"Authorization": f"Bearer {token_admin}"},
        )

        assert response.status_code == 200
        assert "items" in response.json()

    def test_operador_consegue_listar_produtos(
        self, client: TestClient, token_operador: str
    ):
        """Testa que operador consegue listar produtos."""
        response = client.get(
            "/v1/estoque/produtos",
            headers={"Authorization": f"Bearer {token_operador}"},
        )

        assert response.status_code == 200

    def test_leitura_consegue_listar_produtos(
        self, client: TestClient, token_leitura: str
    ):
        """Testa que leitura consegue listar produtos."""
        response = client.get(
            "/v1/estoque/produtos",
            headers={"Authorization": f"Bearer {token_leitura}"},
        )

        assert response.status_code == 200

    def test_sem_autenticacao_nao_consegue_listar(self, client: TestClient):
        """Testa que sem autenticação não consegue listar."""
        response = client.get("/v1/estoque/produtos")

        assert response.status_code == 401


class TestGetProdutoIdRbac:
    """Testes do endpoint GET /v1/estoque/produtos/{id} com RBAC."""

    def test_admin_consegue_buscar_produto(
        self, client: TestClient, token_admin: str, produto_teste: Produto
    ):
        """Testa que admin consegue buscar produto específico."""
        response = client.get(
            f"/v1/estoque/produtos/{produto_teste.id}",
            headers={"Authorization": f"Bearer {token_admin}"},
        )

        assert response.status_code == 200
        assert response.json()["nome"] == "Caneta Azul"

    def test_operador_consegue_buscar_produto(
        self, client: TestClient, token_operador: str, produto_teste: Produto
    ):
        """Testa que operador consegue buscar produto específico."""
        response = client.get(
            f"/v1/estoque/produtos/{produto_teste.id}",
            headers={"Authorization": f"Bearer {token_operador}"},
        )

        assert response.status_code == 200

    def test_leitura_consegue_buscar_produto(
        self, client: TestClient, token_leitura: str, produto_teste: Produto
    ):
        """Testa que leitura consegue buscar produto específico."""
        response = client.get(
            f"/v1/estoque/produtos/{produto_teste.id}",
            headers={"Authorization": f"Bearer {token_leitura}"},
        )

        assert response.status_code == 200


class TestPostProdutosRbac:
    """Testes do endpoint POST /v1/estoque/produtos com RBAC."""

    def test_admin_consegue_criar_produto(self, client: TestClient, token_admin: str):
        """Testa que admin consegue criar produto."""
        response = client.post(
            "/v1/estoque/produtos",
            headers={"Authorization": f"Bearer {token_admin}"},
            json={
                "nome": "Caneta Vermelha",
                "preco": 3.50,
                "ativo": True,
            },
        )

        assert response.status_code == 201
        assert response.json()["nome"] == "Caneta Vermelha"

    def test_operador_consegue_criar_produto(
        self, client: TestClient, token_operador: str
    ):
        """Testa que operador consegue criar produto."""
        response = client.post(
            "/v1/estoque/produtos",
            headers={"Authorization": f"Bearer {token_operador}"},
            json={
                "nome": "Caneta Verde",
                "preco": 3.50,
                "ativo": True,
            },
        )

        assert response.status_code == 201

    def test_leitura_nao_consegue_criar_produto(
        self, client: TestClient, token_leitura: str
    ):
        """Testa que leitura NÃO consegue criar produto (403)."""
        response = client.post(
            "/v1/estoque/produtos",
            headers={"Authorization": f"Bearer {token_leitura}"},
            json={
                "nome": "Caneta Preta",
                "preco": 3.50,
                "ativo": True,
            },
        )

        assert response.status_code == 403
        assert response.json()["error"] == "ACESSO_NEGADO"

    def test_sem_autenticacao_nao_consegue_criar(self, client: TestClient):
        """Testa que sem autenticação não consegue criar."""
        response = client.post(
            "/v1/estoque/produtos",
            json={
                "nome": "Caneta Amarela",
                "preco": 3.50,
                "ativo": True,
            },
        )

        assert response.status_code == 401


class TestPutProdutosRbac:
    """Testes do endpoint PUT /v1/estoque/produtos/{id} com RBAC."""

    def test_admin_consegue_atualizar_produto(
        self, client: TestClient, token_admin: str, produto_teste: Produto
    ):
        """Testa que admin consegue atualizar produto."""
        response = client.put(
            f"/v1/estoque/produtos/{produto_teste.id}",
            headers={"Authorization": f"Bearer {token_admin}"},
            json={"nome": "Caneta Azul Premium", "preco": 4.50},
        )

        assert response.status_code == 200
        assert response.json()["nome"] == "Caneta Azul Premium"

    def test_operador_consegue_atualizar_produto(
        self, client: TestClient, token_operador: str, produto_teste: Produto
    ):
        """Testa que operador consegue atualizar produto."""
        response = client.put(
            f"/v1/estoque/produtos/{produto_teste.id}",
            headers={"Authorization": f"Bearer {token_operador}"},
            json={"preco": 5.00},
        )

        assert response.status_code == 200

    def test_leitura_nao_consegue_atualizar_produto(
        self, client: TestClient, token_leitura: str, produto_teste: Produto
    ):
        """Testa que leitura NÃO consegue atualizar produto (403)."""
        response = client.put(
            f"/v1/estoque/produtos/{produto_teste.id}",
            headers={"Authorization": f"Bearer {token_leitura}"},
            json={"nome": "Caneta Nova"},
        )

        assert response.status_code == 403

    def test_sem_autenticacao_nao_consegue_atualizar(
        self, client: TestClient, produto_teste: Produto
    ):
        """Testa que sem autenticação não consegue atualizar."""
        response = client.put(
            f"/v1/estoque/produtos/{produto_teste.id}",
            json={"nome": "Caneta Nova"},
        )

        assert response.status_code == 401


class TestDeleteProdutosRbac:
    """Testes do endpoint DELETE /v1/estoque/produtos/{id} com RBAC."""

    def test_admin_consegue_desativar_produto(
        self, client: TestClient, token_admin: str, produto_teste: Produto
    ):
        """Testa que admin consegue desativar produto."""
        response = client.delete(
            f"/v1/estoque/produtos/{produto_teste.id}",
            headers={"Authorization": f"Bearer {token_admin}"},
        )

        assert response.status_code == 200
        assert "desativado" in response.json()["message"].lower()

    def test_operador_nao_consegue_desativar_produto(
        self, client: TestClient, token_operador: str, produto_teste: Produto
    ):
        """Testa que operador NÃO consegue desativar produto (403)."""
        response = client.delete(
            f"/v1/estoque/produtos/{produto_teste.id}",
            headers={"Authorization": f"Bearer {token_operador}"},
        )

        assert response.status_code == 403
        assert response.json()["error"] == "ACESSO_NEGADO"

    def test_leitura_nao_consegue_desativar_produto(
        self, client: TestClient, token_leitura: str, produto_teste: Produto
    ):
        """Testa que leitura NÃO consegue desativar produto (403)."""
        response = client.delete(
            f"/v1/estoque/produtos/{produto_teste.id}",
            headers={"Authorization": f"Bearer {token_leitura}"},
        )

        assert response.status_code == 403

    def test_sem_autenticacao_nao_consegue_desativar(
        self, client: TestClient, produto_teste: Produto
    ):
        """Testa que sem autenticação não consegue desativar."""
        response = client.delete(
            f"/v1/estoque/produtos/{produto_teste.id}",
        )

        assert response.status_code == 401


class TestRbacMatrizCompleta:
    """Testa matriz completa de permissões (CRUD x Roles)."""

    def test_matriz_permissoes_completa(
        self,
        client: TestClient,
        token_admin: str,
        token_operador: str,
        token_leitura: str,
        produto_teste: Produto,
    ):
        """Testa matriz completa: GET/POST/PUT/DELETE x admin/operador/leitura."""
        # Matriz esperada:
        # GET:    admin (200), operador (200), leitura (200)
        # POST:   admin (201), operador (201), leitura (403)
        # PUT:    admin (200), operador (200), leitura (403)
        # DELETE: admin (200), operador (403), leitura (403)

        url_lista = "/v1/estoque/produtos"
        url_item = f"/v1/estoque/produtos/{produto_teste.id}"

        # GET — todos conseguem
        for token in [token_admin, token_operador, token_leitura]:
            response = client.get(
                url_lista, headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200, f"GET falhou para token {token[:10]}..."

        # POST — admin e operador conseguem, leitura não
        for token, esperado in [
            (token_admin, 201),
            (token_operador, 201),
            (token_leitura, 403),
        ]:
            response = client.post(
                url_lista,
                headers={"Authorization": f"Bearer {token}"},
                json={"nome": "Novo Produto", "preco": 1.00},
            )
            assert response.status_code == esperado, (
                f"POST retornou {response.status_code}, esperava {esperado}"
            )

        # PUT — admin e operador conseguem, leitura não
        for token, esperado in [
            (token_admin, 200),
            (token_operador, 200),
            (token_leitura, 403),
        ]:
            response = client.put(
                url_item,
                headers={"Authorization": f"Bearer {token}"},
                json={"preco": 5.00},
            )
            assert response.status_code == esperado, (
                f"PUT retornou {response.status_code}, esperava {esperado}"
            )

        # DELETE — somente admin consegue
        for token, esperado in [
            (token_admin, 200),
            (token_operador, 403),
            (token_leitura, 403),
        ]:
            response = client.delete(
                url_item,
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == esperado, (
                f"DELETE retornou {response.status_code}, esperava {esperado}"
            )

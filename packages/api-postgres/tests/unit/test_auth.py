"""Testes unitários do módulo de autenticação (JWT e bcrypt)."""

from datetime import timedelta

import pytest
from shared.exceptions.base import TokenExpiradoError, TokenInvalidoError
from shared.security.jwt import (
    criar_jwt,
    gerar_hash_senha,
    verificar_jwt,
    verificar_senha,
)

_TEST_SECRET = "test-secret-key-for-unit-tests-only"


class TestJWT:
    """Testes para criação e verificação de tokens JWT."""

    def test_criar_e_verificar_token(self):
        payload = {"sub": "42", "role": "admin"}
        token = criar_jwt(payload, _TEST_SECRET, timedelta(minutes=30))

        resultado = verificar_jwt(token, _TEST_SECRET)

        assert resultado.sub == "42"
        assert resultado.role == "admin"

    def test_token_expirado(self):
        payload = {"sub": "1", "role": "leitura"}
        token = criar_jwt(payload, _TEST_SECRET, timedelta(seconds=-1))

        with pytest.raises(TokenExpiradoError):
            verificar_jwt(token, _TEST_SECRET)

    def test_token_invalido(self):
        with pytest.raises(TokenInvalidoError):
            verificar_jwt("token.invalido.aqui", _TEST_SECRET)

    def test_token_com_secret_errada(self):
        payload = {"sub": "1", "role": "admin"}
        token = criar_jwt(payload, _TEST_SECRET, timedelta(minutes=30))

        with pytest.raises(TokenInvalidoError):
            verificar_jwt(token, "chave-errada")


class TestSenha:
    """Testes para hashing e verificação de senha com bcrypt."""

    def test_gerar_e_verificar_hash(self):
        senha = "minha_senha_segura"
        hash_senha = gerar_hash_senha(senha)

        assert verificar_senha(senha, hash_senha)

    def test_senha_incorreta(self):
        hash_senha = gerar_hash_senha("senha_correta")

        assert not verificar_senha("senha_errada", hash_senha)

    def test_hash_diferente_a_cada_chamada(self):
        senha = "mesma_senha"
        hash1 = gerar_hash_senha(senha)
        hash2 = gerar_hash_senha(senha)

        assert hash1 != hash2  # bcrypt gera salt aleatório
        assert verificar_senha(senha, hash1)
        assert verificar_senha(senha, hash2)

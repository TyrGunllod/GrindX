"""
Testes de contrato entre api-postgres e api-sqlserver.

Garante que tokens JWT emitidos pela api-postgres podem ser
validados pela api-sqlserver, e vice-versa.
"""

from datetime import timedelta

from shared.security.jwt import criar_jwt, verificar_jwt


class TestContratoJWT:
    """Validacao de tokens JWT entre as APIs."""

    SECRET_KEY = "l13fqQV90pr45erksgVcp3p3Srr0qfP8r0v74bF3iyg="

    def test_token_com_payload_minimo_e_valido(self):
        """Token com payload basico e valido em qualquer API."""
        token = criar_jwt(
            payload={"sub": "1", "role": "admin"},
            secret_key=self.SECRET_KEY,
            expira_em=timedelta(minutes=30),
        )
        payload = verificar_jwt(token, self.SECRET_KEY)
        assert payload.sub == "1"
        assert payload.role == "admin"

    def test_token_com_company_id_e_valido(self):
        """Token com company_id usado nas duas APIs."""
        token = criar_jwt(
            payload={"sub": "42", "role": "operador", "company_id": 1},
            secret_key=self.SECRET_KEY,
            expira_em=timedelta(minutes=30),
        )
        payload = verificar_jwt(token, self.SECRET_KEY)
        assert payload.sub == "42"
        assert payload.role == "operador"
        assert payload.company_id == 1

    def test_token_rejeitado_com_chave_diferente(self):
        """Token com chave diferente nao deve validar."""
        token = criar_jwt(
            payload={"sub": "1", "role": "admin"},
            secret_key="outra-chave-32-caracteres-nao-valida",
            expira_em=timedelta(minutes=30),
        )
        from shared.exceptions.base import TokenInvalidoError

        try:
            verificar_jwt(token, self.SECRET_KEY)
            assert False, "Deveria ter lancado TokenInvalidoError"
        except TokenInvalidoError:
            pass

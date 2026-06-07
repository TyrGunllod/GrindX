"""
Testes de integração para o endpoint de health check.

Cobre cenários de saúde (healthy) e degradação (degraded)
quando o banco de dados está indisponível ou com schema incompleto.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.integration
class TestHealthCheckHealthy:
    """Testes para cenário de saúde normal (DB conectado)."""

    def test_health_returns_200_when_db_reachable(
        self, client: TestClient, db_session: Session
    ):
        """GET /health retorna 200 quando o banco está acessível."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_status_healthy_when_db_reachable(
        self, client: TestClient, db_session: Session
    ):
        """GET /health retorna status 'healthy' quando o banco está acessível."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_database_dict_with_postgres_key(
        self, client: TestClient, db_session: Session
    ):
        """GET /health retorna dict 'database' com chave 'postgres'."""
        response = client.get("/health")
        data = response.json()
        assert "database" in data
        assert isinstance(data["database"], dict)
        assert "postgres" in data["database"]
        assert data["database"]["postgres"] == "connected"

    def test_health_includes_service_name(
        self, client: TestClient, db_session: Session
    ):
        """GET /health inclui nome do serviço na resposta."""
        response = client.get("/health")
        data = response.json()
        assert data["service"] is not None
        assert len(data["service"]) > 0

    def test_health_includes_version(
        self, client: TestClient, db_session: Session
    ):
        """GET /health inclui versão do serviço na resposta."""
        response = client.get("/health")
        data = response.json()
        assert data["version"] is not None
        assert len(data["version"]) > 0

    def test_health_includes_timestamp(
        self, client: TestClient, db_session: Session
    ):
        """GET /health inclui timestamp na resposta."""
        response = client.get("/health")
        data = response.json()
        assert "timestamp" in data
        assert data["timestamp"] is not None

    def test_health_details_none_when_healthy(
        self, client: TestClient, db_session: Session
    ):
        """GET /health retorna details=None quando saudável."""
        response = client.get("/health")
        data = response.json()
        assert data.get("details") is None


@pytest.mark.integration
class TestHealthCheckDegraded:
    """Testes para cenário de degradação (DB indisponível)."""

    def test_health_returns_503_on_db_failure(self, client: TestClient):
        """GET /health retorna 503 quando falha na conexão com o banco."""
        from unittest.mock import patch

        with patch(
            "sqlalchemy.orm.Session.execute",
            side_effect=Exception("Connection refused"),
        ):
            response = client.get("/health")
            assert response.status_code == 503

    def test_health_status_degraded_on_db_failure(self, client: TestClient):
        """GET /health retorna status 'degraded' quando falha no banco."""
        from unittest.mock import patch

        with patch(
            "sqlalchemy.orm.Session.execute",
            side_effect=Exception("Connection refused"),
        ):
            response = client.get("/health")
            data = response.json()
            assert data["status"] == "degraded"

    def test_health_database_dict_disconnected_on_failure(self, client: TestClient):
        """GET /health retorna database dict com 'disconnected' quando falha."""
        from unittest.mock import patch

        with patch(
            "sqlalchemy.orm.Session.execute",
            side_effect=Exception("Connection refused"),
        ):
            response = client.get("/health")
            data = response.json()
            assert "database" in data
            assert isinstance(data["database"], dict)
            assert "postgres" in data["database"]
            assert data["database"]["postgres"] == "disconnected"

    def test_health_details_contains_error_on_failure(self, client: TestClient):
        """GET /health retorna details com erro quando falha no banco."""
        from unittest.mock import patch

        with patch(
            "sqlalchemy.orm.Session.execute",
            side_effect=Exception("Connection refused"),
        ):
            response = client.get("/health")
            data = response.json()
            assert data["details"] is not None
            assert "error" in data["details"]

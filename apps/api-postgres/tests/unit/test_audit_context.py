"""Testes unitários para o contexto de auditoria da requisição."""
from fastapi.testclient import TestClient

from app.audit.context import audit_ip, audit_user_id


def test_context_defaults_are_none():
    assert audit_user_id.get() is None
    assert audit_ip.get() is None


def test_context_cleared_after_request(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert audit_user_id.get() is None
    assert audit_ip.get() is None
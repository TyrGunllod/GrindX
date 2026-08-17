"""Testes de integração para a API de auditoria e sessões."""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.audit.context import audit_ip, audit_user_id
from app.audit.models import Sessao
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha


def _criar_usuario(db: Session, username: str, role: str = "admin") -> Usuario:
    u = Usuario(
        username=username,
        email=f"{username}@x.com",
        nome_completo=username,
        senha_hash=gerar_hash_senha("senha123"),
        role=role,
    )
    db.add(u)
    db.commit()
    return u


def _token(client: TestClient, username: str) -> dict[str, str]:
    resp = client.post(
        "/v1/auth/token",
        json={"username": username, "password": "senha123"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_login_abre_sessao_e_logout_fecha(client: TestClient, db_session: Session):
    u = _criar_usuario(db_session, "aud")
    headers = _token(client, "aud")

    sessoes = db_session.query(Sessao).filter(Sessao.user_id == u.id).all()
    assert len(sessoes) == 1
    assert sessoes[0].logout_at is None

    resp = client.post("/v1/auth/logout", headers=headers)
    assert resp.status_code == 200
    db_session.refresh(sessoes[0])
    assert sessoes[0].logout_at is not None
    assert sessoes[0].logout_motivo == "logout"


def test_audit_logs_requer_admin(client: TestClient, db_session: Session):
    _criar_usuario(db_session, "leitura", role="leitura")
    headers = _token(client, "leitura")
    resp = client.get("/v1/audit/logs", headers=headers)
    assert resp.status_code == 403


def test_audit_sessoes_requer_admin(client: TestClient, db_session: Session):
    _criar_usuario(db_session, "leitura2", role="leitura")
    headers = _token(client, "leitura2")
    resp = client.get("/v1/audit/sessoes", headers=headers)
    assert resp.status_code == 403


def test_audit_logs_lista_para_admin(client: TestClient, db_session: Session):
    _criar_usuario(db_session, "admin1")
    headers = _token(client, "admin1")

    audit_user_id.set(1)
    audit_ip.set("127.0.0.1")
    try:
        _criar_usuario(db_session, "outro")
    finally:
        audit_user_id.set(None)
        audit_ip.set(None)

    resp = client.get("/v1/audit/logs", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert data["items"][0]["entidade"] == "Usuario"
"""Testes de integração para a API de auditoria e sessões."""

from fastapi.testclient import TestClient
from shared.security.jwt import gerar_hash_senha
from sqlalchemy.orm import Session

from app.audit.context import audit_ip, audit_user_id
from app.audit.models import Sessao
from app.models.usuario import Usuario


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
    admin = _criar_usuario(db_session, "admin1")
    headers = _token(client, "admin1")

    audit_user_id.set(admin.id)
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
    assert data["items"][0]["user_id"] == admin.id
    assert data["items"][0]["usuario_username"] == "admin1"


def test_audit_sessoes_inclui_username(client: TestClient, db_session: Session):
    u = _criar_usuario(db_session, "sess1")
    headers = _token(client, "sess1")

    resp = client.get("/v1/audit/sessoes", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    item = next(i for i in data["items"] if i["user_id"] == u.id)
    assert item["usuario_username"] == "sess1"


def test_sessoes_persistem_entre_requisicoes():
    """Login/logout devem commitar a sessao (visivel em nova conexao).

    Simula producao: cada requisicao usa uma conexao/transacao propria.
    Sem commit, a sessao aberta no login nao aparece para outra conexao.
    """
    import uuid

    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.database import get_db
    from app.main import app
    from app.modules.iam.base import IamBase

    _translate = {"iam": None, "portal": None, "catalogo": None, "org": None}
    engine = create_engine(
        f"sqlite:///file:audit_persist_{uuid.uuid4().hex}?mode=memory&cache=shared&uri=true",
        connect_args={"check_same_thread": False},
    )
    with engine.execution_options(schema_translate_map=_translate).connect() as conn:
        IamBase.metadata.create_all(conn)

    Factory = sessionmaker(
        bind=engine.execution_options(schema_translate_map=_translate)
    )

    def _override_get_db():
        s = Factory()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(app)
    try:
        sess_a = Factory()
        u = Usuario(
            username="persist",
            email="persist@x.com",
            nome_completo="Persist",
            senha_hash=gerar_hash_senha("senha123"),
            role="admin",
        )
        sess_a.add(u)
        sess_a.commit()
        user_id = u.id
        sess_a.close()

        resp = client.post(
            "/v1/auth/token",
            json={"username": "persist", "password": "senha123"},
        )
        assert resp.status_code == 200, resp.text
        token = resp.json()["access_token"]

        sess_b = Factory()
        try:
            sessoes = sess_b.query(Sessao).filter(Sessao.user_id == user_id).all()
            assert len(sessoes) == 1, "login deve commitar a sessao aberta"
            assert sessoes[0].logout_at is None

            sess_b.rollback()
            resp_logout = client.post(
                "/v1/auth/logout",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp_logout.status_code == 200, resp_logout.text

            sessao = sess_b.query(Sessao).filter(Sessao.user_id == user_id).first()
            assert sessao is not None
            assert sessao.logout_at is not None, "logout deve commitar o fechamento"
            assert sessao.duracao_segundos is not None
        finally:
            sess_b.close()
    finally:
        app.dependency_overrides.clear()
        with engine.execution_options(
            schema_translate_map=_translate
        ).connect() as conn:
            IamBase.metadata.drop_all(conn)
        engine.dispose()

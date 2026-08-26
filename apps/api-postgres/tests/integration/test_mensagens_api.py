"""Testes de integração da API de mensagens."""

import os
import uuid

from fastapi.testclient import TestClient
from shared.security.jwt import gerar_hash_senha
from sqlalchemy.orm import Session

from app.mensagens.models import Mensagem
from app.models.usuario import Usuario


def _criar_usuario(db: Session, username: str, role: str = "operador") -> Usuario:
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


def test_fluxo_completo_mensagem_thread_e_lida(
    client: TestClient, db_session: Session
):
    a = _criar_usuario(db_session, "msg_a")
    b = _criar_usuario(db_session, "msg_b")
    h_a = _token(client, "msg_a")
    h_b = _token(client, "msg_b")

    # count inicial = 0
    resp = client.get("/v1/mensagens/nao-lidas/count", headers=h_a)
    assert resp.status_code == 200
    assert resp.json()["count"] == 0

    # A envia para B
    resp = client.post(
        "/v1/mensagens",
        headers=h_a,
        json={
            "destinatario_id": b.id,
            "titulo": "Pedido aprovado",
            "texto": "Seu pedido #88 foi aprovado.",
            "url_acao": "modules/home/index.html",
        },
    )
    assert resp.status_code == 200, resp.text
    raiz = resp.json()
    assert raiz["remetente_id"] == a.id
    assert raiz["categoria"] == "DIRETA"
    assert raiz["remetente_nome"] == "msg_a"

    # count de B = 1
    resp = client.get("/v1/mensagens/nao-lidas/count", headers=h_b)
    assert resp.json()["count"] == 1

    # B responde
    resp = client.post(
        f"/v1/mensagens/{raiz['id']}/respostas",
        headers=h_b,
        json={"texto": "Obrigado!"},
    )
    assert resp.status_code == 200, resp.text
    resposta = resp.json()
    assert resposta["resposta_a_id"] == raiz["id"]
    assert resposta["destinatario_id"] == a.id

    # thread de B lista raiz + resposta
    resp = client.get(f"/v1/mensagens/{raiz['id']}/thread", headers=h_b)
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    # B marca thread como lida -> count de B volta a 0 (só a raiz era de B)
    resp = client.patch(f"/v1/mensagens/{raiz['id']}/thread/lida", headers=h_b)
    assert resp.status_code == 200
    assert resp.json()["count"] == 1

    resp = client.get("/v1/mensagens/nao-lidas/count", headers=h_b)
    assert resp.json()["count"] == 0


def test_sistema_aviso_requer_admin(client: TestClient, db_session: Session):
    comum = _criar_usuario(db_session, "msg_comum")
    alvo = _criar_usuario(db_session, "msg_alvo")
    h = _token(client, "msg_comum")

    resp = client.post(
        "/v1/mensagens",
        headers=h,
        json={
            "destinatario_id": alvo.id,
            "titulo": "Aviso",
            "texto": "Mensagem",
            "categoria": "AVISO",
        },
    )
    assert resp.status_code == 403, resp.text


def test_apenas_destinatario_marca_lida(client: TestClient, db_session: Session):
    a = _criar_usuario(db_session, "msg_a2")
    b = _criar_usuario(db_session, "msg_b2")
    c = _criar_usuario(db_session, "msg_c2")
    h_a = _token(client, "msg_a2")
    h_c = _token(client, "msg_c2")

    resp = client.post(
        "/v1/mensagens",
        headers=h_a,
        json={"destinatario_id": b.id, "titulo": "X", "texto": "Y"},
    )
    msg_id = resp.json()["id"]

    resp = client.patch(f"/v1/mensagens/{msg_id}/lida", headers=h_c)
    assert resp.status_code == 403, resp.text


def test_arquivar_restaura_via_body(client: TestClient, db_session: Session):
    a = _criar_usuario(db_session, "msg_a4")
    b = _criar_usuario(db_session, "msg_b4")
    h_a = _token(client, "msg_a4")
    h_b = _token(client, "msg_b4")

    resp = client.post(
        "/v1/mensagens",
        headers=h_a,
        json={"destinatario_id": b.id, "titulo": "Arq", "texto": "Texto"},
    )
    msg_id = resp.json()["id"]

    resp = client.patch(f"/v1/mensagens/{msg_id}/arquivar", headers=h_b)
    assert resp.status_code == 200
    assert resp.json()["arquivada_em"] is not None

    resp = client.patch(
        f"/v1/mensagens/{msg_id}/arquivar",
        headers=h_b,
        json={"arquivar": False},
    )
    assert resp.status_code == 200
    assert resp.json()["arquivada_em"] is None


def test_anexo_upload_e_download_autenticado(
    client: TestClient, db_session: Session, tmp_path, monkeypatch
):
    from app.mensagens import router as mensagens_router

    monkeypatch.setattr(mensagens_router, "UPLOADS_DIR", str(tmp_path))

    a = _criar_usuario(db_session, "msg_a3")
    b = _criar_usuario(db_session, "msg_b3")
    h_a = _token(client, "msg_a3")
    h_b = _token(client, "msg_b3")

    resp = client.post(
        "/v1/mensagens",
        headers=h_a,
        json={"destinatario_id": b.id, "titulo": "Com anexo", "texto": "Veja"},
    )
    msg_id = resp.json()["id"]

    resp = client.post(
        f"/v1/mensagens/{msg_id}/anexos",
        headers=h_a,
        files={"file": ("relatorio.pdf", b"%PDF-1.4 exemplo", "application/pdf")},
    )
    assert resp.status_code == 201, resp.text
    anexo = resp.json()
    assert anexo["nome_arquivo_original"] == "relatorio.pdf"
    assert anexo["tamanho_bytes"] == 16

    # terceiro não participa -> 403 no download
    c = _criar_usuario(db_session, "msg_c3")
    h_c = _token(client, "msg_c3")
    resp = client.get(
        f"/v1/mensagens/{msg_id}/anexos/{anexo['id']}/download", headers=h_c
    )
    assert resp.status_code == 403

    # participante (destinatário) baixa
    resp = client.get(
        f"/v1/mensagens/{msg_id}/anexos/{anexo['id']}/download", headers=h_b
    )
    assert resp.status_code == 200
    assert resp.content == b"%PDF-1.4 exemplo"

    # upload por não-remetente -> 403
    resp = client.post(
        f"/v1/mensagens/{msg_id}/anexos",
        headers=h_b,
        files={"file": ("x.txt", b"ola", "text/plain")},
    )
    assert resp.status_code == 403

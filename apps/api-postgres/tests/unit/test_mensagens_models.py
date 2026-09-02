"""Testes de modelos do módulo de mensagens."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.mensagens.models import AnexoMensagem, Mensagem
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha


def _usuario(db: Session, username: str) -> Usuario:
    u = Usuario(
        username=username,
        email=f"{username}@x.com",
        nome_completo=username,
        senha_hash=gerar_hash_senha("senha123"),
        role="operador",
    )
    db.add(u)
    db.commit()
    return u


def test_mensagem_cria_e_resposta_aponta_raiz(db_session: Session):
    a = _usuario(db_session, "alice")
    b = _usuario(db_session, "bob")

    raiz = Mensagem(
        remetente_id=a.id,
        destinatario_id=b.id,
        titulo="Olá",
        texto="Mensagem inicial",
        categoria="DIRETA",
    )
    db_session.add(raiz)
    db_session.commit()

    resposta = Mensagem(
        resposta_a_id=raiz.id,
        remetente_id=b.id,
        destinatario_id=a.id,
        titulo="Re: Olá",
        texto="Resposta",
        categoria="DIRETA",
    )
    db_session.add(resposta)
    db_session.commit()

    assert raiz.id is not None
    assert resposta.resposta_a_id == raiz.id
    assert isinstance(raiz.criado_em, datetime)


def test_anexo_mensagem_cria_e_relaciona(db_session: Session):
    a = _usuario(db_session, "alice2")
    b = _usuario(db_session, "bob2")
    msg = Mensagem(
        remetente_id=a.id,
        destinatario_id=b.id,
        titulo="Com anexo",
        texto="Texto",
        categoria="DIRETA",
    )
    db_session.add(msg)
    db_session.commit()

    anexo = AnexoMensagem(
        mensagem_id=msg.id,
        nome_arquivo_original="doc.pdf",
        caminho="mensagens/abc.pdf",
        content_type="application/pdf",
        tamanho_bytes=10,
    )
    db_session.add(anexo)
    db_session.commit()

    assert anexo.id is not None
    assert anexo.mensagem_id == msg.id
    assert anexo.tamanho_bytes == 10

"""Testes unitários para o AuditService."""
import time

from sqlalchemy.orm import Session

from app.audit.service import AuditService
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha


def _mkuser(db: Session) -> Usuario:
    u = Usuario(
        username="aud", email="aud@x.com", nome_completo="Aud",
        senha_hash=gerar_hash_senha("x"),
    )
    db.add(u)
    db.commit()
    return u


def test_registrar_audit(db_session: Session):
    svc = AuditService(db_session)
    log = svc.registrar_audit(
        user_id=1, entidade="Usuario", entidade_id=2, acao="update",
        campos_alterados=["email"], ip="10.0.0.1",
    )
    db_session.commit()
    db_session.refresh(log)
    assert log.id is not None


def test_abrir_e_fechar_sessao_calcula_duracao(db_session: Session):
    user = _mkuser(db_session)
    svc = AuditService(db_session)
    sessao = svc.abrir_sessao(user.id, ip="127.0.0.1")
    assert sessao.login_at is not None
    time.sleep(1.1)
    fechada = svc.fechar_sessao(user.id, motivo="logout")
    assert fechada.id == sessao.id
    assert fechada.logout_at is not None
    assert fechada.logout_motivo == "logout"
    assert fechada.duracao_segundos is not None and fechada.duracao_segundos >= 1


def test_fechar_sessao_sem_aberta_retorna_none(db_session: Session):
    user = _mkuser(db_session)
    assert AuditService(db_session).fechar_sessao(user.id) is None


def test_fechar_fecha_mais_recente(db_session: Session):
    user = _mkuser(db_session)
    svc = AuditService(db_session)
    s1 = svc.abrir_sessao(user.id)
    time.sleep(0.3)
    s2 = svc.abrir_sessao(user.id)
    fechada = svc.fechar_sessao(user.id)
    assert fechada.id == s2.id
    assert svc.fechar_sessao(user.id).id == s1.id
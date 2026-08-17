"""Testes unitários para os listeners de auditoria automática."""
import pytest
from sqlalchemy.orm import Session

from app.audit.context import audit_ip, audit_user_id
from app.audit.models import AuditLog
from app.audit.service import AuditService
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha


def _usuario(**kwargs) -> Usuario:
    dados = {
        "username": "aud",
        "email": "aud@x.com",
        "nome_completo": "Aud",
        "senha_hash": gerar_hash_senha("x"),
    }
    dados.update(kwargs)
    return Usuario(**dados)


def test_insert_genera_audit_log(db_session: Session):
    db_session.add(_usuario())
    db_session.commit()
    logs = db_session.query(AuditLog).filter(AuditLog.acao == "insert").all()
    assert len(logs) == 1
    assert logs[0].entidade == "Usuario"
    assert "username" in logs[0].campos_alterados


def test_update_captura_campos_alterados(db_session: Session):
    u = _usuario()
    db_session.add(u)
    db_session.commit()
    u.email = "novo@x.com"
    db_session.commit()
    logs = db_session.query(AuditLog).filter(AuditLog.acao == "update").all()
    assert len(logs) == 1
    assert logs[0].entidade_id == u.id
    assert "email" in logs[0].campos_alterados


def test_delete_genera_audit_log(db_session: Session):
    u = _usuario()
    db_session.add(u)
    db_session.commit()
    db_session.delete(u)
    db_session.commit()
    logs = db_session.query(AuditLog).filter(AuditLog.acao == "delete").all()
    assert len(logs) == 1
    assert logs[0].entidade_id == u.id


def test_usa_contexto_do_usuario(db_session: Session):
    audit_user_id.set(42)
    audit_ip.set("10.0.0.7")
    try:
        db_session.add(_usuario())
        db_session.commit()
    finally:
        audit_user_id.set(None)
        audit_ip.set(None)
    log = db_session.query(AuditLog).first()
    assert log.user_id == 42
    assert log.ip == "10.0.0.7"


@pytest.mark.parametrize("acao", ["insert", "update", "delete"])
def test_nao_audita_models_excluidos(db_session: Session, acao: str):
    audit_user_id.set(1)
    try:
        svc = AuditService(db_session)
        if acao == "insert":
            svc.abrir_sessao(1)
        elif acao == "update":
            s = svc.abrir_sessao(1)
            s.ip = "9.9.9.9"
        else:
            s = svc.abrir_sessao(1)
            db_session.delete(s)
        db_session.commit()
    finally:
        audit_user_id.set(None)
    assert db_session.query(AuditLog).count() == 0

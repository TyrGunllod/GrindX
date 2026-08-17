"""Testes unitários para os modelos de auditoria."""

from sqlalchemy.orm import Session

from app.audit.models import AuditLog, Sessao


def test_create_audit_log(db_session: Session):
    log = AuditLog(
        user_id=1,
        entidade="Usuario",
        entidade_id=3,
        acao="update",
        campos_alterados=["email", "role"],
        ip="127.0.0.1",
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    assert log.id is not None
    assert log.campos_alterados == ["email", "role"]
    assert log.criado_em is not None


def test_create_sessao(db_session: Session):
    sessao = Sessao(user_id=1, ip="127.0.0.1")
    db_session.add(sessao)
    db_session.commit()
    db_session.refresh(sessao)
    assert sessao.id is not None
    assert sessao.login_at is not None
    assert sessao.logout_at is None

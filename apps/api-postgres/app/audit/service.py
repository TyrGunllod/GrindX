"""Serviço de auditoria: registro explícito de sessões e logs."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.audit.models import AuditLog, Sessao


class AuditService:
    """Serviço para registro de sessões (login/logout) e logs de auditoria."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def registrar_audit(
        self,
        user_id: int | None,
        entidade: str,
        entidade_id: int | None,
        acao: str,
        campos_alterados: list[str],
        ip: str | None = None,
    ) -> AuditLog:
        """Registra um log de auditoria na mesma transação.

        Args:
            user_id: ID do usuário que realizou a ação (pode ser None).
            entidade: Nome da entidade (ex: "Usuario").
            entidade_id: ID da entidade alterada (pode ser None).
            acao: Tipo de ação (insert, update, delete).
            campos_alterados: Nomes dos campos alterados.
            ip: Endereço IP de origem da requisição.

        Returns:
            AuditLog criado.
        """
        log = AuditLog(
            user_id=user_id,
            entidade=entidade,
            entidade_id=entidade_id,
            acao=acao,
            campos_alterados=campos_alterados,
            ip=ip,
        )
        self.db.add(log)
        self.db.flush()
        return log

    def abrir_sessao(self, user_id: int, ip: str | None = None) -> Sessao:
        """Registra o login de um usuário.

        Sessões acumulam — cada login cria uma nova linha.

        Args:
            user_id: ID do usuário.
            ip: Endereço IP de origem do login.

        Returns:
            Sessao criada.
        """
        sessao = Sessao(user_id=user_id, ip=ip)
        self.db.add(sessao)
        self.db.flush()
        self.db.refresh(sessao)
        return sessao

    def fechar_sessao(self, user_id: int, motivo: str = "logout") -> Sessao | None:
        """Fecha a sessão aberta mais recente do usuário.

        Args:
            user_id: ID do usuário.
            motivo: Motivo do fechamento (logout, inativo, expirado).

        Returns:
            Sessao fechada, ou None se não houver sessão aberta.
        """
        sessao = (
            self.db.query(Sessao)
            .filter(Sessao.user_id == user_id, Sessao.logout_at.is_(None))
            .order_by(Sessao.login_at.desc(), Sessao.id.desc())
            .first()
        )
        if sessao is None:
            return None

        now = datetime.now(timezone.utc)
        login_at = sessao.login_at
        if login_at is not None and login_at.tzinfo is None:
            login_at = login_at.replace(tzinfo=timezone.utc)

        sessao.logout_at = now
        sessao.logout_motivo = motivo
        if login_at is not None:
            sessao.duracao_segundos = int((now - login_at).total_seconds())
        self.db.flush()
        return sessao

"""Service do módulo central de mensagens."""

import structlog
from shared.exceptions.base import (
    BusinessValidationError,
    ForbiddenError,
    NotFoundError,
)
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, aliased

from app.mensagens.models import AnexoMensagem, Mensagem
from app.mensagens.schemas import (
    BroadcastCreate,
    MensagemCreate,
    OrdemMensagem,
    RespostaCreate,
    StatusMensagem,
)
from app.models.usuario import Usuario

logger = structlog.get_logger(__name__)

_CATEGORIAS_SISTEMA = {"SISTEMA", "AVISO"}


class MensagensService:
    """Regras de negócio de mensagens, threads e anexos."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _obter_raiz(self, mensagem_id: int) -> Mensagem:
        msg = self.db.get(Mensagem, mensagem_id)
        if msg is None:
            raise NotFoundError("Mensagem", mensagem_id)
        if msg.resposta_a_id is not None:
            raiz = self.db.get(Mensagem, msg.resposta_a_id)
            if raiz is None:
                raise NotFoundError("Mensagem", msg.resposta_a_id)
            return raiz
        return msg

    def _verificar_participante(self, raiz: Mensagem, usuario_id: int) -> None:
        participantes = {raiz.remetente_id, raiz.destinatario_id}
        if usuario_id not in participantes:
            raise ForbiddenError(
                message="Acesso restrito aos participantes da conversa."
            )

    def _verificar_destinatario(self, msg: Mensagem, usuario_id: int) -> None:
        if msg.destinatario_id != usuario_id:
            raise ForbiddenError(message="Permissão insuficiente para esta mensagem.")

    # ------------------------------------------------------------------
    # Criação
    # ------------------------------------------------------------------
    def criar_mensagem(
        self, usuario_id: int, dados: MensagemCreate, is_admin: bool = False
    ) -> Mensagem:
        destinatario = self.db.get(Usuario, dados.destinatario_id)
        if destinatario is None:
            raise NotFoundError("Usuario", dados.destinatario_id)

        categoria = dados.categoria.value
        if categoria in _CATEGORIAS_SISTEMA and not is_admin:
            raise ForbiddenError(
                message="Apenas administradores podem enviar mensagens "
                "das categorias SISTEMA ou AVISO."
            )

        msg = Mensagem(
            remetente_id=None if categoria in _CATEGORIAS_SISTEMA else usuario_id,
            destinatario_id=dados.destinatario_id,
            titulo=dados.titulo.strip(),
            texto=dados.texto,
            categoria=categoria,
            url_acao=dados.url_acao,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        logger.info("Mensagem criada", id=msg.id, categoria=categoria)
        return msg

    def criar_broadcast(
        self, usuario_id: int, dados: BroadcastCreate, is_admin: bool
    ) -> int:
        """Envia mensagem SISTEMA/AVISO para todos os usuários ativos (admin)."""
        categoria = dados.categoria.value
        if categoria not in _CATEGORIAS_SISTEMA:
            raise BusinessValidationError(
                message="Broadcast disponível apenas para as categorias SISTEMA ou AVISO."
            )
        if not is_admin:
            raise ForbiddenError(
                message="Apenas administradores podem enviar mensagens do sistema."
            )

        usuarios = self.db.query(Usuario).filter(Usuario.ativo.is_(True)).all()
        for u in usuarios:
            self.db.add(
                Mensagem(
                    remetente_id=None,
                    destinatario_id=u.id,
                    titulo=dados.titulo.strip(),
                    texto=dados.texto,
                    categoria=categoria,
                    url_acao=dados.url_acao,
                )
            )
        self.db.commit()
        logger.info(
            "Broadcast criado",
            categoria=categoria,
            destinatarios=len(usuarios),
        )
        return len(usuarios)

    def criar_resposta(
        self, usuario_id: int, mensagem_id: int, dados: RespostaCreate
    ) -> Mensagem:
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_participante(raiz, usuario_id)

        if raiz.remetente_id is None:
            raise ForbiddenError(
                message="Não é possível responder a mensagens do sistema."
            )

        outro = (
            raiz.destinatario_id
            if raiz.remetente_id == usuario_id
            else raiz.remetente_id
        )
        resposta = Mensagem(
            resposta_a_id=raiz.id,
            remetente_id=usuario_id,
            destinatario_id=outro,
            titulo=(dados.titulo or raiz.titulo).strip(),
            texto=dados.texto,
            categoria="DIRETA",
            url_acao=dados.url_acao,
        )
        self.db.add(resposta)
        self.db.commit()
        self.db.refresh(resposta)
        logger.info("Resposta criada", id=resposta.id, raiz_id=raiz.id)
        return resposta

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------
    def listar_mensagens(
        self,
        usuario_id: int,
        status: StatusMensagem,
        ordem: OrdemMensagem,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        resposta_alias = aliased(Mensagem)

        tem_resposta_nao_lida = (
            self.db.query(func.count(resposta_alias.id))
            .filter(
                resposta_alias.resposta_a_id == Mensagem.id,
                resposta_alias.destinatario_id == usuario_id,
                resposta_alias.lida_em.is_(None),
            )
            .as_scalar()
            > 0
        )

        subq = (
            self.db.query(
                Mensagem.resposta_a_id.label("raiz_id"),
                func.count(Mensagem.id).label("qtd_respostas"),
                func.max(Mensagem.criado_em).label("ultima_resposta"),
            )
            .filter(Mensagem.resposta_a_id.isnot(None))
            .group_by(Mensagem.resposta_a_id)
            .subquery()
        )

        anexos_subq = (
            self.db.query(
                AnexoMensagem.mensagem_id.label("msg_id"),
                func.count(AnexoMensagem.id).label("qtd_anexos"),
            )
            .group_by(AnexoMensagem.mensagem_id)
            .subquery()
        )

        nao_lidas_subq = (
            self.db.query(
                Mensagem.resposta_a_id.label("raiz_id"),
                func.count(Mensagem.id).label("qtd_nao_lidas"),
            )
            .filter(
                Mensagem.resposta_a_id.isnot(None),
                Mensagem.destinatario_id == usuario_id,
                Mensagem.lida_em.is_(None),
            )
            .group_by(Mensagem.resposta_a_id)
            .subquery()
        )

        participante = or_(
            Mensagem.destinatario_id == usuario_id,
            Mensagem.remetente_id == usuario_id,
        )

        q = (
            self.db.query(
                Mensagem,
                Usuario.nome_completo,
                subq.c.qtd_respostas,
                subq.c.ultima_resposta,
                anexos_subq.c.qtd_anexos,
                nao_lidas_subq.c.qtd_nao_lidas,
            )
            .outerjoin(subq, subq.c.raiz_id == Mensagem.id)
            .outerjoin(Usuario, Usuario.id == Mensagem.remetente_id)
            .outerjoin(anexos_subq, anexos_subq.c.msg_id == Mensagem.id)
            .outerjoin(nao_lidas_subq, nao_lidas_subq.c.raiz_id == Mensagem.id)
            .filter(Mensagem.resposta_a_id.is_(None))
        )

        raiz_nao_lida = and_(
            Mensagem.destinatario_id == usuario_id,
            Mensagem.lida_em.is_(None),
        )

        if status == StatusMensagem.ARQUIVADAS:
            # Arquivadas só fazem sentido para o destinatário (único que pode arquivar)
            q = q.filter(Mensagem.destinatario_id == usuario_id).filter(
                Mensagem.arquivada_em.isnot(None)
            )
        else:
            q = q.filter(participante)
            if status == StatusMensagem.NAO_LIDAS:
                q = q.filter(Mensagem.arquivada_em.is_(None)).filter(
                    or_(raiz_nao_lida, tem_resposta_nao_lida)
                )
            elif status == StatusMensagem.LIDAS:
                q = q.filter(Mensagem.arquivada_em.is_(None)).filter(
                    and_(~raiz_nao_lida, ~tem_resposta_nao_lida)
                )
            else:  # TODAS
                q = q.filter(Mensagem.arquivada_em.is_(None))

        atividade = func.coalesce(subq.c.ultima_resposta, Mensagem.criado_em)
        ordem_dir = (
            atividade.desc() if ordem == OrdemMensagem.DECRESCENTE else atividade.asc()
        )
        q = q.order_by(ordem_dir)

        total = q.count()
        rows = q.offset((page - 1) * page_size).limit(page_size).all()

        itens = []
        for msg, nome, qtd, ultima, qtd_anexos, qtd_nao_lidas in rows:
            nao_lida = (msg.destinatario_id == usuario_id and msg.lida_em is None) or (
                qtd_nao_lidas or 0
            ) > 0
            item = {
                "id": msg.id,
                "resposta_a_id": msg.resposta_a_id,
                "remetente_id": msg.remetente_id,
                "remetente_nome": nome,
                "destinatario_id": msg.destinatario_id,
                "titulo": msg.titulo,
                "texto": msg.texto,
                "categoria": msg.categoria,
                "url_acao": msg.url_acao,
                "lida_em": msg.lida_em,
                "arquivada_em": msg.arquivada_em,
                "criado_em": msg.criado_em,
                "quantidade_respostas": qtd or 0,
                "ultima_resposta_em": ultima,
                "anexos_count": qtd_anexos or 0,
                "nao_lida": nao_lida,
            }
            itens.append(item)
        return itens, total

    def listar_thread(self, usuario_id: int, mensagem_id: int) -> list[dict]:
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_participante(raiz, usuario_id)

        rows = (
            self.db.query(Mensagem, Usuario.nome_completo)
            .outerjoin(Usuario, Usuario.id == Mensagem.remetente_id)
            .filter(or_(Mensagem.id == raiz.id, Mensagem.resposta_a_id == raiz.id))
            .order_by(Mensagem.criado_em.desc(), Mensagem.id.desc())
            .all()
        )
        ids = [m.id for m, _ in rows]
        anexos = (
            self.db.query(AnexoMensagem)
            .filter(AnexoMensagem.mensagem_id.in_(ids))
            .order_by(AnexoMensagem.id.asc())
            .all()
        )
        anexos_por_msg: dict[int, list] = {}
        for anexo in anexos:
            anexos_por_msg.setdefault(anexo.mensagem_id, []).append(anexo)

        itens = []
        for msg, nome in rows:
            item = {
                "id": msg.id,
                "resposta_a_id": msg.resposta_a_id,
                "remetente_id": msg.remetente_id,
                "remetente_nome": nome,
                "destinatario_id": msg.destinatario_id,
                "titulo": msg.titulo,
                "texto": msg.texto,
                "categoria": msg.categoria,
                "url_acao": msg.url_acao,
                "lida_em": msg.lida_em,
                "arquivada_em": msg.arquivada_em,
                "criado_em": msg.criado_em,
                "quantidade_respostas": 0,
                "ultima_resposta_em": None,
                "anexos_count": len(anexos_por_msg.get(msg.id, [])),
                "anexos": [
                    {
                        "id": a.id,
                        "nome_arquivo_original": a.nome_arquivo_original,
                        "content_type": a.content_type,
                        "tamanho_bytes": a.tamanho_bytes,
                        "criado_em": a.criado_em,
                    }
                    for a in anexos_por_msg.get(msg.id, [])
                ],
            }
            itens.append(item)
        return itens

    def contar_nao_lidas(self, usuario_id: int) -> int:
        raiz_alias = aliased(Mensagem)
        return (
            self.db.query(Mensagem)
            .outerjoin(raiz_alias, Mensagem.resposta_a_id == raiz_alias.id)
            .filter(
                Mensagem.destinatario_id == usuario_id,
                Mensagem.lida_em.is_(None),
                func.coalesce(Mensagem.arquivada_em, raiz_alias.arquivada_em).is_(None),
            )
            .count()
        )

    def listar_destinatarios(
        self,
        solicitante_id: int,
        page: int = 1,
        page_size: int = 100,
        role: str | None = None,
    ) -> tuple[list[Usuario], int]:
        """Lista usuários ativos disponíveis como destinatários (inclui administradores).

        Qualquer usuário autenticado pode listar; exclui o próprio solicitante.
        Filtro opcional por `role` (ex.: `admin`).
        """
        q = self.db.query(Usuario).filter(
            Usuario.id != solicitante_id,
            Usuario.ativo.is_(True),
        )
        if role:
            q = q.filter(Usuario.role == role)
        q = q.order_by(Usuario.nome_completo.asc(), Usuario.id.asc())
        total = q.count()
        rows = q.offset((page - 1) * page_size).limit(page_size).all()
        return rows, total

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def marcar_lida(self, usuario_id: int, mensagem_id: int) -> Mensagem:
        msg = self.db.get(Mensagem, mensagem_id)
        if msg is None:
            raise NotFoundError("Mensagem", mensagem_id)
        self._verificar_destinatario(msg, usuario_id)
        if msg.lida_em is None:
            msg.lida_em = func.now()
            self.db.commit()
            self.db.refresh(msg)
        return msg

    def marcar_thread_lida(self, usuario_id: int, mensagem_id: int) -> int:
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_participante(raiz, usuario_id)
        q = self.db.query(Mensagem).filter(
            or_(Mensagem.id == raiz.id, Mensagem.resposta_a_id == raiz.id),
            Mensagem.destinatario_id == usuario_id,
            Mensagem.lida_em.is_(None),
        )
        count = q.count()
        q.update({Mensagem.lida_em: func.now()}, synchronize_session=False)
        self.db.commit()
        return count

    def arquivar(
        self, usuario_id: int, mensagem_id: int, arquivar: bool = True
    ) -> Mensagem:
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_destinatario(raiz, usuario_id)
        raiz.arquivada_em = func.now() if arquivar else None
        self.db.commit()
        self.db.refresh(raiz)
        return raiz

    # ------------------------------------------------------------------
    # Anexos
    # ------------------------------------------------------------------
    def listar_anexos(self, usuario_id: int, mensagem_id: int) -> list[AnexoMensagem]:
        msg = self.db.get(Mensagem, mensagem_id)
        if msg is None:
            raise NotFoundError("Mensagem", mensagem_id)
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_participante(raiz, usuario_id)
        return (
            self.db.query(AnexoMensagem)
            .filter(AnexoMensagem.mensagem_id == mensagem_id)
            .order_by(AnexoMensagem.id.asc())
            .all()
        )

    def salvar_anexo_meta(
        self,
        mensagem_id: int,
        nome_original: str,
        caminho: str,
        content_type: str,
        tamanho_bytes: int,
    ) -> AnexoMensagem:
        anexo = AnexoMensagem(
            mensagem_id=mensagem_id,
            nome_arquivo_original=nome_original,
            caminho=caminho,
            content_type=content_type,
            tamanho_bytes=tamanho_bytes,
        )
        self.db.add(anexo)
        self.db.commit()
        self.db.refresh(anexo)
        return anexo

    def obter_anexo(
        self, usuario_id: int, mensagem_id: int, anexo_id: int
    ) -> AnexoMensagem:
        raiz = self._obter_raiz(mensagem_id)
        self._verificar_participante(raiz, usuario_id)
        anexo = (
            self.db.query(AnexoMensagem)
            .filter(AnexoMensagem.id == anexo_id)
            .filter(AnexoMensagem.mensagem_id == mensagem_id)
            .first()
        )
        if anexo is None:
            raise NotFoundError("Anexo", anexo_id)
        return anexo

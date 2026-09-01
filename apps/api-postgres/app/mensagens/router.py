"""Router do módulo central de mensagens."""

import os
import uuid

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from shared.exceptions.base import ForbiddenError, NotFoundError
from shared.schemas.auth import TokenPayload
from shared.schemas.base import PaginatedResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.mensagens.models import Mensagem
from app.mensagens.schemas import (
    AnexoResponse,
    ArquivarRequest,
    CountResponse,
    DestinatarioResponse,
    MensagemCreate,
    MensagemResponse,
    OrdemMensagem,
    RespostaCreate,
    StatusMensagem,
)
from app.mensagens.service import MensagensService
from app.models.usuario import Usuario

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/mensagens", tags=["Mensagens"])

UPLOADS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"
)

MAX_ANEXO_BYTES = 10 * 1024 * 1024  # 10 MB
CONTENT_TYPES_PERMITIDOS = {
    "application/pdf",
    "text/plain",
    "text/csv",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/zip",
}


def _get_mensagens_service(db: Session = Depends(get_db)) -> MensagensService:
    return MensagensService(db)


def _is_admin(user: TokenPayload) -> bool:
    return user.role == "admin"


@router.get("", response_model=PaginatedResponse[MensagemResponse])
def listar_mensagens(
    status: StatusMensagem = Query(StatusMensagem.TODAS),
    ordem: OrdemMensagem = Query(OrdemMensagem.DECRESCENTE),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Lista as mensagens raiz do destinatário logado."""
    service = MensagensService(db)
    itens, total = service.listar_mensagens(
        int(current_user.sub), status, ordem, page, page_size
    )
    return PaginatedResponse(
        items=[MensagemResponse.model_validate(i) for i in itens],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/nao-lidas/count", response_model=CountResponse)
def contar_nao_lidas(
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Total de mensagens não lidas (raiz e respostas, excluindo arquivadas)."""
    service = MensagensService(db)
    return CountResponse(count=service.contar_nao_lidas(int(current_user.sub)))


@router.get(
    "/destinatarios", response_model=PaginatedResponse[DestinatarioResponse]
)
def listar_destinatarios(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=100),
    role: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Lista usuários ativos disponíveis como destinatários (inclui administradores).

    Qualquer usuário autenticado pode listar; exclui o próprio solicitante.
    Filtro opcional `?role=admin` para listar apenas administradores.
    """
    service = MensagensService(db)
    rows, total = service.listar_destinatarios(
        int(current_user.sub), page, page_size, role
    )
    return PaginatedResponse(
        items=[DestinatarioResponse.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=MensagemResponse)
def criar_mensagem(
    dados: MensagemCreate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Cria mensagem raiz. SISTEMA/AVISO exigem admin."""
    service = MensagensService(db)
    msg = service.criar_mensagem(
        int(current_user.sub), dados, is_admin=_is_admin(current_user)
    )
    resp = MensagemResponse.model_validate(msg)
    resp.remetente_nome = None
    if msg.remetente_id is not None:
        u = db.get(Usuario, msg.remetente_id)
        resp.remetente_nome = u.nome_completo if u else None
    return resp


@router.get("/{mensagem_id}/thread", response_model=list[MensagemResponse])
def listar_thread(
    mensagem_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Retorna a raiz e todas as respostas da thread."""
    service = MensagensService(db)
    itens = service.listar_thread(int(current_user.sub), mensagem_id)
    return [MensagemResponse.model_validate(i) for i in itens]


@router.post("/{mensagem_id}/respostas", response_model=MensagemResponse)
def criar_resposta(
    mensagem_id: int,
    dados: RespostaCreate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Responde à thread (apenas participantes; categorias diretas)."""
    service = MensagensService(db)
    resposta = service.criar_resposta(
        int(current_user.sub), mensagem_id, dados
    )
    return MensagemResponse.model_validate(resposta)


@router.patch("/{mensagem_id}/lida", response_model=MensagemResponse)
def marcar_lida(
    mensagem_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Marca a mensagem como lida (apenas o destinatário)."""
    service = MensagensService(db)
    msg = service.marcar_lida(int(current_user.sub), mensagem_id)
    return MensagemResponse.model_validate(msg)


@router.patch("/{mensagem_id}/thread/lida", response_model=CountResponse)
def marcar_thread_lida(
    mensagem_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Marca todas as mensagens da thread destinadas ao usuário como lidas."""
    service = MensagensService(db)
    count = service.marcar_thread_lida(int(current_user.sub), mensagem_id)
    return CountResponse(count=count)


@router.patch("/{mensagem_id}/arquivar", response_model=MensagemResponse)
def arquivar_mensagem(
    mensagem_id: int,
    payload: ArquivarRequest | None = None,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Arquiva/restaura a thread (apenas o destinatário da raiz)."""
    service = MensagensService(db)
    arquivar = payload.arquivar if payload is not None else True
    msg = service.arquivar(int(current_user.sub), mensagem_id, arquivar=arquivar)
    return MensagemResponse.model_validate(msg)


@router.post(
    "/{mensagem_id}/anexos",
    response_model=AnexoResponse,
    status_code=201,
)
async def anexar_arquivo(
    mensagem_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Anexa um arquivo à mensagem (apenas o remetente da mensagem)."""
    msg = db.get(Mensagem, mensagem_id)
    if msg is None:
        raise NotFoundError("Mensagem", mensagem_id)
    if msg.remetente_id != int(current_user.sub):
        raise ForbiddenError(message="Apenas o remetente pode anexar arquivos.")

    if file.content_type not in CONTENT_TYPES_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não permitido: {file.content_type}",
        )

    content = await file.read()
    if len(content) > MAX_ANEXO_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. Tamanho máximo: {MAX_ANEXO_BYTES // (1024 * 1024)}MB",
        )

    ext = os.path.splitext(file.filename or "")[1].lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    sub_dir = "mensagens"
    dest_dir = os.path.join(UPLOADS_DIR, sub_dir)
    os.makedirs(dest_dir, exist_ok=True)
    caminho = os.path.join(sub_dir, unique_filename)
    file_path = os.path.join(dest_dir, unique_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    service = MensagensService(db)
    anexo = service.salvar_anexo_meta(
        mensagem_id=msg.id,
        nome_original=file.filename or unique_filename,
        caminho=caminho,
        content_type=file.content_type,
        tamanho_bytes=len(content),
    )
    logger.info("Anexo salvo", anexo_id=anexo.id, mensagem_id=msg.id, bytes=len(content))
    return anexo


@router.get("/{mensagem_id}/anexos", response_model=list[AnexoResponse])
def listar_anexos(
    mensagem_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Lista anexos da mensagem (participantes da thread)."""
    service = MensagensService(db)
    return service.listar_anexos(int(current_user.sub), mensagem_id)


@router.get("/{mensagem_id}/anexos/{anexo_id}/download")
def baixar_anexo(
    mensagem_id: int,
    anexo_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Baixa o anexo com autenticação (participantes da thread)."""
    service = MensagensService(db)
    anexo = service.obter_anexo(int(current_user.sub), mensagem_id, anexo_id)
    file_path = os.path.join(UPLOADS_DIR, anexo.caminho)
    if not os.path.exists(file_path):
        raise NotFoundError("Anexo", anexo_id)
    return FileResponse(
        file_path,
        media_type=anexo.content_type,
        filename=anexo.nome_arquivo_original,
    )

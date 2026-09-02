"""Schemas do módulo central de mensagens."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class CategoriaMensagem(StrEnum):
    SISTEMA = "SISTEMA"
    DIRETA = "DIRETA"
    AVISO = "AVISO"


class StatusMensagem(StrEnum):
    TODAS = "todas"
    NAO_LIDAS = "nao_lidas"
    LIDAS = "lidas"
    ARQUIVADAS = "arquivadas"


class OrdemMensagem(StrEnum):
    CRESCENTE = "crescente"
    DECRESCENTE = "decrescente"


class MensagemCreate(BaseModel):
    """Criação de mensagem raiz."""

    destinatario_id: int = Field(..., ge=1)
    titulo: str = Field(..., min_length=1, max_length=150)
    texto: str = Field(..., min_length=1)
    categoria: CategoriaMensagem = CategoriaMensagem.DIRETA
    url_acao: str | None = Field(default=None, max_length=255)


class BroadcastCreate(BaseModel):
    """Criação de mensagem broadcast (SISTEMA/AVISO para todos os usuários ativos)."""

    titulo: str = Field(..., min_length=1, max_length=150)
    texto: str = Field(..., min_length=1)
    categoria: CategoriaMensagem = CategoriaMensagem.SISTEMA
    url_acao: str | None = Field(default=None, max_length=255)


class RespostaCreate(BaseModel):
    """Criação de resposta em uma thread."""

    texto: str = Field(..., min_length=1)
    titulo: str | None = Field(default=None, max_length=150)
    url_acao: str | None = Field(default=None, max_length=255)


class ArquivarRequest(BaseModel):
    """Body opcional do arquivamento (default: arquivar)."""

    arquivar: bool = True


class AnexoResponse(BaseModel):
    """Resposta com metadados de anexo."""

    id: int
    nome_arquivo_original: str
    content_type: str
    tamanho_bytes: int
    criado_em: datetime | None = None

    class Config:
        from_attributes = True


class MensagemResponse(BaseModel):
    """Resposta de uma mensagem (raiz ou resposta)."""

    id: int
    resposta_a_id: int | None = None
    remetente_id: int | None = None
    remetente_nome: str | None = None
    destinatario_id: int
    titulo: str
    texto: str
    categoria: str
    url_acao: str | None = None
    lida_em: datetime | None = None
    arquivada_em: datetime | None = None
    criado_em: datetime | None = None
    quantidade_respostas: int = 0
    ultima_resposta_em: datetime | None = None
    anexos: list[AnexoResponse] = []
    anexos_count: int = 0
    nao_lida: bool = False

    class Config:
        from_attributes = True


class CountResponse(BaseModel):
    """Resposta do contador de não lidas."""

    count: int


class DestinatarioResponse(BaseModel):
    """Usuário disponível como destinatário (inclui administradores)."""

    id: int
    username: str
    nome_completo: str
    role: str
    email: str

    class Config:
        from_attributes = True

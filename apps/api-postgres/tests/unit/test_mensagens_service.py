"""Testes de unidade do service de mensagens."""

import pytest
from shared.exceptions.base import BusinessValidationError, ForbiddenError, NotFoundError
from sqlalchemy.orm import Session

from app.mensagens.models import Mensagem
from app.mensagens.schemas import (
    MensagemCreate,
    OrdemMensagem,
    RespostaCreate,
    StatusMensagem,
)
from app.mensagens.service import MensagensService
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha


def _usuario(db: Session, username: str, role: str = "operador") -> Usuario:
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


def _criar_raiz(db, de, para, **kwargs):
    dados = MensagemCreate(
        destinatario_id=para.id,
        titulo=kwargs.get("titulo", "Título"),
        texto=kwargs.get("texto", "Texto"),
        categoria=kwargs.get("categoria", "DIRETA"),
        url_acao=kwargs.get("url_acao"),
    )
    return MensagensService(db).criar_mensagem(
        usuario_id=de.id, dados=dados, is_admin=kwargs.get("is_admin", False)
    )


def test_criar_mensagem_direta_define_remetente_logado(db_session: Session):
    a = _usuario(db_session, "rem1")
    b = _usuario(db_session, "dest1")
    msg = _criar_raiz(db_session, a, b)
    assert msg.remetente_id == a.id
    assert msg.destinatario_id == b.id
    assert msg.categoria == "DIRETA"
    assert msg.lida_em is None


def test_criar_mensagem_sistema_requer_admin_e_remetente_null(db_session: Session):
    admin = _usuario(db_session, "adm1", role="admin")
    comum = _usuario(db_session, "comum1", role="operador")
    b = _usuario(db_session, "dest2")

    # Usuário comum NÃO pode enviar SISTEMA
    with pytest.raises(ForbiddenError):
        _criar_raiz(db_session, comum, b, categoria="SISTEMA")

    # Admin pode; remetente fica NULL
    msg = _criar_raiz(db_session, admin, b, categoria="AVISO", is_admin=True)
    assert msg.remetente_id is None
    assert msg.categoria == "AVISO"


def test_criar_mensagem_destinatario_inexistente(db_session: Session):
    a = _usuario(db_session, "rem2")
    dados = MensagemCreate(
        destinatario_id=99999, titulo="X", texto="Y", categoria="DIRETA"
    )
    with pytest.raises(NotFoundError):
        MensagensService(db_session).criar_mensagem(a.id, dados, is_admin=False)


def test_contar_nao_lidas_ignora_lidas_e_arquivadas(db_session: Session):
    a = _usuario(db_session, "rem3")
    b = _usuario(db_session, "dest3")
    svc = MensagensService(db_session)

    m1 = _criar_raiz(db_session, a, b, titulo="Não lida")
    m2 = _criar_raiz(db_session, a, b, titulo="Lida")
    m3 = _criar_raiz(db_session, a, b, titulo="Arquivada")

    svc.marcar_lida(b.id, m2.id)
    svc.arquivar(b.id, m3.id, arquivar=True)

    assert svc.contar_nao_lidas(b.id) == 1  # apenas m1


def test_listar_retorna_apenas_raizes_com_filtros(db_session: Session):
    a = _usuario(db_session, "rem4")
    b = _usuario(db_session, "dest4")
    svc = MensagensService(db_session)

    raiz1 = _criar_raiz(db_session, a, b, titulo="Raiz 1")
    raiz2 = _criar_raiz(db_session, a, b, titulo="Raiz 2")

    svc.arquivar(b.id, raiz2.id, arquivar=True)
    svc.criar_resposta(b.id, raiz1.id, RespostaCreate(texto="resposta"))
    svc.marcar_lida(b.id, raiz1.id)

    itens, total = svc.listar_mensagens(
        b.id, StatusMensagem.TODAS, OrdemMensagem.DECRESCENTE, 1, 20
    )
    assert total == 1  # "todas" exclui arquivadas
    assert itens[0]["titulo"] == "Raiz 1"
    assert itens[0]["quantidade_respostas"] == 1

    lidas, total_lidas = svc.listar_mensagens(
        b.id, StatusMensagem.LIDAS, OrdemMensagem.DECRESCENTE, 1, 20
    )
    assert total_lidas == 1

    nao_lidas, total_nl = svc.listar_mensagens(
        b.id, StatusMensagem.NAO_LIDAS, OrdemMensagem.DECRESCENTE, 1, 20
    )
    assert total_nl == 0  # raiz1 lida e resposta é de b para a (não conta para b)

    arq_itens, total_arq = svc.listar_mensagens(
        b.id, StatusMensagem.ARQUIVADAS, OrdemMensagem.DECRESCENTE, 1, 20
    )
    assert total_arq == 1
    assert arq_itens[0]["titulo"] == "Raiz 2"


def test_marcar_lida_apenas_destinatario(db_session: Session):
    a = _usuario(db_session, "rem5")
    b = _usuario(db_session, "dest5")
    c = _usuario(db_session, "terc")
    raiz = _criar_raiz(db_session, a, b)
    svc = MensagensService(db_session)

    with pytest.raises(ForbiddenError):
        svc.marcar_lida(c.id, raiz.id)
    with pytest.raises(ForbiddenError):
        svc.marcar_lida(a.id, raiz.id)

    marcada = svc.marcar_lida(b.id, raiz.id)
    assert marcada.lida_em is not None


def test_marcar_thread_lida_marca_raiz_e_respostas(db_session: Session):
    a = _usuario(db_session, "rem6")
    b = _usuario(db_session, "dest6")
    svc = MensagensService(db_session)

    raiz = _criar_raiz(db_session, a, b, titulo="Thread")
    svc.criar_resposta(b.id, raiz.id, RespostaCreate(texto="r1"))
    svc.criar_resposta(a.id, raiz.id, RespostaCreate(texto="r2"))

    updated = svc.marcar_thread_lida(b.id, raiz.id)
    assert updated == 2  # raiz (a->b) + r2 (a->b); r1 é de b->a e não conta para b

    raiz_r = db_session.get(Mensagem, raiz.id)
    assert raiz_r.lida_em is not None


def test_arquivar_thread_somente_destinatario_da_raiz(db_session: Session):
    a = _usuario(db_session, "rem7")
    b = _usuario(db_session, "dest7")
    raiz = _criar_raiz(db_session, a, b)
    svc = MensagensService(db_session)

    with pytest.raises(ForbiddenError):
        svc.arquivar(a.id, raiz.id, arquivar=True)

    arq = svc.arquivar(b.id, raiz.id, arquivar=True)
    assert arq.arquivada_em is not None
    restaurada = svc.arquivar(b.id, raiz.id, arquivar=False)
    assert restaurada.arquivada_em is None


def test_resposta_negada_para_mensagem_de_sistema(db_session: Session):
    admin = _usuario(db_session, "adm8", role="admin")
    b = _usuario(db_session, "dest8")
    raiz = _criar_raiz(db_session, admin, b, categoria="AVISO", is_admin=True)
    svc = MensagensService(db_session)

    with pytest.raises(ForbiddenError):
        svc.criar_resposta(b.id, raiz.id, RespostaCreate(texto="não deve"))

    assert db_session.query(Mensagem).count() == 1


def test_resposta_deriva_destinatario_e_categoria_direta(db_session: Session):
    a = _usuario(db_session, "rem9")
    b = _usuario(db_session, "dest9")
    raiz = _criar_raiz(db_session, a, b)
    svc = MensagensService(db_session)

    resp = svc.criar_resposta(b.id, raiz.id, RespostaCreate(texto="oi"))
    assert resp.resposta_a_id == raiz.id
    assert resp.remetente_id == b.id
    assert resp.destinatario_id == a.id
    assert resp.categoria == "DIRETA"
    assert resp.titulo == raiz.titulo  # herda título

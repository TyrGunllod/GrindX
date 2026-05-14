"""Testes de integração do repositório de Cliente com banco SQLite."""

from app.models.cliente import Cliente
from app.repositories.cliente_repository import ClienteRepository


def _criar_cliente(db_session, **kwargs) -> Cliente:
    """Helper para criar um cliente de teste no banco."""
    dados = {
        "id": 1,
        "razao_social": "Empresa Teste Ltda",
        "cnpj": "12.345.678/0001-90",
        "ativo": True,
    }
    dados.update(kwargs)
    cliente = Cliente(**dados)
    db_session.add(cliente)
    db_session.commit()
    db_session.refresh(cliente)
    return cliente


class TestClienteRepository:

    def test_buscar_por_id(self, db_session):
        _criar_cliente(db_session, id=1)
        repo = ClienteRepository(db_session)
        resultado = repo.buscar_por_id(1)
        assert resultado is not None
        assert resultado.razao_social == "Empresa Teste Ltda"

    def test_buscar_por_id_inexistente(self, db_session):
        repo = ClienteRepository(db_session)
        assert repo.buscar_por_id(9999) is None

    def test_buscar_por_cnpj(self, db_session):
        _criar_cliente(db_session, id=1, cnpj="11.111.111/0001-11")
        repo = ClienteRepository(db_session)
        resultado = repo.buscar_por_cnpj("11.111.111/0001-11")
        assert resultado is not None

    def test_listar_com_filtro_uf(self, db_session):
        _criar_cliente(db_session, id=1, uf="SP")
        _criar_cliente(db_session, id=2, cnpj="22.222.222/0002-22", uf="RJ")
        repo = ClienteRepository(db_session)
        items, total = repo.listar(uf="SP")
        assert total == 1
        assert items[0].uf == "SP"

    def test_listar_paginado(self, db_session):
        for i in range(5):
            _criar_cliente(
                db_session,
                id=i + 1,
                razao_social=f"Empresa {i}",
                cnpj=f"0{i}.000.000/0001-0{i}",
            )
        repo = ClienteRepository(db_session)
        items, total = repo.listar(page=1, page_size=2)
        assert total == 5
        assert len(items) == 2

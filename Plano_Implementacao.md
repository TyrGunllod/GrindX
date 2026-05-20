Plano detalhado de implementação
Passo 1 — Banco (model + migração)
Criar UsuarioModulo em app/models/usuario.py como tabela de associação:
pythonclass UsuarioModulo(Base):
    __tablename__ = "usuario_modulos"
    usuario_id    = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    modulo_id     = Column(Integer, ForeignKey("portal_modulos.id"), primary_key=True)
    concedido_em  = Column(DateTime, server_default=func.now())
    concedido_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
Adicionar relationship em Usuario:
pythonmodulos_permitidos = relationship("Modulo", secondary="usuario_modulos")
Depois rodar alembic revision --autogenerate -m "add usuario_modulos".

Passo 2 — Backend: filtrar o menu por usuário
Em portal_router.py, o GET /menu hoje não exige autenticação. Vai precisar receber o current_user e filtrar:
python@router.get("/menu")
def obter_menu(current_user = Depends(get_current_user), db = Depends(get_db)):
    if current_user.role == "admin":
        abas = db.query(Aba).filter(Aba.ativo == True).order_by(Aba.ordem).all()
    else:
        # Só retorna módulos que o usuário tem permissão
        modulos_ids = db.query(UsuarioModulo.modulo_id)\
            .filter(UsuarioModulo.usuario_id == int(current_user.sub)).subquery()
        abas = (db.query(Aba)
            .join(Modulo)
            .filter(Aba.ativo == True, Modulo.id.in_(modulos_ids))
            .order_by(Aba.ordem).all())
    return abas

Passo 3 — Backend: 2 novos endpoints em usuario_router.py
GET  /v1/usuarios/{id}/modulos   → retorna lista de modulo_ids liberados
PUT  /v1/usuarios/{id}/modulos   → substitui a lista completa (body: {modulo_ids: [1,2,3]})
O PUT faz um replace completo — deleta entradas existentes e insere as novas. Simples e sem estado intermediário.
Schemas novos em app/schemas/usuario.py:
pythonclass UsuarioModulosUpdate(BaseModel):
    modulo_ids: list[int]

class UsuarioModulosResponse(BaseModel):
    usuario_id: int
    modulos: list[int]  # lista de ids

Passo 4 — Frontend: botão + modal em script.js
Na coluna de ações da tabela, adicionar um botão ao lado do editar:
javascript<button class="btn-icon" onclick="window.usersController.openPermissoes('${user.id}')" title="Permissões">
    <i class="fas fa-shield-alt"></i>
</button>
Novo método openPermissoes(id):

Busca GET /usuarios/{id}/modulos → ids já liberados
Busca GET /portal/menu (versão admin, sem filtro) → lista de todas as abas/módulos
Abre um segundo modal com checkboxes agrupados por aba
Ao salvar: PUT /usuarios/{id}/modulos com os ids marcados

O modal de permissões é separado do modal de edição — dois ReusableModal independentes no HTML.

Arquivos que serão tocados
ArquivoTipo de mudançaapp/models/usuario.py+ model UsuarioModulo + relationshipapp/models/portal.py+ relationship reversa em Moduloapp/routers/portal_router.pyGET /menu recebe auth + filtraapp/routers/usuario_router.py+ 2 endpointsapp/schemas/usuario.py+ 2 schemasalembic/versions/…nova migração (gerada automaticamente)modules/users/index.html+ modal de permissões no HTMLmodules/users/script.js+ método openPermissoes + lógica do modal
Nenhum arquivo novo de modelo ou serviço separado — tudo se encaixa no que já existe.
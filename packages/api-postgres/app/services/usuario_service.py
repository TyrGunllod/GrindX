from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from shared.security.jwt import gerar_hash_senha
from shared.exceptions.base import (
    RecursoNaoEncontradoError,
    RecursoJaExisteError
)

class UsuarioService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    def listar_usuarios(self, page: int = 1, page_size: int = 20, role: str = None):
        if role:
            return self.repo.listar_por_role(role, page, page_size)
        return self.repo.listar_todos(page, page_size)

    def buscar_por_id(self, usuario_id: int):
        usuario = self.repo.buscar_por_id(usuario_id)
        if not usuario:
            raise RecursoNaoEncontradoError(f"Usuário com ID {usuario_id} não encontrado")
        return usuario

    def criar_usuario(self, schema: UsuarioCreate):
        # Verificar duplicidade
        if self.repo.buscar_por_username(schema.username):
            raise RecursoJaExisteError(f"Username '{schema.username}' já está em uso")
        if self.repo.buscar_por_email(schema.email):
            raise RecursoJaExisteError(f"E-mail '{schema.email}' já está em uso")

        usuario = Usuario(
            username=schema.username,
            email=schema.email,
            nome_completo=schema.nome_completo,
            senha_hash=gerar_hash_senha(schema.password),
            role=schema.role,
            ativo=schema.ativo
        )
        return self.repo.criar(usuario)

    def atualizar_usuario(self, usuario_id: int, schema: UsuarioUpdate):
        usuario = self.buscar_por_id(usuario_id)
        dados = schema.model_dump(exclude_unset=True)
        
        if "password" in dados:
            dados["senha_hash"] = gerar_hash_senha(dados.pop("password"))
        
        return self.repo.atualizar(usuario, dados)

    def desativar_usuario(self, usuario_id: int):
        usuario = self.buscar_por_id(usuario_id)
        return self.repo.desativar(usuario)

"""
Guia Completo de Migrações com Alembic.

Alembic é um lightweight database migration tool para SQLAlchemy.
Fornece versionamento automático de schema e facilita updates em produção.
"""

# ============================================================================
# 1. INSTALAÇÃO
# ============================================================================

# Já está em requirements.txt:
# pip install alembic

# ============================================================================
# 2. ESTRUTURA DE DIRETÓRIOS
# ============================================================================

# alembic/
# ├── env.py                 → Configuração do ambiente
# ├── script.py.mako         → Template para novas migrations
# ├── versions/              → Histórico de migrations
# │   ├── 001_initial_schema.py
# │   ├── 002_add_campo_email.py
# │   └── ...
# └── __init__.py
#
# alembic.ini                → Configuração principal do Alembic
# manage_db.py               → CLI para executar migrations
# seed.py                    → Script para popular dados iniciais

# ============================================================================
# 3. WORKFLOW DE DESENVOLVIMENTO
# ============================================================================

# Passo 1: Modificar models em app/models/
# Exemplo: adicionar novo campo ao modelo Produto
#
# from app.models.produto import Produto
#
# class Produto(Base):
#     ...
#     novo_campo: Mapped[str] = mapped_column(String(100), nullable=True)

# Passo 2: Gerar migration automática
# python manage_db.py revision --autogenerate -m "add novo_campo to Produto"

# Passo 3: Revisar o arquivo gerado em alembic/versions/
# O Alembic detecta mudanças e cria o SQL automaticamente

# Passo 4: Aplicar a migration
# python manage_db.py upgrade head

# Passo 5: Committar no Git
# git add alembic/versions/
# git commit -m "Add novo_campo to Produto"

# ============================================================================
# 4. COMANDOS PRINCIPAIS
# ============================================================================

# UPGRADE (aplicar migrações)
# python manage_db.py upgrade head          # Aplica todas as pending
# python manage_db.py upgrade +2            # Aplica as próximas 2
# python manage_db.py upgrade 002_add_campo # Vai para essa versão específica

# DOWNGRADE (desfazer migrações)
# python manage_db.py downgrade -1          # Desfaz a última
# python manage_db.py downgrade base        # Remove todas
# python manage_db.py downgrade 001_initial # Volta para essa versão

# INFO
# python manage_db.py current               # Versão atual do banco
# python manage_db.py history               # Lista de todas as migrations
# python manage_db.py heads                 # Última migration (head)
# python manage_db.py branches              # Branches de migrations

# CREATE
# python manage_db.py revision -m "descrição"           # Migration manual
# python manage_db.py revision --autogenerate -m "desc" # Detection automática

# ============================================================================
# 5. FLUXO: DEVELOPMENT vs PRODUCTION
# ============================================================================

# DESENVOLVIMENTO:
# 1. Modificar models
# 2. python manage_db.py revision --autogenerate -m "descrição"
# 3. Revisar e testar a migration
# 4. python manage_db.py upgrade head
# 5. Testar a aplicação
# 6. Commit no Git

# PRODUÇÃO:
# 1. Pull do código com nova migration
# 2. python manage_db.py upgrade head  (aplica antes de iniciar serviço)
# 3. Iniciar aplicação
# 4. Monitorar logs
# 5. Se falhar: python manage_db.py downgrade -1

# ============================================================================
# 6. ESTRUTURA DE UMA MIGRATION
# ============================================================================

# alembic/versions/002_add_email_to_users.py
#
# """Add email to usuarios table
#
# Revision ID: 002_add_email_to_users
# Revises: 001_initial_schema
# Create Date: 2025-01-15 12:00:00
# """
# from alembic import op
# import sqlalchemy as sa
#
# revision = "002_add_email_to_users"
# down_revision = "001_initial_schema"
# branch_labels = None
# depends_on = None
#
# def upgrade() -> None:
#     """Adiciona coluna email à tabela usuarios."""
#     op.add_column(
#         "usuarios",
#         sa.Column("email", sa.String(255), nullable=False, server_default="unknown@example.com")
#     )
#     # Remove server default após população
#     op.alter_column("usuarios", "email", server_default=None)
#
# def downgrade() -> None:
#     """Remove coluna email."""
#     op.drop_column("usuarios", "email")

# ============================================================================
# 7. AUTOGENERATE vs MANUAL
# ============================================================================

# AUTOGENERATE (recomendado):
# python manage_db.py revision --autogenerate -m "add campo"
# Vantagem: Alembic detecta mudanças automaticamente
# Desvantagem: Pode não detectar tudo (ex: constrangimentos complexos)

# MANUAL:
# python manage_db.py revision -m "add campo"
# Vantagem: Controle total sobre o SQL
# Desvantagem: Mais código a escrever

# DICA: Use autogenerate e revise o arquivo gerado!

# ============================================================================
# 8. OPERAÇÕES COMUNS EM MIGRATIONS
# ============================================================================

# ADICIONAR COLUNA:
# op.add_column("tabela", sa.Column("campo", sa.String(100)))

# REMOVER COLUNA:
# op.drop_column("tabela", "campo")

# RENOMEAR COLUNA:
# op.alter_column("tabela", "nome_antigo", new_column_name="nome_novo")

# CRIAR ÍNDICE:
# op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=False)

# CRIAR RESTRIÇÃO ÚNICA:
# op.create_unique_constraint("uq_usuarios_email", "usuarios", ["email"])

# CRIAR FOREIGN KEY:
# op.create_foreign_key("fk_produtos_categoria", "produtos", "categorias", ["categoria_id"], ["id"])

# ============================================================================
# 9. SEMENTES (SEED DATA)
# ============================================================================

# Usar seed.py para popular dados iniciais:
# python seed.py

# Cria usuários e produtos de exemplo
# Útil para development e testes

# ============================================================================
# 10. BOAS PRÁTICAS
# ============================================================================

# ✓ FAZER:
#   - Usar autogenerate quando possível
#   - Revisar o SQL gerado antes de commitar
#   - Descrever bem a migration no -m "descrição"
#   - Testar upgrade E downgrade localmente
#   - Uma mudança por migration (não acumular)
#   - Commitar migrations junto com models
#   - Em produção: fazer backup antes de upgrade

# ✗ NÃO FAZER:
#   - Modificar migrations já aplicadas (cria inconsistência)
#   - Aplicar migrations sem backup em produção
#   - Esquecer de revisar o SQL autogenerate
#   - Misturar múltiplas mudanças em uma migration
#   - Deixar migrations em working directory sem commitar

# ============================================================================
# 11. TROUBLESHOOTING
# ============================================================================

# Erro: "Target database is not up to date"
# → Solução: python manage_db.py upgrade head

# Erro: "Can't locate revision identified by 'xxx'"
# → Solução: Verificar se a migration file existe em versions/

# Erro: "No such table: alembic_version"
# → Solução: Primeira vez? Execute qualquer upgrade

# Erro: Migration falhou e não dá downgrade
# → Solução: Editar a versão atual em alembic_version (último recurso!)

# ============================================================================
# 12. EXEMPLO REAL: ADICIONAR CAMPO
# ============================================================================

# 1. Adicionar ao Model:
#    class Produto(Base):
#        ...
#        sku: Mapped[str] = mapped_column(String(50), nullable=True)

# 2. Gerar migration:
#    python manage_db.py revision --autogenerate -m "add sku to produtos"

# 3. Revisar em alembic/versions/003_add_sku.py:
#    def upgrade():
#        op.add_column("produtos", sa.Column("sku", sa.String(50), nullable=True))
#
#    def downgrade():
#        op.drop_column("produtos", "sku")

# 4. Aplicar:
#    python manage_db.py upgrade head

# 5. Testar:
#    - Banco atualizado? SELECT * FROM produtos;
#    - Aplicação funciona? pytest tests/

# 6. Commitar:
#    git add alembic/versions/003_add_sku.py app/models/produto.py
#    git commit -m "Add SKU field to produtos"

# ============================================================================
# 13. DEPLOY EM PRODUÇÃO
# ============================================================================

# Dockerfile ou Script de Deploy:
#
# # 1. Pull do código novo
# git pull origin main
#
# # 2. Aplicar migrations
# python manage_db.py upgrade head
#
# # 3. Iniciar aplicação
# uvicorn app.main:app
#
# # 4. Se falhar:
# python manage_db.py downgrade -1
# git checkout HEAD~1
# python manage_db.py downgrade base  # volta para antes
# python manage_db.py upgrade head    # reaplica versão anterior

# ============================================================================

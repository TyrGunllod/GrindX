"""
Script de inicialização e configuração do Alembic.

Gera a estrutura de diretórios:
alembic/
├── env.py              → Configuração de ambiente
├── script.py.mako      → Template de migration
├── versions/           → Histórico de migrations
│   └── (arquivos .py com versionamento)
└── alembic.ini         → Configuração do Alembic

Execute: alembic init alembic
Mas este script já está configurado!
"""

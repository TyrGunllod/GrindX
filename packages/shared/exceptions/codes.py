"""
Registro centralizado de códigos de erro do ERP.

Cada código é único e segue o padrão: CATEGORIA_ACAO
Use este módulo para importar códigos em vez de hardcoding.
"""


class ErrorCode:
    """Códigos de erro padronizados para o ERP GrindX."""

    # Autenticação
    NAO_AUTORIZADO = "NAO_AUTORIZADO"
    CREDENCIAIS_INVALIDAS = "CREDENCIAIS_INVALIDAS"
    TOKEN_EXPIRADO = "TOKEN_EXPIRADO"
    TOKEN_INVALIDO = "TOKEN_INVALIDO"
    ACESSO_NEGADO = "ACESSO_NEGADO"

    # Recursos
    NAO_ENCONTRADO = "NAO_ENCONTRADO"
    CONFLITO = "CONFLITO"
    VALIDACAO_NEGOCIO = "VALIDACAO_NEGOCIO"

    # Banco de Dados
    ERRO_BANCO_DADOS = "ERRO_BANCO_DADOS"

    # Rate Limiting
    RATE_LIMIT_EXCEDIDO = "RATE_LIMIT_EXCEDIDO"

    # Upload
    ARQUIVO_INVALIDO = "ARQUIVO_INVALIDO"
    ARQUIVO_GRANDE = "ARQUIVO_GRANDE"
    TIPO_NAO_PERMITIDO = "TIPO_NAO_PERMITIDO"

    # Template
    TEMPLATE_NAO_ENCONTRADO = "TEMPLATE_NAO_ENCONTRADO"
    TEMPLATE_ERRO_CARGA = "TEMPLATE_ERRO_CARGA"
    SLUG_INVALIDO = "SLUG_INVALIDO"

    # Empresa
    EMPRESA_NAO_VINCULADA = "EMPRESA_NAO_VINCULADA"

    # Erro Interno
    ERRO_INTERNO = "ERRO_INTERNO"
    ERRO_VALIDACAO = "ERRO_VALIDACAO"

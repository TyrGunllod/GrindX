"""
Utilitários JWT compartilhados entre as APIs.

Responsável por criar, verificar e decodificar tokens JWT,
além de hashing e verificação de senhas com bcrypt.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from shared.exceptions.base import TokenExpiradoError, TokenInvalidoError
from shared.schemas.auth import TokenPayload

# Algoritmo JWT
_ALGORITHM = "HS256"


def criar_jwt(
    payload: dict,
    secret_key: str,
    expira_em: timedelta,
) -> str:
    """Gera um token JWT assinado.

    Args:
        payload: Dados a serem incluídos no token (ex: sub, role).
        secret_key: Chave secreta para assinar o token.
        expira_em: Tempo de expiração do token.

    Returns:
        Token JWT como string.
    """
    dados = payload.copy()
    expiracao = datetime.now(timezone.utc) + expira_em
    dados.update({"exp": expiracao})
    return jwt.encode(dados, secret_key, algorithm=_ALGORITHM)


def verificar_jwt(token: str, secret_key: str) -> TokenPayload:
    """Decodifica e valida um token JWT.

    Args:
        token: Token JWT a ser verificado.
        secret_key: Chave secreta usada na assinatura.

    Returns:
        TokenPayload com os dados decodificados.

    Raises:
        TokenExpiradoError: Se o token estiver expirado.
        TokenInvalidoError: Se o token for inválido ou malformado.
    """
    try:
        dados = jwt.decode(token, secret_key, algorithms=[_ALGORITHM])
        return TokenPayload(**dados)
    except JWTError as err:
        erro_str = str(err).lower()
        if "expired" in erro_str:
            raise TokenExpiradoError() from err
        raise TokenInvalidoError() from err


def gerar_hash_senha(senha: str) -> str:
    """Gera hash bcrypt de uma senha em texto plano.

    Args:
        senha: Senha em texto plano.

    Returns:
        Hash bcrypt da senha.
    """
    senha_bytes = senha.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha_bytes, salt).decode("utf-8")


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Verifica se uma senha em texto plano corresponde ao hash.

    Args:
        senha_plana: Senha em texto plano fornecida pelo usuário.
        senha_hash: Hash bcrypt armazenado no banco.

    Returns:
        True se a senha for válida, False caso contrário.
    """
    return bcrypt.checkpw(
        senha_plana.encode("utf-8"),
        senha_hash.encode("utf-8"),
    )

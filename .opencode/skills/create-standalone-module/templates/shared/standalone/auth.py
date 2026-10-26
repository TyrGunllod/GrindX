"""Identidade do standalone — sem autenticação.

Autenticação de verdade só existe dentro do GrindX (JWT). Fora dele o módulo roda
como o usuário de desenvolvimento, sem pedir credencial nenhuma: é o que deixa o
standalone utilizável para teste local, e por isso ele nunca deve ir para um
ambiente exposto.

O header opcional `X-Usuario-Id` serve só para simular outro usuário (testes de
isolamento entre usuários); sem ele, o chamador é o `USUARIO_DEV`.
"""

from dataclasses import dataclass

from fastapi import Header

# Usuário usado no standalone, onde não há autenticação.
USUARIO_DEV = 1


@dataclass(frozen=True)
class Identidade:
    """Identidade do chamador; `sub` é sempre string (id do usuário serializado)."""

    sub: str


def identidade_standalone(x_usuario_id: str | None = Header(default=None)) -> Identidade:
    valor = (x_usuario_id or "").strip()
    return Identidade(sub=valor or str(USUARIO_DEV))

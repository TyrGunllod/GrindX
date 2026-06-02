## Commit Convention

- Formato: [conventional commits](https://www.conventionalcommits.org/)
- Título: inglês (apenas o prefixo `tipo(escopo):`)
- Descrição: português (BR)
- Exemplo:
  ```
  feat(auth): adicionar validacao de login

  Adiciona validação de campos obrigatórios no formulário de login.
  ```

## Pre-commit Checklist

- Rodar `ruff format packages/ apps/` antes de commitar
- Rodar `ruff check --fix .` antes de commitar
- Rodar `ruff check .` para verificar (sem erros)
- Não commitar secrets ou chaves
- Commitar automaticamente após alterações

## Push Policy

- **Commit:** sempre após concluir uma alteração (automático)
- **Push:** somente quando o usuário solicitar explicitamente (ex: "push", "subir", "enviar")

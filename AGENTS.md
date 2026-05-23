## Commit Convention

- Formato: [conventional commits](https://www.conventionalcommits.org/)
- Título: inglês (apenas o prefixo `tipo(escopo):`)
- Descrição: português (BR)
- Exemplo:
  ```
  feat(auth): add login validation

  Adiciona validação de campos obrigatórios no formulário de login.
  ```

## Pre-commit Checklist

- Rodar linter e typecheck antes de commitar
- Não commitar secrets ou chaves
- Commitar automaticamente após alterações

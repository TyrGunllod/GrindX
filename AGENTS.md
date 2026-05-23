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

- Rodar linter e typecheck antes de commitar
- Não commitar secrets ou chaves
- Commitar automaticamente após alterações

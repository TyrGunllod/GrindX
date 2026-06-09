# Dashboard Layout & User Profile Redesign

## Objetivo

Padronizar a exibição do logo + nome da empresa no topbar e sidebar, tornar a área de logo clicável para acesso ao menu do usuário, criar uma página de perfil completa, remover botões de tema da UI global, e adicionar redirect automático ao expirar token.

## Alterações

### 1. Logo Padronizado

Substituir a estrutura de 3 partes (`G<span>RIND</span><span>X</span>`) por um logo único e simples em ambos os locais. O conteúdo será gerenciado dinamicamente pelo `skinLoader` (que já substitui via `_updateBranding`), mas sem a quebra em partes.

- **Sidebar**: elemento `.logo-grindx` → mesmo formato simples
- **Topbar**: elemento `.topbar-logo` → mesmo formato simples (atualmente não é atualizado pelo skinLoader — corrigir)

### 2. Logo Clicável — User Dropdown Unificado

Ambos os logos (sidebar e topbar) abrem um dropdown idêntico ao atual `user-pill-compact` da topbar:

```
┌──────────────────────┐
│ 👤 Nome do Usuário   │
│    Administrador     │
├──────────────────────┤
│ 👤 Meu Perfil        │ → abre módulo profile no viewport
│ 🚪 Sair              │ → logout + redirect
└──────────────────────┘
```

- Comportamento: click toggle (abre/fecha), click fora fecha
- Dropdown posicionado abaixo do logo respectivo
- Estrutura HTML/CSS reusa os estilos atuais de `.user-dropdown`

### 3. Sidebar - Remover User Pill do Footer

- Remover div `.user-pill` do `sidebar-footer`
- Manter apenas `.copyright-text`
- Ajustar CSS para padding do footer sem o user pill

### 4. Topbar - Simplificar Lado Direito

- Remover `#themeToggleTopbar`
- Remover `#userPillTopbar`
- Manter `topbar-right` vazio (para futuras adições de abas)
- Ajustar CSS se necessário

### 5. Remover Theme Toggles da UI

- Remover `#themeToggle` do `main-viewport` header
- Remover `#themeToggleTopbar` da topbar
- `updateThemeIcon()` removido (não há mais ícones de tema)
- Tema passa a ser controlado apenas via perfil do usuário

### 6. Módulo Profile (modules/profile/)

Nova página carregada no viewport como os demais módulos.

#### Estrutura:
- `modules/profile/index.html` — layout da página
- `modules/profile/script.js` — controller com lógica de carregar/salvar
- `modules/profile/style.css` — estilos específicos

#### Seções:
1. **Dados do Usuário** (read-only): nome completo, username, role
2. **Email** (editável): campo input com validação, salvo via API
3. **Alterar Senha**: campos senha atual + nova + confirmar (reusa lógica existente de change-password)
4. **Tema**: toggle light/dark (persiste em localStorage via `window.grindx.theme`)
5. **Botão Salvar**: único, envia apenas campos alterados

#### API necessária:
- `PUT /v1/auth/me` — atualizar próprio perfil (email)
- `POST /v1/auth/change-password` — já existe

### 7. Auto-logout em Token Expirado

- No `apiService.js`, interceptar responses 401:
  - Se response.status === 401, limpar sessão e redirect para `index.html`
- Excluir chamadas de login (`/auth/token`, `/auth/refresh`) do redirect — essas endpoints não usam auth header e podem retornar 401 legítimo

### 8. Backend — Novo Endpoint

**`PUT /v1/auth/me`**:
- Requer autenticação (current_user)
- Aceita `UsuarioUpdate` parcial (email, nome_completo)
- Valida se email já não está em uso por outro usuário
- Retorna `UsuarioResponse` atualizado

## Arquivos Modificados

| Arquivo | Tipo | Mudança |
|---------|------|---------|
| `apps/frontend-webapp/dashboard.html` | HTML | Logo simplificado, logo clicável, remover user-pill sidebar, remover theme toggles, remover user-pill topbar |
| `apps/frontend-webapp/dashboard.css` | CSS | Ajustes de padding/footer, estilos do dropdown do logo |
| `apps/frontend-webapp/dashboard.js` | JS | Handler click logo, remover eventos de theme toggle, remover updateThemeIcon, ajustar updateUserUI |
| `apps/frontend-webapp/shared/apiService.js` | JS | Interceptar 401 → redirect login |
| `apps/frontend-webapp/shared/skinLoader.js` | JS | Corrigir `_updateBranding` para também atualizar `.topbar-logo` |
| `apps/frontend-webapp/modules/profile/index.html` | HTML | Novo módulo |
| `apps/frontend-webapp/modules/profile/script.js` | JS | Controller do perfil |
| `apps/frontend-webapp/modules/profile/style.css` | CSS | Estilos do perfil |
| `apps/api-postgres/app/auth/router.py` | Python | Novo endpoint PUT /v1/auth/me |
| `apps/api-postgres/app/auth/service.py` | Python | Método update_profile |

## Não Escopo

- Alteração de backend para temas (preferência é apenas frontend/localStorage)
- Alteração no layout dos demais módulos
- Alteração no sistema de permissões (RBAC)
- Migrações de banco

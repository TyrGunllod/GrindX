# Design: Sistema de Inatividade do Usuário (GrindX)

**Data da Especificação:** 2026-08-15  
**Versão:** 1.0  
**Responsável:** GrindX Team

---

## 1. Objetivo
Implementar um sistema de detecção de inatividade que:
- Exiba um aviso após **60 segundos** de inatividade
- Force logout automático após **5 minutos** de inatividade contínua
- Rastreie atividade tanto no dashboard shell quanto dentro de módulos carregados em iframes
- Traduza mensagens de aviso dinamicamente conforme o idioma do usuário

---

## 2. Requisitos Funcionais

### 2.1 Detecção de Atividade
- **Eventos que redefinem o timer:**
  - Clices em qualquer elemento do dashboard shell (sidebar, topbar, formulários)
  - Movimentos do mouse
  - Teclas pressionadas (teclado)
  - Interações dentro de iframes (módulos carregados via `iframe.loading`)
- **Timer principal:** 5 minutos (300,000 ms) de inatividade antes do logout
- **Aviso intermediário:** 60 segundos de exibição do aviso antes do logout

### 2.2 Comportamento de Logout
- Ao atingir 5 minutos de inatividade:
  - Limpar `access_token` e `refresh_token` do `localStorage`
  - Limpar cache do `StorageManager`
  - Redirecionar para `/index.html` (página de login)
- Não realizar salvamento automático de dados (como solicitado, aguardando validação dos novos módulos)

### 2.3 Internacionalização
- Mensagens de aviso traduzidas via `TRANSLATIONS` (pt-BR, en-US, es-ES)
- Exemplo de tradução:
  - "Seu trabalho será salvo em 60s" → `translations['pt-BR']['warning']`

### 2.4 Tratamento de Iframes
- Listener de eventos deve ser propagado para iframes (via `window.addEventListener` ou similar)
- Cada iframe deve ter seu próprio contador de inatividade
- Quando um iframe recebe um evento de atividade, o timer global é reiniciado

---

## 3. Arquitetura Técnica

### 3.1 Componentes Principais

| Componente | Responsabilidade |
|------------|------------------|
| `InactivityTracker` | Gerencia o timer global, detecta eventos, atualiza estado |
| `SessionManager` | Manage tokens e cache de sessão (já existente) |
| `NotificationService` | Exibe aviso visual (alert/toast) com tradução |
| `LogoutHandler` | Limpa sessão e redireciona para login |

### 3.2 Fluxo de Execução

1. **Inicialização** – `InactivityTracker` é instanciado no `app.js` e escuta eventos globais
2. **Evento de Atividade** – Qualquer evento (click, keydown, mousemove) chama `resetTimer()`
3. **Timer Principal** – `setTimeout(handleTimeout, 300000)`
4. **Aviso Intermediário** – Se 60s passarem desde o último evento, mostra aviso
5. **Timeout Final** – Após 300s, limpa sessão e redireciona

### 3.3 Integração com Iframes
- Adicionar listener no `window` para capturar eventos dentro de iframes
- Alternativa: usar `postMessage` entre o host e os iframes para notificar o tracker

---

## 4. Interface do Usuário

### 4.1 Aviso Visual
- **Tipo:** Toast/Alert modal com fundo amarelo e texto centralizado
- **Texto (exemplo):** "Seu trabalho será salvo em 60s"
- **Idioma:** Traduzido via `TRANSLATIONS`
- **Ação:** Clique no aviso para ignorar (opcional) ou continuar

### 4.2 Transições
- Após 60s: exibir aviso
- Após 300s: logout automático (sem aviso adicional)

---

## 5. Considerações de Segurança

- **Proteção contra ataques de denegação:** O timer só é reiniciado por eventos legítimos (clique, tecla, movimento)
- **Limpeza de sessão:** Após logout, todos os tokens são removidos do `localStorage` e do `StorageManager`
- **Consistência:** O timer global deve ser consistente entre o host e os iframes

---

## 6. Planos de Implementação (Próximos Passos)

1. Criar classe `InactivityTracker` no `shared/app.js`
2. Adicionar listeners para eventos de ativação (clique, teclado, mousemove)
3. Implementar timer de 5 minutos com logout automático
4. Integrar tradução via `TRANSLATIONS`
5. Estender para rastreamento dentro de iframes
6. Testar em cenários reais (múltiplos iframes, diferentes idiomas)

---

## 7. Dependências

- `shared/app.js` (gerenciamento de sessão e armazenamento)
- `SessionManager` (gerenciamento de tokens)
- `TRANSLATIONS` (internacionalização)
- `StorageManager` (cache local)

---

**Próximo Passo:** Aprovar este design antes de prosseguir com a implementação. Por favor, confirme se as especificações estão corretas ou se há alguma modificação necessária.

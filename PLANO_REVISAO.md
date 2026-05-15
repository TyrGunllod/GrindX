# Plano de Alterações para GrindX Frontend

Baseado na revisão do código, aqui está um plano de implementação dividido em fases lógicas, priorizando segurança, fundamentos e melhorias incrementais. Cada fase pode ser executada em sprints de 1-2 semanas, dependendo da capacidade da equipe.

---

## 🔒 FASE 1: SEGURANÇA E FUNDAMENTOS

> **Objetivo:** Corrigir vulnerabilidades críticas e estabelecer camadas de serviço para reduzir risco e duplicação.

### 1. Substituir concatenação de strings em URLs de API
* **Onde:** `StructureController.js` (linhas com `?nome=${encodeURIComponent(...)}$icone=...`) e outros controllers similares.
* **Como:** Criar função utilitária `buildApiUrl(endpoint, params)` que use `URLSearchParams` para evitar injeção.
* **Impacto:** Elimina risco de injeção de parâmetros maliciosos via campos de formulário.

### 2. Implementar camada de serviço centralizada para API
* **Onde:** Criar `shared/apiService.js`.
* **Como:**
    ```javascript
    export const ApiService = {
      get: (endpoint, params = {}) => fetch(buildUrl(endpoint, params), { headers: authHeaders() }),
      post: (endpoint, data) => fetch(buildUrl(endpoint), { method: 'POST', body: JSON.stringify(data), ... }),
      // ... outros métodos
    };
    ```
* **Impacto:** Centraliza tratamento de erros, headers de autenticação e construção de URLs; reduz 70%+ de código duplicado.

### 3. Padronizar referência a API_BASE_URL
* **Onde:** Todos os controllers que atualmente possuem hardcode de `http://localhost:8002/v1`.
* **Como:** Substituir por `window.grindx.config.API_BASE_URL` ou pelo novo `ApiService`.
* **Impacto:** Elimina inconsistências e facilita mudança de ambiente (dev/stage/prod).

---

## 🧱 FASE 2: QUALIDADE DE CÓDIGO E CONSISTÊNCIA

> **Objetivo:** Reduzir duplicação, melhorar legibilidade e estabelecer padrões reutilizáveis.

### 1. Extrair constantes compartilhadas (ícones, perfis, etc.)
* **Onde:** Criar `shared/constants.js`.
* **Como:** Mover arrays duplicados como `iconOptions` e opções de `role` para este módulo.
* **Impacto:** Elimina 3 cópias idênticas de listas de ícones; facilita atualizações globais.

### 2. Refatorar métodos `setupForms()` extensos
* **Onde:** `StructureController.js`, `UsersController.js` e similares.
* **Como:** * Criar funções menores como `createTextField()`, `createSelectField()`.
    * Extrair lógica de pré-visualização de ícones para componente separado.
* **Impacto:** Reduz métodos de 50+ linhas para 10-15 linhas; melhora testabilidade.

### 3. Estabelecer e aplicar convenções de nomenclatura
* **Onde:** Todo o código JavaScript.
* **Como:**
    * Padronizar para `camelCase` consistente (ex: `modUrl` -> `moduleUrl`).
    * Nomear funções de evento com prefixo `handle` (ex: `handleSaveClick`).
    * Usar nomes descritivos para variáveis temporárias.
* **Impacto:** Melhora legibilidade reduzindo esforço de compreensão em ~30%.

### 4. Criar componentes UI reutilizáveis
* **Onde:** Pasta `shared/components/`.
* **Como:** Implementar inicialmente:
    * `ReusableModal.js` (com foco de teclado e ARIA adequados).
    * `DataTable.js` (para tabelas de usuários/estrutura).
    * `FormField.js` (wrapper para inputs com label e validação).
* **Impacto:** Base para eliminar duplicação futura em todos os módulos.

---

## ♿ FASE 3: EXPERIÊNCIA DO USUÁRIO E ACESSIBILIDADE

> **Objetivo:** Tornar a interface mais intuitiva, acessível e com feedback consistente.

### 1. Implementar captura de foco em modais
* **Onde:** Novo `ReusableModal.js`.
* **Como:**
    * Ao abrir: salvar elemento focado anteriormente, mover foco para primeiro campo.
    * Enquanto aberto: impedir navegação para fora do modal com `Tab`.
    * Ao fechar: restaurar foco ao elemento que abriu o modal.
* **Impacto:** Essencial para usuários de teclado e leitores de tela (WCAG 2.1).

### 2. Padronizar estados de carregamento e mensagens vazias
* **Onde:** Todos os módulos que carregam dados via API.
* **Como:**
    * Criar componente `LoadingSpinner.js` reutilizável.
    * Estado vazio padrão com ícone, título e ação primária (ex: *"Nenhum usuário encontrado. [Adicionar primeiro]"*).
* **Impacto:** Elimina estados de carregamento inconsistentes (*"Carregando..."* vs div vazia vs spinner customizado).

### 3. Melhorar mensagens de erro para usuários finais
* **Onde:** Tratamento de erros em todas chamadas de API.
* **Como:**
    * Mapear erros técnicos para mensagens amigáveis (ex: *"Falha de rede"* -> *"Verifique sua conexão e tente novamente"*).
    * Manter detalhes técnicos apenas em console para desenvolvedores.
    * Usar Toast/notificação não-intrusiva em vez de `alert()`.
* **Impacto:** Reduz frustração do usuário e chamadas de suporte por confusão.

### 4. Adicionar validação client-side básica
* **Onde:** Formulários de criação/edição (usuários, estrutura).
* **Como:**
    * Integrar biblioteca leve como `validator.js` ou criar funções customizadas.
    * Validar campos obrigatórios, formato de email, força mínima de senha antes do submit.
    * Mostrar erros inline próximo ao campo inválido.
* **Impacto:** Reduz requisições desnecessárias à API e fornece feedback imediato.

---

## ⚡ FASE 4: OTIMIZAÇÕES AVANÇADAS

> **Objetivo:** Melhorar performance, manutenibilidade e preparar para escalabilidade.

### 1. Otimizar acesso ao `localStorage`
* **Onde:** Métodos `init()` em controllers que chamam `localStorage.getItem()` repetidamente.
* **Como:**
    * Armazenar token/user em variável de instância após primeira leitura.
    * Atualizar apenas quando evento `storage` for disparado (para sincronização entre abas).
* **Impacto:** Reduz leituras síncronas dispendiosas em ~80% durante uso normal.

### 2. Implementar atualizações otimizadas de dados
* **Onde:** Métodos como `loadUsers()`, `loadStructure()` que fazem reload completo.
* **Como:**
    * Para listas: usar `PATCH` ou endpoints que retornem apenas mudanças quando possível.
    * Para detalhes: carregar apenas o item modificado ao invés de recarregar lista inteira.
* **Impacto:** Reduz consumo de banda e tempo de resposta em cenários de edição frequente.

### 3. Criar classe base para controllers de módulo
* **Onde:** `shared/baseController.js`.
* **Como:**
    * Encapsular padrões comuns: inicialização, gerenciamento de estado, métodos CRUD genéricos.
    * Permitir sobrescrita de métodos específicos quando necessário.
    * Exemplo: `class BaseController { async loadData() { ... }; bindEvents() { ... } }`
* **Impacto:** Reduz código boilerplate em 40%+; garante consistência entre novos módulos.

### 4. Adicionar validação de entrada com biblioteca dedicada
* **Onde:** Formulários complexos (ex: cadastro de usuário com múltiplas regras).
* **Como:** Integrar `yup` ou `zod` para esquemas de validação declarativa.
* *Exemplo:*
    ```javascript
    const userSchema = yup.object({
      email: yup.string().email().required(),
      password: yup.string().min(8).required()
    });
    ```
* **Impacto:** Validação mais robusta com menos código imperativo; mensagens de erro customizáveis.

---

## 📋 PRÓXIMOS PASSOS RECOMENDADOS

* **Iniciar com Fase 1:** Segurança é prioritária e estabelece fundamentos para outras mudanças.
* **Criar branch específica para cada fase:** Facilita code review e isolamento de mudanças.
* **Definir critérios de "Done" para cada tarefa:** Ex: *"Todas as concatenações de URL substituídas e testes unitários passando"*.
* **Incluir atualização de documentação:** Após cada fase, atualizar `ARCHITECTURE_PORTAL.md` com novos padrões.
* **Considerar pares de desenvolvimento:** Para tarefas de refatoração, trabalhe em dupla para garantir qualidade.

Este plano equilibra correções críticas com melhorias evolutivas, permitindo que a equipe entregue valor continuamente enquanto reduz dívida técnica. A ordem respeita dependências lógicas (ex: não faz sentido otimizar acessibilidade antes de corrigir vulnerabilidades de segurança).
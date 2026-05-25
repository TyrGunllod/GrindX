# Sub-Abas: Abas Dentro de Abas

## Data: 2026-05-25

## Problema

Atualmente a estrutura do portal tem dois níveis fixos: **Aba → Módulo**. Não é possível agrupar módulos dentro de sub-grupos em uma mesma aba, forçando o usuário a criar abas separadas para cada categoria ou listar todos os módulos em uma lista plana.

## Solução

Adicionar auto-relacionamento (`parent_id`) na tabela `portal_abas`, permitindo que uma aba contenha tanto sub-abas quanto módulos diretamente. A sidebar renderiza recursivamente e o módulo de estrutura exibe os cards aninhados.

## Abordagem Escolhida

**Abordagem 1 — `parent_id` auto-referencial na Aba** (recomendada):
- Sem tabelas novas
- Suporta N níveis de profundidade sem alteração de schema futura
- Módulos podem pertencer tanto a abas raiz quanto a sub-abas

### Descartadas

**Abordagem 2 — Nova tabela `SubAba`:** sobrecarga desnecessária de nova tabela + CRUD extra.

**Abordagem 3 — Módulos apenas em folhas:** não atende ao requisito de ter módulos em abas raiz e sub-abas.

## 1. Modelo de Dados

### `Aba` (portal.py)

```python
class Aba(Base):
    __tablename__ = "portal_abas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False)
    icone = Column(String(50), nullable=True)
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey("portal_abas.id"), nullable=True)

    parent = relationship("Aba", remote_side=[id], back_populates="children")
    children = relationship("Aba", back_populates="parent", cascade="all, delete-orphan")
    modulos = relationship("Modulo", back_populates="aba", cascade="all, delete-orphan")
```

- `parent_id = NULL` → aba raiz
- `parent_id = <id>` → sub-aba
- `Modulo` não é alterado

## 2. API (portal_router.py)

### Schema

```python
class AbaResponse(BaseModel):
    id: int
    nome: str
    icone: str
    ordem: int
    parent_id: int | None
    modulos: List[ModuloSchema]
    children: List["AbaResponse"] = []

    class Config:
        from_attributes = True
```

### Endpoints

| Método | Rota | Mudança |
|--------|------|---------|
| GET | `/v1/portal/menu` | Retorna árvore hierárquica com `children[]` |
| POST | `/v1/portal/abas` | Aceita `parent_id` opcional |
| PUT | `/v1/portal/abas/{id}` | Aceita `parent_id` opcional (permite mover) |
| DELETE | `/v1/portal/abas/{id}` | Cascade deleta children |

### Regras

- Sub-abas de abas protegidas herdam proteção contra exclusão
- Para não-admin, sub-abas sem módulos acessíveis são omitidas
- `parent_id` não pode apontar para si mesmo ou criar ciclo

## 3. Frontend — Módulo de Estrutura

### renderStructure (recursivo)

Abas raiz como cards, sub-abas como cards aninhados com `padding-left`:

```
┌─ 📁 Cadastro ──── [edit][del] ─┐
│  ┌─ 📁 Pessoas ── [edit][del] ┐│
│  │ 🔹 Clientes [edit][del]    ││
│  │ 🔹 Fornecedores [edit][del]││
│  └────────────────────────────┘│
│  ┌─ 📁 Estoque ── [edit][del] ┐│
│  │ 🔹 Produtos [edit][del]    ││
│  │ 🔹 Inventário [edit][del]  ││
│  └────────────────────────────┘│
│  🔹 Relatórios [edit][del]     │
└────────────────────────────────┘
```

### Formulários

- **Modal de Aba:** novo campo "Sub-aba de" (select opcional listando apenas abas raiz)
- **Select "Aba Destino"** do módulo: lista hierárquica com indentação (`--` ou `├──`)

### CRUD

- `saveAba`: envia `parent_id` no POST/PUT
- `deleteAba`: cascade via backend, recarrega estrutura
- `upsertAba`/`upsertModulo`: navega pela árvore recursivamente

## 4. Frontend — Sidebar (dashboard.js)

### renderSidebar (recursivo)

```html
<div class="nav-group" id="group-{id}">
  <div class="nav-title" onclick="toggleGroup('{id}')">
    <i class="{icone}"></i> {nome} <i class="chevron"></i>
  </div>
  <div class="nav-links-container">
    <!-- Sub-abas -->
    <div class="nav-subgroup" id="subgroup-{id}">
      <div class="nav-subtitle" onclick="toggleSubgroup('{id}')">
        <i class="{icone}"></i> {nome} <i class="chevron"></i>
      </div>
      <div class="nav-links-container">{modulos...}</div>
    </div>
    <!-- Módulos diretos -->
    <a class="nav-link" data-module="{slug}">{nome}</a>
  </div>
</div>
```

### Estilos (dashboard.css)

- `.nav-subgroup { padding-left: 1rem; }`
- `.nav-subtitle { font-size: 0.8rem; ... }` (mesmo padrão de collapse)
- Sidebar colapsada: sub-abas seguem mesma regra (só ícone)

## 5. Permissões e Casos de Borda

| Caso | Comportamento |
|------|---------------|
| Sub-aba sem módulos acessíveis (não-admin) | Omitida do menu |
| Exclusão de raiz com sub-abas | Cascade: deleta tudo |
| Mover aba entre níveis | PUT altera `parent_id` |
| Proteção de exclusão | Sub-abas herdam proteção da raiz |
| Sidebar colapsada | Sub-abas mostram só ícone |
| Ciclo (`parent_id` apontar para si) | Prevenido no backend |

## Arquivos Afetados

### Backend (2 arquivos)
- `packages/api-postgres/app/models/portal.py` — Adicionar `parent_id` + relationships
- `packages/api-postgres/app/routers/portal_router.py` — Ajustar schemas, queries e CRUD

### Frontend (4 arquivos)
- `packages/frontend-webapp/dashboard.js` — `renderSidebar` recursivo
- `packages/frontend-webapp/dashboard.css` — `.nav-subgroup`, `.nav-subtitle`
- `packages/frontend-webapp/modules/structure/script.js` — `renderStructure` recursivo, forms com `parent_id`
- `packages/frontend-webapp/modules/structure/style.css` — Estilos para cards aninhados
- `packages/frontend-webapp/modules/structure/index.html` — Se necessário, campo extra no modal

### Migration (1 arquivo)
- Script de migração do banco para adicionar `parent_id` column

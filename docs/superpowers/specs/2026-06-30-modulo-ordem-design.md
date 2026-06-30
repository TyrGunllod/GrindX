# Módulo Ordem — Design

> Adicionar campo `ordem` aos módulos para organização dentro das abas.

## Modelo

`apps/api-postgres/app/modules/portal/models/portal.py`

- `Modulo.ordem`: `Column(Integer, default=0)`
- `Aba.modulos`: adicionar `order_by="Modulo.ordem"` na relationship

## Migration

`012_add_modulo_ordem.py` — revises `011_add_layout_preference`

- `ALTER TABLE portal.portal_modulos ADD COLUMN ordem INTEGER DEFAULT 0 NOT NULL`
- Backfill: `UPDATE portal.portal_modulos SET ordem = id` (ordem = ID original)
- Índice: `(aba_id, ordem)` para performance

## API

`apps/api-postgres/app/routers/portal_router.py`

- `ModuloSchema` ganha `ordem: int = 0`
- POST `/v1/portal/modulos`: aceita `ordem` opcional
- PUT `/v1/portal/modulos/{modulo_id}`: aceita `ordem` opcional
- Menu response ordenado pelo `order_by` na relationship

## Frontend

`apps/frontend-webapp/modules/structure/script.js`

- Campo `modOrdem` (input number) no formulário de módulo
- Payload de criação/edição inclui `ordem`
- Listagem exibe ordem

`apps/frontend-webapp/shared/validation.js`

- `portalModulo` ganha `{ id: 'modOrdem', number: true }`

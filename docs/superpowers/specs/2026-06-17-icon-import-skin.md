# Importação de Fonte de Ícones no Módulo de Skins

## Problema

O módulo de skins permite importar fontes customizadas (heading/body) mas não oferece suporte a fontes de ícones. A coluna `icon_library` existe no banco mas é hardcoded como `'fontawesome'` e não tem UI.

## Escopo

Adicionar upload de arquivo de fonte de ícones (.woff2/.ttf/.woff/.otf) no form de edição de skin, abaixo da seção de importação de fonte customizada. Reutiliza lógica existente de upload de fontes com um único endpoint unificado.

## Itens de Trabalho

### 1. Endpoint único `POST /v1/themes/fonts-icons/upload`

Unifica o upload de fontes (texto e ícones) em um único endpoint. Aceita `multipart/form-data` com:
- `file`: arquivo .woff2/.woff/.ttf/.otf
- `type`: `"font"` ou `"icon"` (define diretório de destino)

Valida magic bytes (`filetype` library). Salva em `uploads/fonts/` ou `uploads/icons/`.

### 2. Modelo — campo `fonts.icons`

O JSON `fonts` da `CompanyTheme` passa a aceitar:

```json
{
  "heading": "Barlow Condensed",
  "body": "DM Sans",
  "custom": [...],
  "icons": {
    "name": "Material Icons",
    "url": "/uploads/icons/uuid.woff2",
    "format": "woff2"
  }
}
```

### 3. UI — upload de ícones no admin-skins

No `admin-skins/index.html`, abaixo da seção "Importar Fonte Customizada", adicionar seção "Importar Fonte de Ícones":
- Input de nome para a fonte de ícones
- File input aceitando .woff2/.ttf/.woff/.otf
- Preview do nome após upload
- Botão remover

### 4. Aplicação — `skinLoader.js`

Novo método `_applyIconFont(fonts)` que:
- Injeta `@font-face` no `<head>` para a fonte de ícones
- Define `--skin-font-icons: '<name>'` como variável CSS

### 5. Iframe — `dashboard.js`

Injetar a `@font-face` de ícones nos iframes dos módulos, seguindo o mesmo padrão das fontes customizadas.

## Não Escopo

- Catálogo de bibliotecas de ícones (Font Awesome, Material Icons, etc.)
- Preview visual dos glifos da fonte de ícones
- Upload de múltiplos arquivos
- Remoção do Font Awesome (coexiste com a fonte customizada)

# CHANGELOG

<!-- version list -->

## v1.4.1 (2026-05-23)

### Bug Fixes

- **skin**: Apply font changes on save and preview
  ([`3bc2649`](https://github.com/TyrGunllod/GrindX/commit/3bc26492c83cad1c8695a5fc247ed6ef6456a59d))


## v1.4.0 (2026-05-23)

### Features

- **skins**: Adicionar mais opções de fontes no editor de skins e corrigir carregamento de fontes
  ausentes no FONT_CDN_MAP
  ([`d1d22bc`](https://github.com/TyrGunllod/GrindX/commit/d1d22bc4a7237a9ac6cf2dbb78cc7765e8cc4d71))


## v1.3.0 (2026-05-22)

### Bug Fixes

- _loadIconLibrary nao remove mais links FA estaticos
  ([`c1ef01f`](https://github.com/TyrGunllod/GrindX/commit/c1ef01fe092173a74d1e288ebc9afb513812b572))

- ActivateSkin notifica parent ao ativar skin
  ([`eefad9e`](https://github.com/TyrGunllod/GrindX/commit/eefad9e71e88c4bd86515890db8daebd469626f2))

- Adiciona prefixo 'fas ' nos valores do mapeamento de icones
  ([`ed11830`](https://github.com/TyrGunllod/GrindX/commit/ed118309469ef1aa22fb62822ab68e78250e3988))

- Admin-skins agora atualiza icones da propria pagina ao trocar biblioteca
  ([`a09cf44`](https://github.com/TyrGunllod/GrindX/commit/a09cf449db0b7186247e9f56d7b18dd220712484))

- Aplica variaveis CSS da skin nos modulos (iframe)
  ([`263b8cf`](https://github.com/TyrGunllod/GrindX/commit/263b8cf99a6931ff6e1239ea433ab979053d8170))

- Atualiza sidebar ao salvar icone de aba/modulo
  ([`9ea94fa`](https://github.com/TyrGunllod/GrindX/commit/9ea94fa7234527e1f94495a6afeb354c744d9008))

- Carrega LoadingSpinner.js no admin-skins para toasts funcionarem
  ([`6e57bc4`](https://github.com/TyrGunllod/GrindX/commit/6e57bc446af41b91bf0a6fefc6b39c4c10288411))

- Carrega recursos Lucide/Material no iframe para renderizar icones
  ([`bdee3b4`](https://github.com/TyrGunllod/GrindX/commit/bdee3b44ad370f5a7862ed420e37d116a38f3596))

- Fallback generico para icones FA nao mapeados em _replacePageIcons
  ([`7c126d3`](https://github.com/TyrGunllod/GrindX/commit/7c126d330dcadc291c5beaf97d337c0d3eb10016))

- Layout do modal de edicao de aba e remocao do X
  ([`b195e4b`](https://github.com/TyrGunllod/GrindX/commit/b195e4b066fdcaa1ee2c9e9591b8fbcb2cb1ae06))

- Modulos de estrutura e usuarios convertem icones via grindx.icons.convertAll()
  ([`dbef800`](https://github.com/TyrGunllod/GrindX/commit/dbef800dddbc04199d04171818c9553ea77a1095))

- Notifica dashboard ao salvar skin para recarregar sidebar e icones
  ([`9d6f50d`](https://github.com/TyrGunllod/GrindX/commit/9d6f50d19e43633e3d8ee0afef4c3d14587870f2))

- Recarrega pagina apos salvar skin para aplicar alteracoes
  ([`395b7ae`](https://github.com/TyrGunllod/GrindX/commit/395b7ae9d22c5c93b63c13ab6750e6ac25d4f5fe))

- Recarrega parent ao salvar/ativar skin em vez de postMessage
  ([`37e0493`](https://github.com/TyrGunllod/GrindX/commit/37e0493aad286888530ba10d1a7235e5f86a1088))

- Remove chave extra que causava SyntaxError no setupEvents
  ([`512716f`](https://github.com/TyrGunllod/GrindX/commit/512716f3b67c21b6e29e1b12e5b906b61025365f))

- Seletor de icone em abas/modulos respeita biblioteca da skin ativa
  ([`020a5b2`](https://github.com/TyrGunllod/GrindX/commit/020a5b2f6ea5f2ad9f2fe8f81ede529036f2553e))

- Sidebar agora atualiza icones conforme biblioteca selecionada
  ([`ab19cac`](https://github.com/TyrGunllod/GrindX/commit/ab19cac01ef6d7f417597e07bb7adaa632d7c0eb))

- Tema escuro nao era aplicado nos modulos (iframe)
  ([`460bbfe`](https://github.com/TyrGunllod/GrindX/commit/460bbfe01f6620501744077bf15d3bb2a4d2f917))

- **admin-skins**: Adiciona import do baseController.js para corrigir cards sumindo
  ([`4d98916`](https://github.com/TyrGunllod/GrindX/commit/4d98916c0f6a7857b2d7b68cfa776ce03455437c))

- **admin-skins**: Carrega Font Awesome e corrige caminho do dashboard no botao Testar
  ([`22989e8`](https://github.com/TyrGunllod/GrindX/commit/22989e8a489f7ce2a7c0320ffa88a7a2521e20d1))

- **admin-skins**: Preview agora reflete biblioteca de icones selecionada
  ([`ec2110a`](https://github.com/TyrGunllod/GrindX/commit/ec2110ac45bea23e2d60a1c0765b1836fb3b2cd8))

- **admin-skins**: TogglePreviewTheme agora usa variaveis semanticas em vez de --skin-*
  ([`68a163b`](https://github.com/TyrGunllod/GrindX/commit/68a163b63d233ba096cc37fb06534241d51b35fa))

- **admin-skins,dashboard**: Usa variaveis CSS semanticas para dark/light mode
  ([`e808289`](https://github.com/TyrGunllod/GrindX/commit/e808289be7b208a361370621973edc271ede4ed9))

- **api**: Corrige create_theme_from_template para receber body JSON em vez de query params
  ([`94b53eb`](https://github.com/TyrGunllod/GrindX/commit/94b53eb254cabf2883ea9d03af0978e9bda777a7))

- **api**: Corrige diretorio de upload do logo para evitar 404
  ([`6ae9b4e`](https://github.com/TyrGunllod/GrindX/commit/6ae9b4eab124f31270582fe93921579137f2d2b0))

- **dashboard**: Centraliza logo e nome da empresa verticalmente no sidebar
  ([`9d76d35`](https://github.com/TyrGunllod/GrindX/commit/9d76d35c8dbcf415b9287e3a683eb6104660e33b))

- **frontend**: Corrige escaping de aspas nos onerror do preview do logo
  ([`5203bcb`](https://github.com/TyrGunllod/GrindX/commit/5203bcb2bdd671ab9aa08f0f90796e92e19aa442))

- **frontend**: Resolve URL relativa do logo usando API_BASE_URL
  ([`97862a0`](https://github.com/TyrGunllod/GrindX/commit/97862a0f850a35485905c1bdaf153ffe001268aa))

- **seed**: Vincula todos os usuarios sem empresa a GrindX
  ([`401ba92`](https://github.com/TyrGunllod/GrindX/commit/401ba92501e783d47cff1dfff63bb67319417e34))

- **skin-loader**: Fallback para texto quando logo nao encontrada (404)
  ([`068d520`](https://github.com/TyrGunllod/GrindX/commit/068d520d34e0bdf0f478d8c0d98ecf45305bedb1))

- **skins**: Aumentar margem vertical da barra de rolagem para nao sobrepor cantos arredondados
  ([`217e8d2`](https://github.com/TyrGunllod/GrindX/commit/217e8d21d1bd666feab093b3a6de88eca698a330))

- **theme**: Corrige imports e teste de criação a partir de template
  ([`5927839`](https://github.com/TyrGunllod/GrindX/commit/592783927842b605718fc4126e4e3b7e525d3610))

- **ui**: Alterar scrollbar global para valor initial
  ([`57a007e`](https://github.com/TyrGunllod/GrindX/commit/57a007efb8f6822da2c4c420d8abe73d9d2a9f12))

- **usuarios**: Vincula novo usuario a empresa do admin que o criou
  ([`058f99c`](https://github.com/TyrGunllod/GrindX/commit/058f99c29bbf87ece1760bf54938180200fa2fd1))

### Chores

- Remove listener message obsoleto (skin agora recarrega parent)
  ([`dbea635`](https://github.com/TyrGunllod/GrindX/commit/dbea635bcd8dd44b1bee1b9c3fabdf7e980e99b2))

### Code Style

- **skins**: Reduzir largura da barra de rolagem no modal de edição de temas
  ([`5485d92`](https://github.com/TyrGunllod/GrindX/commit/5485d92b0213e169ace0093c5a6cae6cfc04b437))

- **theme**: Aplica formatação ruff em theme_router.py
  ([`f6402a9`](https://github.com/TyrGunllod/GrindX/commit/f6402a9d19fc670d9e00fa3648f179bc8b6de194))

### Features

- Adiciona grindx.icons.convert() para converter icones FA em qualquer modulo
  ([`68f2fc4`](https://github.com/TyrGunllod/GrindX/commit/68f2fc4037d9fd741d8ef9a3387044584877731c))

- Seletor de icone visual em grid no lugar de dropdown de texto
  ([`9655c52`](https://github.com/TyrGunllod/GrindX/commit/9655c528cc4a52982e2fcde87cf12c9cb56e0cea))

- **admin-skins**: Adiciona feedback toast ao salvar, ativar e excluir skins
  ([`0186e49`](https://github.com/TyrGunllod/GrindX/commit/0186e49cd803cb277780d25f776afa2db5da9b37))

- **gestao**: Impedir deleção de módulos criados na aba Gestão
  ([`6ad6313`](https://github.com/TyrGunllod/GrindX/commit/6ad6313bac1e65c8d02cbaeb6fc26ed8591e02ec))

- **sidebar**: Altera ícone do avatar conforme perfil do usuário
  ([`151a0f7`](https://github.com/TyrGunllod/GrindX/commit/151a0f7af7be86cd5da0a5084e228d9778d29651))

- **skin-loader**: Exibe nome da empresa ao lado do logo quando sidebar expandida
  ([`ee4c9b1`](https://github.com/TyrGunllod/GrindX/commit/ee4c9b1d983e31c51aea9ce21bc51570595554a9))

- **ui**: Aplicar scrollbar fina globalmente em todos os elementos
  ([`4836ff4`](https://github.com/TyrGunllod/GrindX/commit/4836ff4b8f7eec8390198067b988bf79248ed3ef))

### Refactoring

- Remove bibliotecas Lucide/Material, usa apenas Font Awesome
  ([`2361e2f`](https://github.com/TyrGunllod/GrindX/commit/2361e2f94bf184d734991689faf0eb1bcc9bd34d))

- **admin-skins**: Remove campos de url alternativa de logo e simplifica upload
  ([`f52310c`](https://github.com/TyrGunllod/GrindX/commit/f52310c616c3e85161611c74dae3f29ad4f95e22))


## v1.2.0 (2026-05-22)

### Bug Fixes

- Ajuste do comando make dev-all
  ([`46905ff`](https://github.com/TyrGunllod/GrindX/commit/46905ff987b59938e7d3ca22224f791548b25dd1))

- Apply theme class to :root and sync iframe documentElement
  ([`25ae360`](https://github.com/TyrGunllod/GrindX/commit/25ae360852dfcbb08301b9aaba0874f1facc862a))

- **skins**: Corrige warnings de cor rgba em input type color
  ([`00751f3`](https://github.com/TyrGunllod/GrindX/commit/00751f35c0f892e56b2416929686aac79fbf3fc1))

### Features

- **seed**: Adiciona skin padrao GrindX no seed
  ([`605c91a`](https://github.com/TyrGunllod/GrindX/commit/605c91a8cbce8bf4642c73dc4d1e4320c4f77bfe))

- **skins**: Substitui botoes por cards no grid e corrige retorno da API sem empresa
  ([`2c97b84`](https://github.com/TyrGunllod/GrindX/commit/2c97b84d18b58fc9e5f8c20c4b8c74099b5d6561))


## v1.1.1 (2026-05-22)


## v1.1.0 (2026-05-22)

### Bug Fixes

- Corrigir import do fastapi-limiter e organizar imports no usuario_router
  ([`817c67e`](https://github.com/TyrGunllod/GrindX/commit/817c67e3417c70e770ab765618628015f87a415e))

- Remover dependencia de pyrate-limiter (API incompativel)
  ([`085b7db`](https://github.com/TyrGunllod/GrindX/commit/085b7db9d533ab4aa85f2618f7c9d6e4075b19f9))

- **api-postgres**: Adicionar guard de ambiente no seed.py
  ([`69d0f71`](https://github.com/TyrGunllod/GrindX/commit/69d0f71105121dd98920e08c8731d1610b6031ea))

- **api-postgres, api-sqlserver**: Usar CORS_ORIGINS do .env em vez de lista hardcoded
  ([`46cc430`](https://github.com/TyrGunllod/GrindX/commit/46cc4301d88a983dc4d1e7deb7669ecc580239a6))

- **config**: Validar comprimento minimo da SECRET_KEY
  ([`07f9e5a`](https://github.com/TyrGunllod/GrindX/commit/07f9e5ada27544b5b39308932f2fe68b414f6bcc))

- **frontend**: Detectar host dinamicamente no apiService
  ([`422654a`](https://github.com/TyrGunllod/GrindX/commit/422654a5667618abfbad8db921f197b33365210e))

- **infra**: Bind explicito 0.0.0.0 nos containers do podman-compose
  ([`211a78d`](https://github.com/TyrGunllod/GrindX/commit/211a78df43d6d6dc81eb2215bdf997b2e25b335c))

- **middleware**: Tornar RateLimitMiddleware thread-safe com asyncio.Lock
  ([`72f336e`](https://github.com/TyrGunllod/GrindX/commit/72f336e844c056f7b722e9c94163d3de7a1e45ed))

### Chores

- **config**: Separar .env de dev e producao
  ([`b815bc1`](https://github.com/TyrGunllod/GrindX/commit/b815bc1e85ed273105b2aef6d5829f04511fb702))

- **makefile**: Adicionar target dev-all para subir todos os servicos
  ([`d6f01cc`](https://github.com/TyrGunllod/GrindX/commit/d6f01cc2a87a32ac3edaed43164e50cc04c233f4))

### Features

- **auth**: Adicionar logs de auditoria em acoes criticas
  ([`2c13d3f`](https://github.com/TyrGunllod/GrindX/commit/2c13d3f652319c311c158007e1ae5cba18f6c0e7))

- **config**: Adicionar propriedade allowed_origins_list em api-sqlserver
  ([`a33a128`](https://github.com/TyrGunllod/GrindX/commit/a33a1289258ac0526c177c0134c6d4c4098cfd71))

- **frontend**: Injetar URL da API via GRINDX_CONFIG no deploy
  ([`b27d5be`](https://github.com/TyrGunllod/GrindX/commit/b27d5beb5bcf2f3007710b2e22bf62b0c40a7763))

- **infra**: Adicionar configuracao Nginx como reverse proxy
  ([`ecf7711`](https://github.com/TyrGunllod/GrindX/commit/ecf7711d100c437d8760865c8fae5b729de8046c))

- **makefile**: Expor servicos na rede com --host 0.0.0.0
  ([`8adc57d`](https://github.com/TyrGunllod/GrindX/commit/8adc57dfe070fd0f676b3b5bd53bbf99a7e6723c))

- **middleware**: Adicionar Content-Security-Policy no SecurityHeadersMiddleware
  ([`92d5ff8`](https://github.com/TyrGunllod/GrindX/commit/92d5ff893e5da1d75c55e59913d882a6dc95dcf7))

- **middleware**: Adicionar suporte a rate limiter distribuido com Redis
  ([`664bb5a`](https://github.com/TyrGunllod/GrindX/commit/664bb5acdd508d114448229f8818704aa871e9f2))

### Refactoring

- **api-postgres, api-sqlserver**: Eliminar injecao dupla de get_current_user
  ([`b31fd5e`](https://github.com/TyrGunllod/GrindX/commit/b31fd5e2860b2ec3a15eda17ce779e412eac21be))

### Testing

- Adicionar testes de contrato entre api-postgres e api-sqlserver
  ([`ab82d6e`](https://github.com/TyrGunllod/GrindX/commit/ab82d6ee6f74cb3b4b123699f7de894dc1a76c96))


## v1.0.0 (2026-05-21)

- Initial Release

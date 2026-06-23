# CHANGELOG

<!-- version list -->

## v1.34.4 (2026-06-23)

### Bug Fixes

- **import**: Frontend folder removal now uses startswith(module_name)
  ([`c81dde5`](https://github.com/TyrGunllod/GrindX/commit/c81dde511afe02c15f3924dd3f4bc97e99558006))


## v1.34.3 (2026-06-23)

### Bug Fixes

- **deploy**: Replace chown 1001:1001 with chmod 777 for rootless podman
  ([`1e271d5`](https://github.com/TyrGunllod/GrindX/commit/1e271d5159d3e1dbda0d13dde49679f53409abdc))


## v1.34.2 (2026-06-23)

### Bug Fixes

- Copy frontend PermissionError now raises; deploy chown 1001:1001
  ([`0d42d03`](https://github.com/TyrGunllod/GrindX/commit/0d42d03700165175ea3daeee9047e0e51a0eeba0))


## v1.34.1 (2026-06-23)

### Bug Fixes

- **api-postgres**: Handle IntegrityError on POST /v1/portal/modulos
  ([`49b9b5b`](https://github.com/TyrGunllod/GrindX/commit/49b9b5b35896f9a0c56c15db2fafd2231cfa2b56))

### Documentation

- **skill**: Add sqlserver support to create-standalone-module
  ([`666ccc2`](https://github.com/TyrGunllod/GrindX/commit/666ccc24510add681950cf35e6840337eb7b666c))


## v1.34.0 (2026-06-23)

### Documentation

- Document sqlserver module import with target_api
  ([`1f4b4e9`](https://github.com/TyrGunllod/GrindX/commit/1f4b4e9c8f52571b9d60d2cbcd87071496e573c1))

- **spec**: Cria especificacao para import de modulos no api-sqlserver
  ([`6dabcc6`](https://github.com/TyrGunllod/GrindX/commit/6dabcc67aa54cc9a2b02ef80647fc40487e74c5a))

### Features

- **import**: Add --target-api CLI and conditional flow for api-sqlserver
  ([`865d655`](https://github.com/TyrGunllod/GrindX/commit/865d65536adcf0ca37df4e5832b7e28859cda92f))

- **import**: Add _get_sqlserver_api_dir() and target_api manifest field
  ([`2e14115`](https://github.com/TyrGunllod/GrindX/commit/2e1411563544dd0752c341b4bde9456ddd29a573))

- **import**: Add register_router_sqlserver() for api-sqlserver main.py
  ([`0cc3495`](https://github.com/TyrGunllod/GrindX/commit/0cc3495c3c0a5f035c13394c151f351f43f1febf))

- **import**: Pass target_api from module.json to import subprocess
  ([`00c13c1`](https://github.com/TyrGunllod/GrindX/commit/00c13c18047ea947305420027e233e5507bc92e0))


## v1.33.7 (2026-06-23)

### Bug Fixes

- **makefile**: Use sudo rm -rf no deploy para arquivos de UIDs diferentes
  ([`9c76b98`](https://github.com/TyrGunllod/GrindX/commit/9c76b98b505a3d3fbfa27da436cf427b4a757c0c))


## v1.33.6 (2026-06-23)

### Bug Fixes

- **compose**: Revert api-postgres to user 1001:1001
  ([`cc8328d`](https://github.com/TyrGunllod/GrindX/commit/cc8328d4a1230ef5e476d0e6a16748919b54ff84))


## v1.33.5 (2026-06-23)

### Bug Fixes

- **compose**: Run api-postgres as root (0:0) to write bind mounts on WSL
  ([`b214d6e`](https://github.com/TyrGunllod/GrindX/commit/b214d6ec3e7afbf1477f88cb62695070ac420793))


## v1.33.4 (2026-06-23)

### Bug Fixes

- **import**: Handle PermissionError on bind-mount backup and frontend dirs
  ([`4bd0caf`](https://github.com/TyrGunllod/GrindX/commit/4bd0caf469d6d4d4f949b52a9ea670a88740237e))


## v1.33.3 (2026-06-23)

### Bug Fixes

- **import**: Stream subprocess output in real-time to diagnose hang
  ([`0ab3794`](https://github.com/TyrGunllod/GrindX/commit/0ab37944c21315332308fea29c139a85c090e58f))


## v1.33.2 (2026-06-23)

### Bug Fixes

- **import**: Add 60s timeout and timing logs to diagnose hang
  ([`db71752`](https://github.com/TyrGunllod/GrindX/commit/db7175205f15df7d89a6351eea48d6697bb01564))


## v1.33.1 (2026-06-23)

### Bug Fixes

- **a11y**: Add autocomplete attribute to forgotUsername field
  ([`66c0571`](https://github.com/TyrGunllod/GrindX/commit/66c057107b320f747782b71faf270d34e1e9e60b))

- **import**: Add 25s timeout to import endpoint to prevent browser timeout
  ([`d048827`](https://github.com/TyrGunllod/GrindX/commit/d048827b37eb43dae992b119ebebad2fe1bd4a7a))

- **import**: Run migrations as background thread to prevent HTTP timeout
  ([`4c92087`](https://github.com/TyrGunllod/GrindX/commit/4c92087a1bd80797ac48e101c05f3dee6471bcbd))

- **sqlserver**: Lazy engine creation to prevent import timeout
  ([`cd36d63`](https://github.com/TyrGunllod/GrindX/commit/cd36d636497d47c2c8afc87486c53d2439cd354d))

### Code Style

- Ruff format database.py
  ([`5fe28ac`](https://github.com/TyrGunllod/GrindX/commit/5fe28ace061c8ca21ce1c732e53babcd5b97acc1))

### Documentation

- Add ruff format to pre-push checklist in AGENTS.md
  ([`099a700`](https://github.com/TyrGunllod/GrindX/commit/099a7004510d6487a172477cf9b093d602f34d13))


## v1.33.0 (2026-06-23)

### Features

- **docker**: Enable uvicorn --reload in sqlserver container
  ([`803cbb3`](https://github.com/TyrGunllod/GrindX/commit/803cbb3835d533f4594060761516db88c1520ddf))


## v1.32.13 (2026-06-23)

### Bug Fixes

- **docker**: Install msodbcsql17 instead of msodbcsql18
  ([`8b50b1a`](https://github.com/TyrGunllod/GrindX/commit/8b50b1ad712ba8ba1ed76176639fa9d249e71284))

- **sqlserver**: Simplify health check and fix import order
  ([`a77fab2`](https://github.com/TyrGunllod/GrindX/commit/a77fab246a76986d942689ddcd4ace4b1cea4586))

- **swagger**: Exclude docs paths from CSP to enable Swagger UI rendering
  ([`57b9e62`](https://github.com/TyrGunllod/GrindX/commit/57b9e624666c4768f3f0a9fab91c58f0c2ba6ba4))

- **tests**: Recreate tests/unit dir for api-sqlserver
  ([`97525c0`](https://github.com/TyrGunllod/GrindX/commit/97525c09319ffe5c489b0ae07010b04da9a3ab79))

### Refactoring

- **sqlserver**: Remove all endpoints except healthcheck
  ([`2b27e86`](https://github.com/TyrGunllod/GrindX/commit/2b27e862638b28830c0cec7be61243d676816d19))


## v1.32.12 (2026-06-23)

### Bug Fixes

- **admin-skins**: Corrige endpoint font upload, adiciona requireAuth e apiService
  ([`f3fb07f`](https://github.com/TyrGunllod/GrindX/commit/f3fb07ff6665ef2782eecc535546bfb7ebbb4309))

### Documentation

- Atualiza documentacao com WSL, CSP, volumes PWD e deploy
  ([`25d31e7`](https://github.com/TyrGunllod/GrindX/commit/25d31e7308b519de1371c1e14e0e95bebcd54e38))


## v1.32.11 (2026-06-23)

### Bug Fixes

- Deploy remove modules antes de copiar para evitar aninhamento
  ([`c8ab56f`](https://github.com/TyrGunllod/GrindX/commit/c8ab56ff6019d66e00dcf6f9fa10ceffd66109e6))


## v1.32.10 (2026-06-23)

### Bug Fixes

- Make deploy copia modules e compose usa PWD portatil
  ([`0f71354`](https://github.com/TyrGunllod/GrindX/commit/0f71354634f0985b1902afa962149d8e46121653))


## v1.32.9 (2026-06-23)

### Bug Fixes

- Corrige paths dos volumes para usar HOME no WSL
  ([`69dc92b`](https://github.com/TyrGunllod/GrindX/commit/69dc92b1939eb687ebaedb71c2f4c7052106f2d6))


## v1.32.8 (2026-06-22)

### Bug Fixes

- Corrige CSP, requireAuth no importer e inclui config.js nos modulos
  ([`8e50e57`](https://github.com/TyrGunllod/GrindX/commit/8e50e57de79e360ce380810ab5b10c8c9f34414a))


## v1.32.7 (2026-06-22)

### Bug Fixes

- **infra**: Corrigir template de path dos volumes no compose
  ([`719661e`](https://github.com/TyrGunllod/GrindX/commit/719661e35484138f700bec2df2d66054bb3487d3))


## v1.32.6 (2026-06-22)

### Bug Fixes

- **infra**: Restaurar prefixo localhost/ nas image tags do compose
  ([`c99543c`](https://github.com/TyrGunllod/GrindX/commit/c99543c38efe789573735ad305749d18f7f083a9))


## v1.32.5 (2026-06-22)

### Bug Fixes

- **infra**: Remover prefixo localhost/ das image tags no compose
  ([`ad79fd7`](https://github.com/TyrGunllod/GrindX/commit/ad79fd786d922f2fbcb0ec99c3685feffcc211b0))


## v1.32.4 (2026-06-22)

### Bug Fixes

- **infra**: Remover build contexts do compose, manter apenas image tags
  ([`dd8f326`](https://github.com/TyrGunllod/GrindX/commit/dd8f3260f9ccda519d8717ed2a18fda12582c18c))


## v1.32.3 (2026-06-22)

### Bug Fixes

- **infra**: Criar diretorios de source no deploy
  ([`29115e3`](https://github.com/TyrGunllod/GrindX/commit/29115e3d50094508fb0dcd5ba339bb167f523ba9))

- **infra**: Remover volumes do deploy, copiar nginx.conf para source
  ([`c1c34e5`](https://github.com/TyrGunllod/GrindX/commit/c1c34e55b7672fc4d194136e19f8475c6118bb49))


## v1.32.2 (2026-06-19)

### Bug Fixes

- **infra**: Adicionar image tags ao compose.yaml e tag latest ao make images
  ([`8fb0bd1`](https://github.com/TyrGunllod/GrindX/commit/8fb0bd19deb61db6439a2a614f82372228aba69b))


## v1.32.1 (2026-06-19)

### Bug Fixes

- **infra**: Tornar copia de .env.postgres/.sqlserver opcional no deploy
  ([`9e9f65f`](https://github.com/TyrGunllod/GrindX/commit/9e9f65f84789cf24e1328197676d5f7ac3fa4a14))


## v1.32.0 (2026-06-19)

### Features

- **infra**: Incluir .env.example renomeados no make deploy
  ([`6647e35`](https://github.com/TyrGunllod/GrindX/commit/6647e3540352120a5331359ddc6e4dda9551ac2d))


## v1.31.0 (2026-06-19)

### Features

- **infra**: Adicionar subdiretorios uploads/logos, fonts, icons ao make volumes
  ([`f494d59`](https://github.com/TyrGunllod/GrindX/commit/f494d597047eece18b2c3c9736cf3184e39619d1))


## v1.30.0 (2026-06-19)

### Documentation

- Revisar AGENTS.md e corrigir path de exportacao
  ([`848cdb2`](https://github.com/TyrGunllod/GrindX/commit/848cdb2b93810532809b372e5e6059368ca09839))

### Features

- **infra**: Unificar paths de volumes e imagens fora do projeto
  ([`f9cdb4a`](https://github.com/TyrGunllod/GrindX/commit/f9cdb4afbfada617008d5699ab710c21802c6c8e))


## v1.29.0 (2026-06-19)

### Features

- **infra**: Adicionar make venv e exportacao de imagens tar
  ([`cc52813`](https://github.com/TyrGunllod/GrindX/commit/cc528136d51c85b36fbd6dfe3740e255c5e88040))


## v1.28.1 (2026-06-19)

### Bug Fixes

- **infra**: Extrair versao via script para compatibilidade Windows
  ([`33ea0d1`](https://github.com/TyrGunllod/GrindX/commit/33ea0d16255bbd0e736255fd5db547c3a17cb7f9))


## v1.28.0 (2026-06-19)

### Features

- **infra**: Adicionar make images e make deploy
  ([`f6bc57c`](https://github.com/TyrGunllod/GrindX/commit/f6bc57c546245d21c99b08ebc4414d6987cc2a6d))


## v1.27.0 (2026-06-19)

### Bug Fixes

- **infra**: Corrigir upstream api-postgres para localhost no nginx.conf
  ([`deb9cf9`](https://github.com/TyrGunllod/GrindX/commit/deb9cf9a9ad670d0031bd36881c85a89848ab542))

- **scripts**: Corrigir recursao infinita em _get_api_dir e _get_frontend_dir
  ([`c7b962b`](https://github.com/TyrGunllod/GrindX/commit/c7b962b3e9b64ce41a9909331e5b08098edf6b4e))

### Features

- **infra**: Suporte a importacao de modulos no container
  ([`9f17fed`](https://github.com/TyrGunllod/GrindX/commit/9f17fed0bd24943c335bb158508e150a6e2654c8))

### Refactoring

- **infra**: Centralizar volumes em Containers/volumes/grindx
  ([`eb93cf0`](https://github.com/TyrGunllod/GrindX/commit/eb93cf0fa14801c8c75cd1e81a713a0a0ce0d55f))


## v1.26.3 (2026-06-18)

### Bug Fixes

- **infra**: Mover todos os arquivos de versao para version_variables
  ([`aef4ddc`](https://github.com/TyrGunllod/GrindX/commit/aef4ddc8052413c18e1e5584d3e30538737e5a9c))


## v1.26.2 (2026-06-18)

### Bug Fixes

- **infra**: Corrigir volumes .env trocados no compose.yaml
  ([`81cc416`](https://github.com/TyrGunllod/GrindX/commit/81cc41695c86b54e94cd69eae4fac3bc82c8eb5e))

### Chores

- **infra**: Remover compose.yaml.old do tracking
  ([`a935479`](https://github.com/TyrGunllod/GrindX/commit/a9354793b19b27834d9fe89a336213a7446b7092))


## v1.26.1 (2026-06-18)

### Bug Fixes

- **infra**: Corrigir versionamento quebrado pelo PSR v10
  ([`1108672`](https://github.com/TyrGunllod/GrindX/commit/110867205268cbb04cee440aa6df2fd519bc43f0))

### Chores

- **infra**: Adicionar compose.yaml.old ao gitignore
  ([`a04b7ce`](https://github.com/TyrGunllod/GrindX/commit/a04b7ce6c4732196cc9842e9efc5d431c5131250))

### Refactoring

- **infra**: Unificar Makefile para Windows e Linux
  ([`d474e61`](https://github.com/TyrGunllod/GrindX/commit/d474e61bb725d088f0f4a6137bce9333ce829d32))


## v1.26.0 (2026-06-18)

### Features

- **infra**: Criar Dockerfiles para frontend, api-sqlserver e api-postgres
  ([`21d5376`](https://github.com/TyrGunllod/GrindX/commit/21d53767a3b1f424bcc7eea378960e20dec52d25))

### Refactoring

- **infra**: Otimizar compose.yaml com build local e realocar .env
  ([`8c74c60`](https://github.com/TyrGunllod/GrindX/commit/8c74c601f48ec3f94fb2a9a68db287b84198d495))


## v1.25.2 (2026-06-18)

### Bug Fixes

- Restaurar build_command como fallback para version.json
  ([`d2966f7`](https://github.com/TyrGunllod/GrindX/commit/d2966f77a444632d0c95555b708476964c74b5f3))

### Documentation

- Spec e plan de importacao de icones no modulo skins
  ([`8b55d5d`](https://github.com/TyrGunllod/GrindX/commit/8b55d5da2984f809d4c987222e05a8ff04656694))


## v1.25.1 (2026-06-18)

### Bug Fixes

- Version.json agora atualizado via version_variable do semantic-release
  ([`9175e6d`](https://github.com/TyrGunllod/GrindX/commit/9175e6d3b40ba66a5afc45ea98740b67bd50bfe0))


## v1.25.0 (2026-06-18)

### Bug Fixes

- Atualizar URL do endpoint de upload nos testes
  ([`f628225`](https://github.com/TyrGunllod/GrindX/commit/f628225108b3add35d8a56ef7df613dbb6983a30))

- Type param deve ser Form() nao query
  ([`0c9c4b9`](https://github.com/TyrGunllod/GrindX/commit/0c9c4b95718d4ac90d5f64091eb0cb453c60e290))

- **proxy**: Dev auto-detection para nao quebrar dev local
  ([`61d5dd8`](https://github.com/TyrGunllod/GrindX/commit/61d5dd82f131ee5d3396968d5a2cf471d7bc3c4d))

### Chores

- Alterar porta do frontend de 5500 para 8101
  ([`a1b9a5f`](https://github.com/TyrGunllod/GrindX/commit/a1b9a5f625dd072755bb07cab8bcee92fa4bff3f))

### Code Style

- Format theme_router.py com ruff
  ([`339655d`](https://github.com/TyrGunllod/GrindX/commit/339655df6385245c9a0c36273dfe9ae5b4ca7abf))

### Documentation

- Atualizar contagem de testes, datas e secao de reverse proxy
  ([`4d0410d`](https://github.com/TyrGunllod/GrindX/commit/4d0410de00e077b7a226ac075c14ad32f3a7a80f))

### Features

- **proxy**: Preparar frontend e nginx para reverse proxy
  ([`3ca9668`](https://github.com/TyrGunllod/GrindX/commit/3ca9668c701744489b2d2a454251d766751bd374))

- **skins**: Aplicar fonte de icones via @font-face no skinLoader
  ([`8338ca7`](https://github.com/TyrGunllod/GrindX/commit/8338ca77a4cb0adc556b532c6ae0c8775cfab5f0))

- **skins**: Endpoint unificado POST /v1/themes/fonts-icons/upload
  ([`aa29244`](https://github.com/TyrGunllod/GrindX/commit/aa292446119d246d90efcf77d83bc7f493da8e76))

- **skins**: Injetar fonte de icones nos iframes dos modulos
  ([`aa1b2af`](https://github.com/TyrGunllod/GrindX/commit/aa1b2afb1538425ef91476e484d50fb706ee332c))

- **skins**: UI de importacao de fonte de icones no admin-skins
  ([`5574478`](https://github.com/TyrGunllod/GrindX/commit/55744786660e4af43f7ccd35ad359c136fb93c19))


## v1.24.0 (2026-06-16)

### Bug Fixes

- Ajuste de containers e makefile para linux
  ([`5f9ea5b`](https://github.com/TyrGunllod/GrindX/commit/5f9ea5b592229be5d0abbaf729dac6c1de137e24))

- **migrations**: Tornar migrations idempotentes e corrigir schemas
  ([`f78528d`](https://github.com/TyrGunllod/GrindX/commit/f78528db7dc807d3a0f3e75e2979219120ad3b24))

### Features

- **migrations**: Criar banco automaticamente se nao existir
  ([`22fd819`](https://github.com/TyrGunllod/GrindX/commit/22fd81969f61d9c43e87530072cd2076a9382a9b))


## v1.23.0 (2026-06-10)

### Documentation

- **deploy**: Atualizar DEPLOYMENT.md com parametros atuais
  ([`0b99e7e`](https://github.com/TyrGunllod/GrindX/commit/0b99e7e75f8bea175fe6896d67fe3ea92a8744af))

- **skill**: Add icon+hide-mobile button pattern to create-standalone-module
  ([`c615f63`](https://github.com/TyrGunllod/GrindX/commit/c615f639e18f19ba817c8043e80dcfd2a92d7ad0))

### Features

- **infra**: Adicionar frontend via Nginx nos containers e regras de firewall
  ([`cd180a7`](https://github.com/TyrGunllod/GrindX/commit/cd180a7b6cf679c1f3397a8c1544406c0871552e))


## v1.22.10 (2026-06-10)

### Bug Fixes

- **css**: Hide-mobile un-hide needs !important to override default
  ([`a614d5b`](https://github.com/TyrGunllod/GrindX/commit/a614d5b14a2380a98dee6465362dfc9bed38626b))

- **login**: Reduce spacing and padding
  ([`f3ada09`](https://github.com/TyrGunllod/GrindX/commit/f3ada0939c46862be783945c60f8b2bfeda65de5))

- **release**: Remove template_dir to fix changelog generation
  ([`38f07db`](https://github.com/TyrGunllod/GrindX/commit/38f07db90ab7786a78c2c40f6dc2a363ac352acc))


## v1.22.9 (2026-06-10)

### Bug Fixes

- **login**: Reduce card max-width to 360px
  ([`0f3a80e`](https://github.com/TyrGunllod/GrindX/commit/0f3a80ea77e331463dec9a40dd4402de3d591d75))


## v1.22.8 (2026-06-10)

### Bug Fixes

- **profile**: Add hide-mobile to Salvar Alteracoes button
  ([`73ca3ca`](https://github.com/TyrGunllod/GrindX/commit/73ca3cae678a3888e0a192e5468dac4a35374553))


## v1.22.7 (2026-06-10)

### Bug Fixes

- **importer**: Add hide-mobile to Checar Arquivos button
  ([`1755f61`](https://github.com/TyrGunllod/GrindX/commit/1755f61d3dde47fbe8e992203f746b931c6e514e))


## v1.22.6 (2026-06-10)

### Bug Fixes

- **importer**: Add icon+hide-mobile pattern to action buttons
  ([`64d9af6`](https://github.com/TyrGunllod/GrindX/commit/64d9af66e1abbf9fa9366d1f32d7a406a60c349e))


## v1.22.5 (2026-06-10)

### Bug Fixes

- **dashboard**: Hide top-bar on desktop to fix iframe overlap
  ([`4be9cce`](https://github.com/TyrGunllod/GrindX/commit/4be9cce11e5293ca80db870193bc6e4e0fa7fdda))


## v1.22.4 (2026-06-10)

### Bug Fixes

- Force sidebar mode on mobile/tablet, revert buttons to previous format
  ([`99aa0b4`](https://github.com/TyrGunllod/GrindX/commit/99aa0b4180ec9286663e88d5bf61b986734dffe1))


## v1.22.3 (2026-06-10)

### Bug Fixes

- **dashboard**: Proper top-bar height on mobile to fix iframe overlap
  ([`9006cdd`](https://github.com/TyrGunllod/GrindX/commit/9006cdda61d863f7aaa2f870fcdfb08b14058b1c))


## v1.22.2 (2026-06-10)

### Bug Fixes

- Sidebar hidden on mobile in topbar mode, and action buttons in table-to-card
  ([`5e7194e`](https://github.com/TyrGunllod/GrindX/commit/5e7194ea82392186bb1ad348929475887cf5464d))


## v1.22.1 (2026-06-10)

### Bug Fixes

- **ci**: Remove persist-credentials false and deduplicate release steps
  ([`f497b40`](https://github.com/TyrGunllod/GrindX/commit/f497b403d645cffb2ae8e8cb15abb1a70d972b02))

### Documentation

- Update plan with space-050 naming fix
  ([`da52b0f`](https://github.com/TyrGunllod/GrindX/commit/da52b0f31c5959431afde4f29b8f214b4c599c1d))


## v1.22.0 (2026-06-10)

### Bug Fixes

- **admin-skins**: Responsive max-width constraints and color-grid
  ([`a78c8b3`](https://github.com/TyrGunllod/GrindX/commit/a78c8b38ee167ee28101745dc799e6257914f9ca))

- **css**: Address code review issues for responsive utilities
  ([`0768d2e`](https://github.com/TyrGunllod/GrindX/commit/0768d2e2271d399e7507396ee4d5339afa1fce5c))

- **css**: Rename space-0.5 and space-1.5 to space-050 and space-150 to avoid fragile CSS escaped
  dots
  ([`4f69c75`](https://github.com/TyrGunllod/GrindX/commit/4f69c7530045a4026a4731911185be7114280d4f))

- **dashboard**: Address code review - overlay class, resize debounce, inline styles
  ([`c500aff`](https://github.com/TyrGunllod/GrindX/commit/c500aff915a743c5094b0d6682775ba7506b238d))

- **modules**: Add touch targets to structure and profile
  ([`8c6feb3`](https://github.com/TyrGunllod/GrindX/commit/8c6feb387fb7a258f3107cd882f5dc21e54cafcc))

- **users**: Remove duplicate hide-mobile from preview CSS
  ([`1177cd6`](https://github.com/TyrGunllod/GrindX/commit/1177cd61a2471e0055889d1b036b79a58503814f))

### Documentation

- Add frontend responsividade spec, plan and update create-standalone-module skill
  ([`cb5cfbb`](https://github.com/TyrGunllod/GrindX/commit/cb5cfbb8a2ead126d0f17c31d99d7789648ffec8))

### Features

- **css**: Add breakpoint tokens and spacing scale to core.css
  ([`60800ec`](https://github.com/TyrGunllod/GrindX/commit/60800ec11ad373a82a9e1007421847a6ca7cfd3a))

- **css**: Add responsive utilities, touch targets and grid extensions
  ([`4b2eeda`](https://github.com/TyrGunllod/GrindX/commit/4b2eeda53e46a939de217459986824f1948e50b0))

- **dashboard**: Implement 3-breakpoint responsive sidebar shell
  ([`96edd23`](https://github.com/TyrGunllod/GrindX/commit/96edd23318deed016db29afbd6b23c4003148447))

- **importer**: Implement table-to-card responsive pattern
  ([`44ef609`](https://github.com/TyrGunllod/GrindX/commit/44ef609dcaacda59ee26a8319fc6739e23ef7e25))

- **users**: Implement table-to-card responsive pattern with data-label
  ([`1ed69c0`](https://github.com/TyrGunllod/GrindX/commit/1ed69c0119f66665fc12fb2eaf3063074680b5ee))


## v1.21.0 (2026-06-10)

### Bug Fixes

- **auth**: Reattach cached ORM object before refresh
  ([`70f8f48`](https://github.com/TyrGunllod/GrindX/commit/70f8f4887699ef366165e52f76bfdb2bbe618af2))

- **cors**: Garantir origins de dev sempre presentes
  ([`a161320`](https://github.com/TyrGunllod/GrindX/commit/a161320397069af4c86f99dde69c2c6bab2dea38))

- **dashboard**: Abrir abas no click em vez de hover para funcionar em touch
  ([`62d10e7`](https://github.com/TyrGunllod/GrindX/commit/62d10e7dfd27359a8bd328c0433445612f41de7e))

- **frontend**: Servir apple-touch-icon.png na raiz
  ([`4feb35b`](https://github.com/TyrGunllod/GrindX/commit/4feb35bf089274dc70c31eb0dfb145cdbc64a7a7))

### Documentation

- **agents**: Adicionar regra de atualizacao de documentacao
  ([`77e75d3`](https://github.com/TyrGunllod/GrindX/commit/77e75d357359c69869a84008cb01402648af6fb3))

- **network**: Atualizar .env.example com DEV_NETWORK_IP e CORS_ORIGINS vazio
  ([`876ac51`](https://github.com/TyrGunllod/GrindX/commit/876ac51b8cae7ca76d4ac4f22fa1e567f7bfe75a))

### Features

- **auth**: Persistir preferencia de tema light/dark no banco
  ([`279206e`](https://github.com/TyrGunllod/GrindX/commit/279206e8294204b23422bb2841a787f8d0887872))

- **network**: Centralizar IP de acesso externo via DEV_NETWORK_IP env var
  ([`b18a0b8`](https://github.com/TyrGunllod/GrindX/commit/b18a0b814aa1362c68a0d372d5282133c00ec29f))

- **skins**: Adicionar preview cards, snapshot original e API de restore
  ([`9fd8a30`](https://github.com/TyrGunllod/GrindX/commit/9fd8a306c266b523a8f896a91288973dbf01a837))


## v1.20.0 (2026-06-10)

### Bug Fixes

- _updateLogos preserva dropdown, .logo-text escondido no collapsed
  ([`02bf6cd`](https://github.com/TyrGunllod/GrindX/commit/02bf6cde62c651a8799cdc09cb93585911744f6b))

- Sincronizar userUI ao salvar perfil, corrigir toggle tema e adicionar feedback de erro
  ([`8dd2506`](https://github.com/TyrGunllod/GrindX/commit/8dd25067832ba7d797b4e6f82723d991d685b6d1))

- SkinLoader nao destroi dropdown ao atualizar logo, usar event delegation no click
  ([`b3a75d7`](https://github.com/TyrGunllod/GrindX/commit/b3a75d7543b2a98628525bfab95bfa492be5bbb0))

- Usar endsWith para evitar falsos positivos no redirect 401
  ([`a15a232`](https://github.com/TyrGunllod/GrindX/commit/a15a2322983cefe7569c9a4980fc54f144c7e081))

- **auth**: Adicionar docstrings e logging em update_profile e update_me
  ([`6563f70`](https://github.com/TyrGunllod/GrindX/commit/6563f705a0636322fd3a4930107e3a8c4a635d9a))

- **dashboard**: Dropdown do logo usando > .user-dropdown, topbar igual ao sidebar
  ([`3a68e22`](https://github.com/TyrGunllod/GrindX/commit/3a68e2216bf48e2443c4aa25babe51d6314ce4da))

- **dashboard**: Fix topbar dropdown menu clipping
  ([`3e96a55`](https://github.com/TyrGunllod/GrindX/commit/3e96a55b30dd4d1d2749e4b691ee660dc8e85d0c))

- **dashboard**: Fix topbar layout direction
  ([`15dd225`](https://github.com/TyrGunllod/GrindX/commit/15dd2255a771441a3ac24b98059b08c1e923d476))

- **dashboard**: Truncate long module names in topbar dropdowns
  ([`222bc97`](https://github.com/TyrGunllod/GrindX/commit/222bc97f8d78e7e2bedc8c74e07a3a82b43a0e3f))

- **dashboard**: Truncate module and tab names to 16 chars
  ([`5d91175`](https://github.com/TyrGunllod/GrindX/commit/5d91175f8c10d13da0823ebfd4f9848d751a0eb5))

- **dashboard**: Use position fixed for topbar dropdowns
  ([`1652530`](https://github.com/TyrGunllod/GrindX/commit/1652530b5209fc1fecd446f80c7a44cfc05c6fa7))

- **migrations**: Make all migrations idempotent for fresh databases
  ([`69a574b`](https://github.com/TyrGunllod/GrindX/commit/69a574bc3c774a06d3a90935e6a6e8a62b5538c8))

- **profile**: Carregar dados do parent como fallback, adicionar config.js, corrigir 401 redirect no
  iframe
  ([`7998d98`](https://github.com/TyrGunllod/GrindX/commit/7998d98049544faeb9f000c4c799d551cf3ef5ae))

- **skin**: Invalidate cache when theme is updated
  ([`8f08e01`](https://github.com/TyrGunllod/GrindX/commit/8f08e01fd30827c444c0f452b23d64620392a7e9))

- **skinloader**: Atualizar tambem topbar-logo no _updateBranding
  ([`a0b7139`](https://github.com/TyrGunllod/GrindX/commit/a0b7139267b86d92ef7ee03e96f453272a06201f))

- **skins**: Mover importar fontes para baixo do seletor de fonte
  ([`b0bca0d`](https://github.com/TyrGunllod/GrindX/commit/b0bca0d7eee14d2c267a8d4618048156aba876a5))

- **skins**: Padronizar botoes de importar/usar template para btn-primary
  ([`52225a8`](https://github.com/TyrGunllod/GrindX/commit/52225a8c2fd4a2415fd2ee00595a0e7956a81e7a))

- **skins**: Uniformizar largura dos inputs no editor de skin
  ([`7a71128`](https://github.com/TyrGunllod/GrindX/commit/7a71128ca96c011b04bf96289fe32573e9e41c1d))

- **skins,structure**: Remover estilos duplicados de botoes
  ([`1f4c99d`](https://github.com/TyrGunllod/GrindX/commit/1f4c99d9772aec4130964bb96fdc1dd53530fd2e))

- **theme**: Incluir layout_mode no template creation
  ([`4213d0a`](https://github.com/TyrGunllod/GrindX/commit/4213d0a150b7efc10dbaed7d4542f665053140f8))

### Chores

- Corrigir importacoes nao utilizadas em migracoes alembic
  ([`a1df2c8`](https://github.com/TyrGunllod/GrindX/commit/a1df2c85795591c11d945616f382351b16df57bc))

### Code Style

- Aplicar ruff format em arquivos python
  ([`e637b6e`](https://github.com/TyrGunllod/GrindX/commit/e637b6e2d2806a6cb8b6b99054bbbca203660864))

- Format update_profile signature
  ([`8227709`](https://github.com/TyrGunllod/GrindX/commit/8227709f8584df597737e5be81ead84d9ac4cfb4))

### Documentation

- Adicionar spec e plano para redesign do dashboard e perfil
  ([`4c0e4ca`](https://github.com/TyrGunllod/GrindX/commit/4c0e4ca8cbb78dce012fccd6ecdd107e6e123594))

- Update documentation for dual layout feature
  ([`a707d66`](https://github.com/TyrGunllod/GrindX/commit/a707d66b90475c804cf39f8894d03bac0458da47))

### Features

- **admin-skins**: Add layout mode selector to skin editor
  ([`74d5a36`](https://github.com/TyrGunllod/GrindX/commit/74d5a365a549d0b671c3a3e81df3de2d70992049))

- **api**: Redirecionar para login ao receber 401 em chamadas autenticadas
  ([`f0ce646`](https://github.com/TyrGunllod/GrindX/commit/f0ce646ceb06cbb43bc859b7c396bb392e90e6b2))

- **auth**: Adicionar endpoint PUT /v1/auth/me para autoatualizacao de perfil
  ([`f90193b`](https://github.com/TyrGunllod/GrindX/commit/f90193bea7b0bfcda8de81fa0b949aa580973389))

- **dashboard**: Estilos para logo-clicavel e ajustes pos-remocao user-pill
  ([`01d8c70`](https://github.com/TyrGunllod/GrindX/commit/01d8c7096698a97ded388883cc0c0be740d2bca4))

- **dashboard**: Eventos de click no logo, loadProfileModule, remover metodos de tema e senha
  ([`7c2f59f`](https://github.com/TyrGunllod/GrindX/commit/7c2f59ff444e63156e5d53e9e4a26c21c1e51d1b))

- **dashboard**: Logos clicaveis, remover user-pill sidebar, theme toggles e modal senha
  ([`c34c617`](https://github.com/TyrGunllod/GrindX/commit/c34c617a3aa96d4edcc72e0697c9ca6ac970a8a1))

- **dashboard**: Suporte dual layout sidebar e topbar
  ([`ce8bf0b`](https://github.com/TyrGunllod/GrindX/commit/ce8bf0b304422b5de04cdb05128d4b7704be2d61))

- **frontend**: Add topbar header structure to dashboard HTML
  ([`61e5459`](https://github.com/TyrGunllod/GrindX/commit/61e545994d52cbf6973b0ed242daff02e0b06bcf))

- **layout**: Add topbar CSS styles and layout switching rules
  ([`5452acf`](https://github.com/TyrGunllod/GrindX/commit/5452acf7b09bad034edb1f6b8064f86bcd48eccf))

- **migration**: Adicionar coluna layout_mode em company_themes
  ([`395d264`](https://github.com/TyrGunllod/GrindX/commit/395d264ae2f28b19ed11f75c7b837bb003b5a361))

- **org**: Add layout_mode column to CompanyTheme model
  ([`226dc40`](https://github.com/TyrGunllod/GrindX/commit/226dc409ba36c8163a658fb4ac13b96c69c4364b))

- **profile**: Criar modulo de perfil com email, senha e preferencia de tema
  ([`f4bed46`](https://github.com/TyrGunllod/GrindX/commit/f4bed466420b1ddc01b925720093333df0360791))

- **skinLoader**: Adicionar layout_mode no fluxo de skin
  ([`98a2c64`](https://github.com/TyrGunllod/GrindX/commit/98a2c640a3ef59f59ce1609a077e2e5074a9afc4))

- **skins**: Remover botao refresh e adicionar importar skin
  ([`a193d6d`](https://github.com/TyrGunllod/GrindX/commit/a193d6db82750a9177a2d4e17cb7d8008b9af59d))

- **theme**: Add layout_mode to Pydantic schemas
  ([`885b201`](https://github.com/TyrGunllod/GrindX/commit/885b201b2fa8a7212f349dd7581bfbf3215c34af))

- **theme**: Incluir layout_mode na logica do ThemeService
  ([`0de07ba`](https://github.com/TyrGunllod/GrindX/commit/0de07baf9e709abf81f051417d497ba80210c6b1))

- **ui**: Padronizar botoes e ajustar hover/icone do logo
  ([`61f3d70`](https://github.com/TyrGunllod/GrindX/commit/61f3d70af392f0f60ae622f98cd12f45159a3d49))

### Testing

- **theme**: Add layout_mode unit tests
  ([`b509736`](https://github.com/TyrGunllod/GrindX/commit/b509736eb441e1b419b19cbab450252d0be4c65b))

- **themes**: Add layout_mode integration tests
  ([`06ba12e`](https://github.com/TyrGunllod/GrindX/commit/06ba12e533a520957e0a40d8539700fbb88848f2))


## v1.19.2 (2026-06-09)

### Bug Fixes

- Atualizar APP_VERSION para 1.19.0 (sync com CHANGELOG)
  ([`81d9137`](https://github.com/TyrGunllod/GrindX/commit/81d91375271ca1ff7b4c72ec7139cb5ff287b19a))


## v1.19.1 (2026-06-09)

### Bug Fixes

- Tornar update_frontend_version.py independente do CWD
  ([`66727d5`](https://github.com/TyrGunllod/GrindX/commit/66727d572edf9e88720a042001bb812e2841c670))


## v1.19.0 (2026-06-09)

### Bug Fixes

- Atualizar APP_VERSION para 1.18.0
  ([`fe6c0dd`](https://github.com/TyrGunllod/GrindX/commit/fe6c0dd33d792a3e06d7981cf3353547bf002440))

- Corrigir CI para usar requirements-dev.txt e remover slowapi duplicado no api-sqlserver
  ([`5724260`](https://github.com/TyrGunllod/GrindX/commit/572426080fd2ec9c143a73a8a80cb4de446e2f67))

- Remover SEC-07 dos itens adiados no STATE.md
  ([`b7031b8`](https://github.com/TyrGunllod/GrindX/commit/b7031b8c5e527ac07f857da1d35c8bb7b14ee136))

- Remover slowapi duplicado no requirements.txt
  ([`065dff1`](https://github.com/TyrGunllod/GrindX/commit/065dff18a29448c22a79d4ddad71be5602ac996a))

- Sincronizar version.json automaticamente no release
  ([`456e183`](https://github.com/TyrGunllod/GrindX/commit/456e183dde09d67ca9e5fc1a9cd965401e5387a6))

### Continuous Integration

- Adicionar coverage threshold 70% ao Jenkinsfile
  ([`bb52f69`](https://github.com/TyrGunllod/GrindX/commit/bb52f697e0db0d8fcdfb8fbb69d703c6c9452f42))

### Documentation

- Atualizar API.md — remover produtos, adicionar import
  ([`22d6723`](https://github.com/TyrGunllod/GrindX/commit/22d67230b93180a9adfa86c87509932ac94fc714))

- Atualizar MAPA-ARQUIVOS com estrutura atual
  ([`70485ef`](https://github.com/TyrGunllod/GrindX/commit/70485ef047fe84049b86365633aa749436ad0374))

- Atualizar SETUP com paths apps/
  ([`e9d628e`](https://github.com/TyrGunllod/GrindX/commit/e9d628eef1848576a1b09655c8d34ec68ea1d8b4))

### Features

- Tornar API_BASE_URL injetavel via window.__GRINDX_API_URL
  ([`6fd0783`](https://github.com/TyrGunllod/GrindX/commit/6fd078395f0470f1ac214a4d7ac108b9a0add420))

### Refactoring

- Renomear migracoes para padrao sequencial (001-008)
  ([`2240761`](https://github.com/TyrGunllod/GrindX/commit/2240761a7212feced90c9264600ccb6cd3d5c6cb))

- Separar dependencias dev/prod no api-postgres
  ([`66dcf11`](https://github.com/TyrGunllod/GrindX/commit/66dcf11e326b965add4040dd90d617863b35f8e1))


## v1.18.0 (2026-06-09)

### Features

- **security**: SECRET_KEY com validação de entropia Shannon (mínimo 3.5 bits/caractere)
- **security**: Senhas temporárias com expiração de 15 minutos via `secrets` module
- **security**: Rate limiting com SlowAPI e chaves duplas (IP + user_id) para ambas as APIs
- **security**: Validação de magic bytes em uploads via biblioteca `filetype`
- **security**: CORS strict mode em produção (nunca `*`)
- **cache**: Camada de cache in-memory com `cachetools` TTLCache (15 min TTL)
- **indexes**: 5 índices B-tree via migração Alembic para queries comuns
- **health**: Health checks profundos com verificação de conectividade + schema
- **versioning**: Módulo de versionamento de API documentado (`versioning.py`)
- **docs**: Script para exportação OpenAPI (`scripts/export_openapi.py`)

### Bug Fixes

- **health**: Corrigir health check para SQLite (tabelas sem prefixo de schema)
- **health**: Adicionar `connect_timeout=5` para evitar hang quando DB inacessível
- **auth**: Corrigir cache invalidation após criar usuário
- **auth**: Corrigir mock de `temp_password_hash` e `expires_at` em testes
- **frontend**: Adicionar prefixo `/v1/` correto nas chamadas API

### Improvements

- **error-codes**: Registro centralizado de códigos de erro (`packages/shared/exceptions/codes.py`)
- **path-traversal**: Proteção contra directory traversal no theme_router
- **model-docs**: Documentação de re-exports em `app/models/usuario.py`
- **config**: Centralização de API URLs no frontend
- **lint**: Correção de todos os erros de lint e formatação com ruff

### Infrastructure

- **pytest-cov**: Configurado com threshold de 70% mínimo
- **migrations**: Consolidação de migrações órfãs (cadeia linear com único head)
- **schema**: Validação de `_SCHEMA_TRANSLATE` cobre todos os 4 schemas PostgreSQL

### Documentation

- **AGENTS.md**: Atualizado com informações de segurança, performance e infraestrutura
- **CONCERNS.md**: 17/21 itens resolvidos (81%)

---

## v1.17.0 (2026-06-01)

### Bug Fixes

- Raise RuntimeError when main.py has no router imports
  ([`c562669`](https://github.com/TyrGunllod/GrindX/commit/c5626691b5f81624ae0eae5c58ac2fc5bfd65c0f))

- **import**: Corrigir limpeza de dependencies.py e env.py
  ([`59c4e7a`](https://github.com/TyrGunllod/GrindX/commit/59c4e7a90ae198ac02c04af584ec844852ee04f7))

- **import**: Limpar dependencies.py e env.py ao remover modulo
  ([`9624f90`](https://github.com/TyrGunllod/GrindX/commit/9624f907a3ea19348702e7b13a505f8c0aab3b3b))

- **import**: Limpar main.py ao remover modulo
  ([`dddfd56`](https://github.com/TyrGunllod/GrindX/commit/dddfd561f9ca94893a33e4c1613f739e7839dedb))

- **import**: Passar force como query param correto
  ([`12e007a`](https://github.com/TyrGunllod/GrindX/commit/12e007a19a0f4ac96f4bb066818e054ee36d24bd))

- **import**: Prevenir interrupcao do subprocesso no Windows
  ([`e4cf0c5`](https://github.com/TyrGunllod/GrindX/commit/e4cf0c555357127f1a5e76681927251e87b797cb))

- **import**: Resetar estado do botao ao abrir modal
  ([`bd1ea75`](https://github.com/TyrGunllod/GrindX/commit/bd1ea75b5c9d7c5bbe109387c24ff9f998f0c31f))

- **import**: Tratar erro de importacao como possivel reinicio
  ([`91e6ff7`](https://github.com/TyrGunllod/GrindX/commit/91e6ff7ab2be0647c2b7658f9f7ef18b72ec10c9))

- **import**: Verificar filesystem no scan de modulos
  ([`b87e26c`](https://github.com/TyrGunllod/GrindX/commit/b87e26cf74b39f41d3fdec3bec61d1fdd25d7784))

- **import_module**: Correct router import path for standalone modules
  ([`d95a685`](https://github.com/TyrGunllod/GrindX/commit/d95a6856da315f488a9ad9ac69e5f608021c6c41))

- **importer**: Corrigir page-header para padrao vertical igual ao preview
  ([`204a815`](https://github.com/TyrGunllod/GrindX/commit/204a8154cbaca36268ae95661d6a19744980cd91))

- **importer**: Usar Python do venv + timeout 120s + tratar KeyboardInterrupt
  ([`04df110`](https://github.com/TyrGunllod/GrindX/commit/04df1103815e749f9d0c82535c26133bfae5f9b8))

- **test**: Corrigir erros de linting no test_import_module.py
  ([`0989cea`](https://github.com/TyrGunllod/GrindX/commit/0989ceaeb1aca4aca930fb29d7e146228c962afa))

### Chores

- Commit pendente - seed, style, migration
  ([`8b08685`](https://github.com/TyrGunllod/GrindX/commit/8b08685e04a8de0653df73ba06bb2a361268e293))

### Code Style

- Aplicar ruff format nos arquivos
  ([`6c6695c`](https://github.com/TyrGunllod/GrindX/commit/6c6695cd97bb34b0d9a51dc394656e553937427f))

- **importer**: Centralizar cabecalhos e valores da tabela
  ([`f6858ff`](https://github.com/TyrGunllod/GrindX/commit/f6858ffe4432a49ffd8ca60891cc4199fa2b2fb4))

### Features

- Add register_dependency() to import_module.py
  ([`d84031b`](https://github.com/TyrGunllod/GrindX/commit/d84031bc1cfc62adabc6d26edf083364fc06ade5))

- **frontend**: Padronizar header dos modulos e adicionar push policy
  ([`d653c02`](https://github.com/TyrGunllod/GrindX/commit/d653c02f923f4e94a7dde9a32866d280cd919793))

- **import**: Aguardar reinicio do servidor apos importacao
  ([`6baff93`](https://github.com/TyrGunllod/GrindX/commit/6baff939f87448abbe94e886aa6968d7a26493a1))

- **import**: Substituir reimportar por remover
  ([`4fbf718`](https://github.com/TyrGunllod/GrindX/commit/4fbf7188b554bf1a285c47fd16a2643d0eaa0226))

### Refactoring

- **importer**: Remover funcionalidade de expandir modulos
  ([`4215153`](https://github.com/TyrGunllod/GrindX/commit/4215153b60f0964ef04f5af8649cae51e5de84c0))

### Testing

- Add integration test for complete import flow (Task 4)
  ([`14c1d95`](https://github.com/TyrGunllod/GrindX/commit/14c1d954f7cbb7276c746f03f18a1a8ef1af00bb))


## v1.16.1 (2026-06-01)

### Bug Fixes

- **seed**: Corrigir aspas faltante em valor de cor
  ([`bd6afda`](https://github.com/TyrGunllod/GrindX/commit/bd6afdaf58282ee4232c1087876c15797ce94d2f))

### Chores

- Limpar preview nao utilizado e atualizar seed
  ([`be3942d`](https://github.com/TyrGunllod/GrindX/commit/be3942df78da23db1138644e80431c125fa02f53))


## v1.16.0 (2026-05-31)

### Bug Fixes

- Auto-fix ruff lint errors (import sorting, unused imports)
  ([`dd33c5a`](https://github.com/TyrGunllod/GrindX/commit/dd33c5a20379a1976cf7a46c4040d81d9ad1d28c))

- **data-table**: Passar item completo quando coluna nao tem key
  ([`0107ee4`](https://github.com/TyrGunllod/GrindX/commit/0107ee439cd40ef2c4d08b02841450fcf56c4cae))

- **data-table**: Suportar colunas com key e render
  ([`50e911e`](https://github.com/TyrGunllod/GrindX/commit/50e911e97f80db2af05cb1d9194f44983c148e95))

- **frontend**: Remover referencia a apple-touch-icon inexistente
  ([`2426b91`](https://github.com/TyrGunllod/GrindX/commit/2426b9112c2f05d05112decb7ef0c4bd1162345b))

- **frontend**: Replace sidebar nav <a> with <button> to hide status bar on hover
  ([`be8a811`](https://github.com/TyrGunllod/GrindX/commit/be8a811dd8f56b9652b4f3f270ffdbd5acc50a71))

- **importer**: Adicionar style.css da raiz para estilos do modal
  ([`ac30e58`](https://github.com/TyrGunllod/GrindX/commit/ac30e58175eac9e9f6a60c71638dfc15b33268ac))

- **importer**: Corrigir URL duplicada /v1/v1 nos endpoints da API
  ([`1d63d86`](https://github.com/TyrGunllod/GrindX/commit/1d63d862ac4c2d69752ef22310903010b75f067d))

- **infra**: Extract APP_VERSION to module-level for semantic-release
  ([`6e15998`](https://github.com/TyrGunllod/GrindX/commit/6e15998ed0f55b72f734afca8ed5344af98a76cb))

- **scripts**: Corrigir caminhos no update_frontend_version.py
  ([`bf6177d`](https://github.com/TyrGunllod/GrindX/commit/bf6177d950db7790c0a69f1e4d5a28c81c3816e3))

- **skins**: Remove old header styles, use standard page-header spacing
  ([`234eaa8`](https://github.com/TyrGunllod/GrindX/commit/234eaa8771c7f24f453bcebe01696710604c5f03))

### Chores

- Adicionar import/ ao .gitignore
  ([`657576a`](https://github.com/TyrGunllod/GrindX/commit/657576a73d63da016cbcfe459b9c3d9eeaa03eac))

- Merge refactor/migrate-to-apps para main
  ([`19401e9`](https://github.com/TyrGunllod/GrindX/commit/19401e94ee7e78cec3f96b80b7f71ed98ac9483d))

- **skills**: Atualizar create-standalone-module com regra de page-header
  ([`4e76617`](https://github.com/TyrGunllod/GrindX/commit/4e766178cb19dd63e648b846b97910a664ca6562))

### Code Style

- **api**: Aplicar ruff format nos arquivos pendentes
  ([`9ef9cfc`](https://github.com/TyrGunllod/GrindX/commit/9ef9cfcff4ed3fc6f7187f5fbb665d091ec0169b))

- **importer**: Alinhar paddings e margins com modulo users
  ([`4d1a823`](https://github.com/TyrGunllod/GrindX/commit/4d1a82393afabbdaafdb2df2923b26797891b661))

### Documentation

- Update documentation paths for apps/ migration
  ([`b533449`](https://github.com/TyrGunllod/GrindX/commit/b5334491b976c072675a1c82e367b098f9540ce2))

- **import**: Add implementation plan for module import feature
  ([`f86aca5`](https://github.com/TyrGunllod/GrindX/commit/f86aca560c7d7d104af0afc36ae87f2d98fb7c94))

- **import**: Adicionar spec de importacao de modulos via UI
  ([`c5a5cb0`](https://github.com/TyrGunllod/GrindX/commit/c5a5cb0fae7fece1ba45d95cddcf72bef5606f5c))

### Features

- **assets**: Gerar apple-touch-icon via generate_favicon.py
  ([`003e2a7`](https://github.com/TyrGunllod/GrindX/commit/003e2a710bfb14210e66c053420467d6f588eddf))

- **import**: Add frontend importer module with scan UI
  ([`845fa0c`](https://github.com/TyrGunllod/GrindX/commit/845fa0c64f98f9791739083ee49ed5715029f634))

- **import**: Adicionar configuracao IMPORT_DIR
  ([`9d0a222`](https://github.com/TyrGunllod/GrindX/commit/9d0a2222d6d6d1afc8d35f40226b180b8f8714c2))

- **import**: Adicionar import_router e testes
  ([`d97986d`](https://github.com/TyrGunllod/GrindX/commit/d97986db90e411ee07045b6d04974bff4b44c31d))

- **import**: Adicionar script import_module.py
  ([`3fd9069`](https://github.com/TyrGunllod/GrindX/commit/3fd9069abe40398f0b014f6ceff28e2ff91e847e))

- **importer**: Add page header with description and font-awesome icons
  ([`e2f0644`](https://github.com/TyrGunllod/GrindX/commit/e2f0644c6da1a55898df59177a0dadf7dbde1ebf))

- **importer**: Adicionar estilos CSS para cards inline
  ([`96e4eb3`](https://github.com/TyrGunllod/GrindX/commit/96e4eb3a609db3d96d3b75ddd69ed7d611aa1acb))

- **importer**: Adicionar função abrirCard para expansão de cards
  ([`0d15110`](https://github.com/TyrGunllod/GrindX/commit/0d1511064626f7ae80f841805cd4ee1c609c539a))

- **importer**: Adicionar função criarCardExpandido para renderizar card
  ([`9e8d5e2`](https://github.com/TyrGunllod/GrindX/commit/9e8d5e2f5c7462b753f61e834d1f41bd73a0085a))

- **importer**: Adicionar propriedade modules ao controller
  ([`aa658f5`](https://github.com/TyrGunllod/GrindX/commit/aa658f54f59502732b539c69f01a0d8cdc7ef79a))

- **importer**: Adicionar suporte a classes CSS e data attributes no DataTable
  ([`0832f67`](https://github.com/TyrGunllod/GrindX/commit/0832f67cd2dd5a8b8e0364e566d4a1ebca74f0e5))

- **importer**: Adicionar verificacao manual de arquivos
  ([`b876092`](https://github.com/TyrGunllod/GrindX/commit/b8760927a87e2e76cced77c77a72d3d7f308ac66))

- **importer**: Ajustar estrutura HTML e lógica de cards para tabela válida
  ([`833fadb`](https://github.com/TyrGunllod/GrindX/commit/833fadb0f066cd30deee540fb57342da36013bbd))

- **importer**: Modificar bindEvents para suportar expansão de cards
  ([`31867c0`](https://github.com/TyrGunllod/GrindX/commit/31867c0232f9b3f2d127cf88aca109fd73f9be9d))

- **importer**: Salvar dados dos módulos na instância do controller
  ([`09fc89a`](https://github.com/TyrGunllod/GrindX/commit/09fc89a5f23afc2eb66f7e0dafd241a8ea32b19c))

- **scripts**: Auto-instalar dependencias no generate_favicon.py
  ([`7c53ba7`](https://github.com/TyrGunllod/GrindX/commit/7c53ba7656fb1d61bd77cd41d41b3f10f06f547f))

- **seed**: Add importer module to Gestão tab
  ([`cca3f10`](https://github.com/TyrGunllod/GrindX/commit/cca3f10bf7fa2df2a837fedf1f979b0b05d34c54))

- **skill**: Adicionar module.json e comando package ao create-standalone-module
  ([`6984d43`](https://github.com/TyrGunllod/GrindX/commit/6984d43e7ebf23db42d0684c8a7d7648bbf1b14d))

- **skins**: Add page header with description and action buttons
  ([`99d4503`](https://github.com/TyrGunllod/GrindX/commit/99d4503d6481da3928e3d4aa08704d324eb1e193))

### Refactoring

- Move api-postgres, api-sqlserver, frontend-webapp to apps/
  ([`c4d989f`](https://github.com/TyrGunllod/GrindX/commit/c4d989fea97125360579c4db58673a8871b8d887))

- Update config files for apps/ migration (podman, makefile, pyproject, CI, jenkins, pytest)
  ([`fd5825b`](https://github.com/TyrGunllod/GrindX/commit/fd5825bfb9abc9501e8a74bbdd664b349ab0bf55))

- Update test paths and import_module.py for apps/ migration
  ([`5db099d`](https://github.com/TyrGunllod/GrindX/commit/5db099dcec3ff4444d6facefb0348315fdb6b30f))

- **api**: Remover módulo produto completo (router, service, schema, model, tests)
  ([`15cc908`](https://github.com/TyrGunllod/GrindX/commit/15cc9081aad2944c5518f55be8a0e3207bcbb24f))

- **api**: Renomear prefixo /v1/estoque para /v1/produto
  ([`6e9c636`](https://github.com/TyrGunllod/GrindX/commit/6e9c6365b6454a07618ffdf64492a90355cc4fb7))


## v1.15.0 (2026-05-26)

### Chores

- **infra**: Add .gitattributes para normalizar line endings
  ([`a7fe42f`](https://github.com/TyrGunllod/GrindX/commit/a7fe42f184dc43ccd6fd214b06b3fed243106bb9))

### Features

- **docs**: Add create-module skill with backend and frontend templates
  ([`a821a27`](https://github.com/TyrGunllod/GrindX/commit/a821a27a02ddf583e07d97791af87d7bc0b7a23a))


## v1.14.0 (2026-05-26)

### Code Style

- Add ruff.toml for api-postgres and fix all I001 import sorting
  ([`e603dd7`](https://github.com/TyrGunllod/GrindX/commit/e603dd78f17d1ccb72a5b258a7e4810ce8bb9b7c))

- Fix import sorting across api-postgres with ruff I001
  ([`4984de8`](https://github.com/TyrGunllod/GrindX/commit/4984de8b79f3adc506b47b65ac10cc990e44c3e9))

- Ruff format 3 files in api-postgres
  ([`9c3f801`](https://github.com/TyrGunllod/GrindX/commit/9c3f801a83ad7b3482305e2f2980aa69d85905b4))

### Features

- **frontend**: Add release version to login screen
  ([`a7d874c`](https://github.com/TyrGunllod/GrindX/commit/a7d874cff316cc4edc6d133698a5ba6e5578877a))


## v1.13.0 (2026-05-26)

### Code Style

- **shared**: Adicionar padding padrao no subtitulo do page-header
  ([`fc8c974`](https://github.com/TyrGunllod/GrindX/commit/fc8c9742110e9dd3c3292338e91904235c703bbc))

### Documentation

- Update all documentation to reflect current project state
  ([`2dbf506`](https://github.com/TyrGunllod/GrindX/commit/2dbf506c321f714b4ac4b03d8abff952d1c2c12d))

### Features

- **admin**: Remover botao X e adicionar cancelar no modal de skins; adicionar scroll nos modais de
  estrutura
  ([`25a7090`](https://github.com/TyrGunllod/GrindX/commit/25a709030dffa222db22ab925b4feb00e06ffe0f))


## v1.12.1 (2026-05-25)

### Bug Fixes

- **auth**: Order forgot-password ops and fix SMTP default host
  ([`3c47d44`](https://github.com/TyrGunllod/GrindX/commit/3c47d44b8b8a99ff5944d1fb07995ae805f45dfc))

### Chores

- **env**: Add SMTP default config to .env.example
  ([`090e0bc`](https://github.com/TyrGunllod/GrindX/commit/090e0bc19447d8a0cf80334de4d06983ab84c9dd))


## v1.12.0 (2026-05-25)

### Features

- **auth**: Forgot-password flow with email recovery
  ([`685d001`](https://github.com/TyrGunllod/GrindX/commit/685d001b75b6e1e24d88ef5c23dc0fc39ee08de9))


## v1.11.0 (2026-05-25)

### Code Style

- **seed**: Format with ruff
  ([`fa5eda9`](https://github.com/TyrGunllod/GrindX/commit/fa5eda9498aca322b2e17329c6953a698d2d23d7))

### Features

- **seed**: Add logo_url to GrindX default theme
  ([`789cb7a`](https://github.com/TyrGunllod/GrindX/commit/789cb7ac5f6a4283c3e3928753addcd7f5e95446))


## v1.10.1 (2026-05-25)

### Bug Fixes

- **portal**: Add from_attributes to ModuloSchema
  ([`46d859c`](https://github.com/TyrGunllod/GrindX/commit/46d859c65cc4ab6095104694b53eb9881443de90))


## v1.10.0 (2026-05-25)

### Bug Fixes

- **portal**: Build tree with Pydantic objects to avoid ORM mutation
  ([`61989a4`](https://github.com/TyrGunllod/GrindX/commit/61989a4d4ca87e959e200b8b53c30b078dd100ec))

- **portal**: Change children cascade to prevent orphan deletion on reparent
  ([`729d334`](https://github.com/TyrGunllod/GrindX/commit/729d334e75c32f0cced70d7fdd92d5132720a620))

### Code Style

- Format portal_router.py with ruff
  ([`b106eb9`](https://github.com/TyrGunllod/GrindX/commit/b106eb9f85252394fc4915ab8f0acd599e2506ae))

### Features

- **api**: Adicionar suporte a parent_id nas rotas de abas
  ([`930bd5f`](https://github.com/TyrGunllod/GrindX/commit/930bd5f902ee55b7837bf0f98c032ebd8866fac7))

- **dashboard**: Recursive sidebar rendering with sub-aba groups
  ([`96da4bf`](https://github.com/TyrGunllod/GrindX/commit/96da4bf347321e0e5a25ff7d7e968af14c72b55c))

- **portal**: Add alembic migration for parent_id column
  ([`4086a86`](https://github.com/TyrGunllod/GrindX/commit/4086a866247368c76af641cda8a357818cbfd5db))

- **portal**: Add parent_id to aba CRUD endpoints with cycle detection
  ([`e333474`](https://github.com/TyrGunllod/GrindX/commit/e333474b4e07d2a9f84fc1507ad35211062abb71))

- **portal**: Add parent_id to Aba model for nested hierarchy
  ([`efbfcea`](https://github.com/TyrGunllod/GrindX/commit/efbfceacf955e332486ccd513a6b61f66e1a1c78))

- **portal**: Tornar AbaResponse recursivo com parent_id e children
  ([`4a6efd4`](https://github.com/TyrGunllod/GrindX/commit/4a6efd4618718092a8a35bc3174d5edaf2d47fd3))

- **structure**: Nested card styles for sub-abas
  ([`ea8f89e`](https://github.com/TyrGunllod/GrindX/commit/ea8f89e25a6db4e632e01e2fed9328fc8d12f881))

- **structure**: Recursive render, parent_id form, hierarchical select for sub-abas
  ([`797b5d9`](https://github.com/TyrGunllod/GrindX/commit/797b5d93cb20ee5ef1cff32711c1e188e5315bdf))


## v1.9.0 (2026-05-25)

### Bug Fixes

- **auth**: Carregar perfil do usuario logado sem depender de role admin
  ([`2574dc9`](https://github.com/TyrGunllod/GrindX/commit/2574dc987017b022efdd05401d94b2666fbc97bb))

### Code Style

- Format auth router and service with ruff
  ([`fa66eea`](https://github.com/TyrGunllod/GrindX/commit/fa66eea72e1971a7eba5918d8c2ab1fd6d4e81ce))

- **auth**: Organizar imports no router de autenticacao
  ([`de07b5a`](https://github.com/TyrGunllod/GrindX/commit/de07b5a3546d300f517d8b401db46bd444a5c967))

### Features

- **auth**: Add change password endpoint and avatar redesign
  ([`3b800e3`](https://github.com/TyrGunllod/GrindX/commit/3b800e3a1f59ba9ee6bbd32d883a8cabf5790e3f))


## v1.8.1 (2026-05-25)

### Bug Fixes

- **structure**: Aba_id nao era enviado ao editar modulo
  ([`51bb341`](https://github.com/TyrGunllod/GrindX/commit/51bb341198d61aa3cc1cc7330f6b2c38e8d90d32))


## v1.8.0 (2026-05-25)

### Bug Fixes

- **skins**: Cross-origin iframe seguro e fonte herdada nos botoes
  ([`7f0a88d`](https://github.com/TyrGunllod/GrindX/commit/7f0a88da5024a1e083b6d30726d712248deff3fe))

- **structure**: Permitir URL externa no campo url do modulo
  ([`951f84a`](https://github.com/TyrGunllod/GrindX/commit/951f84ad6e7f5ea1c8a4e3b10b3f8e604240508e))

### Features

- **skins**: Adicionar importacao de fontes personalizadas
  ([`ff259ac`](https://github.com/TyrGunllod/GrindX/commit/ff259ac6cc4642c69b5343c4912d0f83864dc479))

- **skins**: Importar fontes de arquivo ZIP com nome automatico
  ([`2e06ff9`](https://github.com/TyrGunllod/GrindX/commit/2e06ff922adcc3ef57afb48bb72a8a985602988c))

- **skins**: Upload fontes para o servidor e corrigir aplicacao em iframes
  ([`95cdbae`](https://github.com/TyrGunllod/GrindX/commit/95cdbae40e1adf5d527b5bc45e75a8c3d32df9d4))

### Refactoring

- **skins**: Fontes lado a lado e remover lista de fontes importadas
  ([`23a0bee`](https://github.com/TyrGunllod/GrindX/commit/23a0bee0a5618456d5c8b72e93628c4dc5530625))


## v1.7.0 (2026-05-24)


## v1.6.0 (2026-05-24)


## v1.5.0 (2026-05-24)

### Documentation

- Atualizar documentacao para estado atual do projeto
  ([`b5d9738`](https://github.com/TyrGunllod/GrindX/commit/b5d973886cf5bce7cedbaa3afb87698542e8d2c8))

### Features

- **seed**: Criar database PostgreSQL automaticamente se nao existir
  ([`8f03696`](https://github.com/TyrGunllod/GrindX/commit/8f0369632085dbfcd910561056423d81dfb5b48e))


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

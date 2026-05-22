# CHANGELOG

<!-- version list -->

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

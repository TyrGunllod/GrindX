# Guia de Deploy — GrindX

O projeto GrindX foi projetado para containerização (utilizando `podman-compose` ou `docker-compose`).

## 🐳 Estratégia de Deploy

1. **Produção (Docker/Podman):**
   - Utilize o `podman-compose.yml` na raiz para orquestrar os serviços.
   - As imagens devem ser construídas baseadas nos `Containerfile` contidos em cada pasta de pacote.

2. **Variáveis de Ambiente:**
   - Em produção, nunca utilize o arquivo `.env` de desenvolvimento. Configure as variáveis de ambiente diretamente no orquestrador (Docker Secrets, Kuberenetes ConfigMaps, etc).

3. **Migrações:**
   - Sempre execute as migrações (`manage_db.py upgrade head`) antes de iniciar os containers da API em uma nova versão.

4. **SSL/HTTPS:**
   - O GrindX deve rodar atrás de um Reverse Proxy (Nginx, Traefik) para garantir terminação SSL e proteção contra ataques comuns.

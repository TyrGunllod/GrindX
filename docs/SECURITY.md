# Guia de Segurança — GrindX

A segurança no GrindX é implementada em múltiplas camadas.

## 🔐 Autenticação (JWT)
- O sistema utiliza **JSON Web Tokens (JWT)** para autenticação stateless.
- O `AccessToken` possui tempo de expiração curto.
- O `RefreshToken` permite renovar a sessão sem necessidade de re-autenticação.

## 👤 Controle de Acesso (RBAC)
- O acesso aos recursos é controlado por **Role-Based Access Control (RBAC)**.
- Os perfis definidos (Admin, Operador) restringem a execução de métodos (GET, POST, PUT, DELETE) baseados no endpoint.

## 🛡️ Melhores Práticas
- **Hashing de Senha:** Todas as senhas são armazenadas com hash utilizando algoritmos seguros (bcrypt).
- **Proteção contra ataques:** Middlewares em FastAPI implementam proteção básica contra injeções, cabeçalhos de segurança (Security Headers) e limitação de taxa (Rate Limiting) para evitar DoS.

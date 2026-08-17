# GrindX Agente IA

Assistente de IA (RAG) que responde perguntas sobre os manuais do ERP GrindX.

## Endpoints

- `GET  /health` — health check
- `POST /v1/agente/chat` — pergunta + módulo → resposta com fontes
- `POST /v1/agente/manuais` — ingestão de manual Markdown por módulo
- `GET  /v1/agente/modulos` — lista módulos indexados

## Execução local

```bash
pip install -r requirements.txt
copy .env.example .env   # preencher DATABASE_URL e DEEPSEEK_API_KEY
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## Testes

```bash
python -m pytest tests/ -v
```

FROM python:3.12-slim

RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

COPY apps/api-postgres/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api-postgres/app/ app/
COPY packages/ packages/

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]

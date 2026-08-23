"""Schemas Pydantic de requisição e resposta da API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    module: str = Field(default="", max_length=120)


class Source(BaseModel):
    filename: str
    title: str
    module: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    used_fallback: bool
    found: bool


class IngestRequest(BaseModel):
    module: str = Field(min_length=1, max_length=120)
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class IngestResponse(BaseModel):
    chunks: int


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    database: dict
    timestamp: str

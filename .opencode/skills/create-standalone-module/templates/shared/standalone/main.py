from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.{module_name}.routers.{module_name}_router import router as {module_name}_router

app = FastAPI(title="{entity_name} API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router({module_name}_router)

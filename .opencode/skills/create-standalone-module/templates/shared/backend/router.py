from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from shared.schemas.base import ErrorResponse, MessageResponse, PaginatedResponse

from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Response, {entity_name}Update
from app.modules.{module_name}.services.{module_name}_service import {entity_name}Service
from app.modules.{module_name}.repositories.{module_name}_repository import {entity_name}Repository

try:
    from app.database import get_db
    from app.auth.dependencies import get_current_user as _auth_dependency
    _grindx_mode = True
except ImportError:
    from app.core.database_protheus import get_db_protheus as get_db
    from app.core.auth import verify_api_key as _auth_dependency
    _grindx_mode = False

router = APIRouter(prefix="{route_prefix}", tags=["{route_tag}"])


def get_{module_name}_service(db: Session = Depends(get_db)) -> {entity_name}Service:
    repository = {entity_name}Repository(db)
    return {entity_name}Service(repository)


@router.get("", response_model=PaginatedResponse[{entity_name}Response],
    summary="Listar", dependencies=[Depends(_auth_dependency)])
def listar(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.listar(page, page_size)


@router.get("/{id}", response_model={entity_name}Response,
    summary="Buscar por ID", responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(_auth_dependency)])
def buscar(id: int, service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.buscar(id)


@router.post("", response_model={entity_name}Response, status_code=201,
    summary="Criar", responses={409: {"model": ErrorResponse}},
    dependencies=[Depends(_auth_dependency)])
def criar(dados: {entity_name}Create, service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.criar(dados)


@router.put("/{id}", response_model={entity_name}Response,
    summary="Atualizar", responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(_auth_dependency)])
def atualizar(id: int, dados: {entity_name}Update, service: {entity_name}Service = Depends(get_{module_name}_service)):
    return service.atualizar(id, dados)


@router.delete("/{id}", response_model=MessageResponse,
    summary="Desativar", responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(_auth_dependency)])
def desativar(id: int, service: {entity_name}Service = Depends(get_{module_name}_service)):
    service.desativar(id)
    return MessageResponse(message=f"{entity_name} {id} desativado com sucesso.")

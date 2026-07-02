"""
Routers de consulta externa — proxies para APIs sem CORS.

Evita problemas de CORS ao buscar dados de CBO e CEP diretamente do frontend.
"""

from urllib import request as urllib_request
from urllib.error import URLError

from fastapi import APIRouter, HTTPException
from starlette.responses import Response

router = APIRouter(prefix="/v1", tags=["Proxies"])

CBO_URL = "https://sistemas.unasus.gov.br/ws_cbo/cbo.php"
CEP_URL = "https://opencep.com/v1"


@router.get("/cbo/{codigo}", summary="Consultar descrição de CBO")
def consultar_cbo(codigo: str):
    url = f"{CBO_URL}?cbo={codigo}"
    try:
        with urllib_request.urlopen(url, timeout=10) as r:
            return Response(content=r.read(), media_type="text/xml")
    except URLError:
        raise HTTPException(status_code=502, detail="Erro ao consultar API de CBO")


@router.get("/cep/{cep}", summary="Consultar endereço por CEP")
def consultar_cep(cep: str):
    url = f"{CEP_URL}/{cep}"
    try:
        with urllib_request.urlopen(url, timeout=10) as r:
            return Response(content=r.read(), media_type="application/json")
    except URLError:
        raise HTTPException(status_code=502, detail="Erro ao consultar API de CEP")

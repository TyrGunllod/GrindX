"""
Router de consulta CBO — proxy para API externa do UNASUS.

Evita problemas de CORS ao buscar dados de CBO diretamente do frontend.
"""

from urllib import request as urllib_request
from urllib.error import URLError

from fastapi import APIRouter, HTTPException
from starlette.responses import Response

router = APIRouter(prefix="/v1/cbo", tags=["CBO"])

CBO_URL = "https://sistemas.unasus.gov.br/ws_cbo/cbo.php"


@router.get("/{cbo}", summary="Consultar descrição de CBO")
def consultar_cbo(cbo: str):
    url = f"{CBO_URL}?cbo={cbo}"
    try:
        with urllib_request.urlopen(url, timeout=10) as r:
            return Response(content=r.read(), media_type="text/xml")
    except URLError:
        raise HTTPException(status_code=502, detail="Erro ao consultar API de CBO")

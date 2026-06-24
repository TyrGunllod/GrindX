from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from app.modules.custo.repositories.custo_produto_repository import (
    CustoProdutoRepository,
)
from app.modules.custo.services.custo_produto_service import CustoProdutoService
from app.modules.custo.schemas.custo_produto import (
    CustoProdutoRangeResponse,
)
from sqlalchemy.orm import Session

try:
    from app.database import get_db

    _grindx_mode = True
except ImportError:
    from app.core.database_protheus import get_db_protheus as get_db

    _grindx_mode = False

try:
    from app.auth.dependencies import get_current_user as _auth_dependency
except ImportError:
    try:
        from app.core.auth import verify_api_key as _auth_dependency
    except ImportError:

        async def _auth_dependency():
            pass


try:
    from app.modules.custo.services.custo_produto_pdf_service import (
        gerar_pdf,
        gerar_pdf_range,
    )

    _pdf_disponivel = True
except ModuleNotFoundError:
    _pdf_disponivel = False

router = APIRouter(prefix="/v1/produtos/custos", tags=["Custo Produto"])


def get_custo_produto_service(db: Session = Depends(get_db)) -> CustoProdutoService:
    repository = CustoProdutoRepository(db)
    return CustoProdutoService(repository)


@router.get("/range", response_model=CustoProdutoRangeResponse)
def calcular_range(
    inicial: str = Query(...),
    final: str = Query(...),
    service: CustoProdutoService = Depends(get_custo_produto_service),
    auth=Depends(_auth_dependency),
):
    return service.calcular_range(inicial, final)


@router.get("/range/pdf")
def pdf_range(
    inicial: str = Query(...),
    final: str = Query(...),
    service: CustoProdutoService = Depends(get_custo_produto_service),
    auth=Depends(_auth_dependency),
):
    if not _pdf_disponivel:
        raise HTTPException(
            status_code=500,
            detail="xhtml2pdf não instalado. Execute: pip install xhtml2pdf",
        )
    result = service.calcular_range(inicial, final)
    pdf_bytes = gerar_pdf_range(inicial, final, result.produtos)
    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={inicial}-{final}_resumido.pdf"
        },
    )


@router.get("/{codigo}")
def calcular(
    codigo: str,
    service: CustoProdutoService = Depends(get_custo_produto_service),
    auth=Depends(_auth_dependency),
):
    return service.calcular(codigo)


@router.get("/{codigo}/pdf")
def pdf_single(
    codigo: str,
    service: CustoProdutoService = Depends(get_custo_produto_service),
    auth=Depends(_auth_dependency),
):
    if not _pdf_disponivel:
        raise HTTPException(
            status_code=500,
            detail="xhtml2pdf não instalado. Execute: pip install xhtml2pdf",
        )
    data = service.calcular(codigo)
    pdf_bytes = gerar_pdf(data)
    filename = f"{data.codigo}-{data.descricao.replace(' ', '_')}.pdf"
    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

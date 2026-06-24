import locale
from datetime import datetime
from io import BytesIO

from xhtml2pdf import pisa

from app.modules.custo.schemas.custo_produto import CustoProdutoResponse

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


def _fmt(n: float, dec: int = 2) -> str:
    return f"R$ {n:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_qty(n: float) -> str:
    return f"{n:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _build_html_range(
    inicial: str, final: str, produtos: list[CustoProdutoResponse]
) -> str:
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    rows = ""
    for p in produtos:
        rows += f"""<tr>
            <td width="17%" valign="middle" style="padding:3px 6px;border:1px solid #999;font-size:11px;text-align:center">{p.codigo}</td>
            <td width="61%" valign="middle" style="padding:3px 6px;border:1px solid #999;font-size:11px">{p.descricao[:35]}</td>
            <td width="22%" valign="middle" style="padding:3px 6px;border:1px solid #999;font-size:11px;text-align:center">{_fmt(p.custo_total)}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head><body style="font-family:Arial,sans-serif;padding:20px 20px 0;color:#333;font-size:12px">
<div style="line-height:1">
<h1 style="font-size:18px;margin:0 0 12px 0;text-align:center">Relatório de Custos — Intervalo</h1>
<table style="width:100%;margin:0;padding:0" border="0" cellpadding="0" cellspacing="0">
<tr>
<td style="text-align:left;padding:0;margin:0"><strong>Período:</strong> {inicial} a {final}</td>
<td style="text-align:right;padding:0;margin:0"><strong>Produtos:</strong> {len(produtos)}</td>
</tr>
</table>
</div>
<table style="width:100%;border-collapse:collapse;margin:14px auto 0" border="0" cellpadding="0" cellspacing="0">
<thead><tr style="background:#eaeaea">
<th width="17%" valign="middle" style="padding:4px 6px;border:1px solid #999;font-size:11px;text-align:center">Código</th>
<th width="61%" valign="middle" style="padding:4px 6px;border:1px solid #999;font-size:11px;text-align:center">Descrição</th>
<th width="22%" valign="middle" style="padding:4px 6px;border:1px solid #999;font-size:11px;text-align:center">Custo Total</th>
</tr></thead>
<tbody>{rows}</tbody></table>
<div style="text-align:right;font-size:9px;color:#888;margin-top:20px">Emitido em: {now}</div>
</body></html>"""


def _build_html(data: CustoProdutoResponse) -> str:
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    rows = ""
    if data.componentes:
        for c in data.componentes:
            rows += f"""<tr>
                <td width="11%" valign="middle" style="padding:2px 4px;border:1px solid #999;font-size:10px;text-align:center">{c.codigo}</td>
                <td width="49%" valign="middle" style="padding:2px 4px;border:1px solid #999;font-size:10px">{c.descricao[:35]}</td>
                <td width="13%" valign="middle" style="padding:2px 4px;border:1px solid #999;font-size:10px;text-align:center">{_fmt_qty(c.quantidade)}</td>
                <td width="13%" valign="middle" style="padding:2px 4px;border:1px solid #999;font-size:10px;text-align:center">{_fmt(c.custo_standard, 4)}</td>
                <td width="14%" valign="middle" style="padding:2px 4px;border:1px solid #999;font-size:10px;text-align:center">{_fmt(c.custo_total)}</td>
            </tr>"""

    table = (
        f"""<table style="width:100%;border-collapse:collapse;margin:14px auto 0" border="0" cellpadding="0" cellspacing="0">
<thead><tr style="background:#eaeaea">
<th width="11%" valign="middle" style="padding:3px 4px;border:1px solid #999;font-size:10px;text-align:center">Código</th>
<th width="49%" valign="middle" style="padding:3px 4px;border:1px solid #999;font-size:10px;text-align:center">Descrição</th>
<th width="13%" valign="middle" style="padding:3px 4px;border:1px solid #999;font-size:10px;text-align:center">Quantidade</th>
<th width="13%" valign="middle" style="padding:3px 4px;border:1px solid #999;font-size:10px;text-align:center">Valor</th>
<th width="14%" valign="middle" style="padding:3px 4px;border:1px solid #999;font-size:10px;text-align:center">Valor Total</th>
</tr></thead>
<tbody>{rows}</tbody></table>"""
        if rows
        else ""
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head><body style="font-family:Arial,sans-serif;padding:20px 20px 0;color:#333;font-size:11px">
<div style="line-height:1">
<h1 style="font-size:16px;margin:0 0 12px 0;text-align:center">Relatório de Custo: {data.codigo}</h1>
<table style="width:100%;margin:0;padding:0" border="0" cellpadding="0" cellspacing="0">
<tr>
<td style="text-align:left;padding:0;margin:0"><strong>Descrição:</strong> {data.descricao}</td>
<td style="text-align:right;padding:0;margin:0"><strong>Custo Total:</strong> {_fmt(data.custo_total)}</td>
</tr>
</table>
</div>
{table}
<div style="text-align:right;font-size:9px;color:#888;margin-top:20px">Emitido em: {now}</div>
</body></html>"""


def gerar_pdf(data: CustoProdutoResponse) -> bytes:
    html = _build_html(data)
    buf = BytesIO()
    pisa.CreatePDF(html, dest=buf)
    return buf.getvalue()


def gerar_pdf_range(
    inicial: str, final: str, produtos: list[CustoProdutoResponse]
) -> bytes:
    html = _build_html_range(inicial, final, produtos)
    buf = BytesIO()
    pisa.CreatePDF(html, dest=buf)
    return buf.getvalue()

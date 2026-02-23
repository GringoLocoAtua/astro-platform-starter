from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))

from core.industry_registry import IndustryRegistry
from core.quote_builder import build_quote
from export.pdf_generator import generate_quote_pdf

app = FastAPI(title="SnapQuote API")
registry = IndustryRegistry()


class QuotePayload(BaseModel):
    industry_id: str
    region: str = "DEFAULT"
    urgency: str = "standard"
    rooms: int = 0
    bathrooms: int = 0
    quantity_fields: dict = Field(default_factory=dict)
    selected_addons: list[str] = Field(default_factory=list)
    scope_text: str = ""
    image_paths: list[str] = Field(default_factory=list)
    tier: str = "FREE"
    client_name: str = ""
    client_email: str = ""


class PdfPayload(BaseModel):
    quote_result: dict
    tier: str = "FREE"
    industry_name: str = "Generic"
    scope_text: str = ""
    show_footer: bool = False


@app.get('/health')
def health() -> dict:
    return {"ok": True}


@app.get('/industries')
def industries() -> list[dict]:
    return registry.list_industries()


@app.post('/quote')
def quote(payload: QuotePayload) -> dict:
    result = build_quote(payload.model_dump())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post('/export/pdf')
def export_pdf(payload: PdfPayload):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as fp:
        output = generate_quote_pdf(
            quote=payload.quote_result,
            output_path=fp.name,
            industry_name=payload.industry_name,
            scope_text=payload.scope_text,
            tier=payload.tier,
            show_footer=payload.show_footer,
        )
    return FileResponse(output, media_type="application/pdf", filename="quote.pdf")

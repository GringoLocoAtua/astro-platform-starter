from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from export.watermark import draw_free_watermark


def _truncate(text: str, max_len: int) -> str:
    text = text or ""
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def generate_quote_pdf(quote: dict, output_path: str, industry_name: str, scope_text: str, tier: str = "FREE", show_footer: bool = False) -> str:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output), pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 45, "SnapQuote™")
    c.setFont("Helvetica", 11)
    c.drawString(40, height - 65, f"Industry: {industry_name}")
    c.drawString(40, height - 82, f"Generated: {datetime.now().isoformat(timespec='seconds')}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 115, "Scope")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 130, _truncate(scope_text, 115))

    y = height - 160
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Breakdown")
    y -= 18
    c.setFont("Helvetica", 10)
    for idx, item in enumerate(quote.get("breakdown", [])[:16], start=1):
        line = f"{idx}. {item.get('item', '')}: {quote.get('currency', 'AUD')} {item.get('amount', 0):.2f}"
        c.drawString(45, y, _truncate(line, 120))
        y -= 14

    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, 90, f"Total: {quote.get('currency', 'AUD')} {quote.get('total', 0):.2f}")

    if tier.upper() == "FREE":
        draw_free_watermark(c, width, height)
        c.setFont("Helvetica", 8)
        c.drawRightString(width - 40, 30, "Powered by BU1ST SnapQuote™")
    elif show_footer:
        c.setFont("Helvetica", 8)
        c.drawRightString(width - 40, 30, "Generated with SnapQuote Pro")

    c.showPage()
    c.save()
    return str(output)

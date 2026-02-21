from __future__ import annotations

from reportlab.lib.colors import Color


def draw_free_watermark(canvas, page_width: float, page_height: float) -> None:
    canvas.saveState()
    canvas.setFillColor(Color(0.7, 0.7, 0.7, alpha=0.15))
    canvas.translate(page_width / 2, page_height / 2)
    canvas.rotate(35)
    canvas.setFont("Helvetica-Bold", 42)
    canvas.drawCentredString(0, 0, "FREE TIER")
    canvas.restoreState()

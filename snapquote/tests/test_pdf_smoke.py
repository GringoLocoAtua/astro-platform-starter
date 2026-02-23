from export.pdf_generator import generate_quote_pdf


def test_pdf_smoke_free_and_pro(tmp_path):
    quote = {
        'currency': 'AUD',
        'total': 123.45,
        'breakdown': [{'item': 'Base Service', 'amount': 100.0}],
    }
    free_pdf = tmp_path / 'quote-free.pdf'
    generate_quote_pdf(quote, str(free_pdf), 'Cleaning', 'basic clean', tier='FREE', settings={'pdf': {'watermark_enabled': True}})
    assert free_pdf.exists()
    assert free_pdf.stat().st_size > 0

    pro_pdf = tmp_path / 'quote-pro.pdf'
    generate_quote_pdf(quote, str(pro_pdf), 'Cleaning', 'basic clean', tier='PRO', settings={'pdf': {'show_footer': False}})
    assert pro_pdf.exists()
    assert pro_pdf.stat().st_size > 0

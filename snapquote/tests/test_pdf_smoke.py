from export.pdf_generator import generate_quote_pdf


def test_pdf_smoke(tmp_path):
    quote = {
        'currency': 'AUD',
        'total': 123.45,
        'breakdown': [{'item': 'Base Service', 'amount': 100.0}],
    }
    output = tmp_path / 'quote.pdf'
    generate_quote_pdf(quote, str(output), 'Cleaning', 'basic clean', tier='FREE')
    assert output.exists()
    assert output.stat().st_size > 0

from core.industry_registry import IndustryRegistry
from core.pricing_engine import calculate_quote
from core.validation import QuoteRequest


def test_deterministic_total():
    reg = IndustryRegistry()
    req = QuoteRequest(industry_id='cleaning', region='NSW', urgency='standard', rooms=2, bathrooms=1, selected_addons=['oven'])
    result = calculate_quote(req, reg, [])
    assert result['total'] == 303.56


def test_heavy_dirt_multiplier_applied():
    reg = IndustryRegistry()
    req = QuoteRequest(industry_id='cleaning', region='DEFAULT', urgency='standard', rooms=0, bathrooms=0)
    result = calculate_quote(req, reg, ['heavy_dirt'])
    assert any('Heavy Dirt Uplift' in b['item'] for b in result['breakdown'])


def test_addon_auto_inclusion_from_tag():
    reg = IndustryRegistry()
    req = QuoteRequest(industry_id='cleaning', region='DEFAULT', urgency='standard')
    result = calculate_quote(req, reg, ['oven'])
    assert any('Tag Addon: oven' == b['item'] for b in result['breakdown'])


def test_region_urgency_order():
    reg = IndustryRegistry()
    req = QuoteRequest(industry_id='cleaning', region='NSW', urgency='urgent')
    result = calculate_quote(req, reg, [])
    assert result['subtotal'] == 144.9


def test_recurring_discount_applied():
    reg = IndustryRegistry()
    req = QuoteRequest(industry_id='cleaning', region='DEFAULT', urgency='standard', scope_text='weekly cleaning required')
    result = calculate_quote(req, reg, [])
    assert result['discounts'] > 0

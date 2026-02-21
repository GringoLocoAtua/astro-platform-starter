from core.quote_builder import build_quote


def test_unconfirmed_detected_tag_not_applied():
    request = {
        "industry_id": "cleaning",
        "region": "DEFAULT",
        "urgency": "standard",
        "rooms": 0,
        "bathrooms": 0,
        "quantity_fields": {},
        "selected_addons": [],
        "scope_text": "",
        "image_paths": [],
        "tier": "FREE",
        "client_name": "",
        "client_email": "",
    }
    result = build_quote(request, confirmed_tags=[])
    assert all("oven" not in item["item"].lower() for item in result["breakdown"])
    assert result["total"] == 141.6

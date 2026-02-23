from core.industry_registry import IndustryRegistry


def test_registry_loads_industries():
    reg = IndustryRegistry()
    items = reg.list_industries()
    assert len(items) >= 4


def test_registry_optional_defaults_safe(tmp_path):
    path = tmp_path / 'industries'
    path.mkdir()
    path.joinpath('x.json').write_text('''{
      "id":"x","name":"X","currency":"AUD","base_rate":1,"hourly_rate":1,
      "inputs":{},"multipliers":{},"addons":{},"tag_rules":{},"margin_default":0.1,
      "region_modifiers":{},"urgency_modifiers":{}
    }''')
    reg = IndustryRegistry(path)
    assert reg.get_industry('x')['id'] == 'x'

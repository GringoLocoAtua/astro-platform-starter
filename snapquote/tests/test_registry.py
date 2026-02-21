from core.industry_registry import IndustryRegistry


def test_registry_loads_industries():
    reg = IndustryRegistry()
    items = reg.list_industries()
    assert len(items) >= 80


def test_registry_optional_defaults_safe(tmp_path):
    path = tmp_path / 'industries'
    path.mkdir()
    path.joinpath('x.json').write_text('{"id":"x","name":"X"}', encoding='utf-8')
    reg = IndustryRegistry(path)
    x = reg.get_industry('x')
    assert x['id'] == 'x'
    assert x['base_rate'] > 0

from core.auth import create_user, verify_user
from core.currency import format_money
from core.settings_store import load_settings, save_settings
from ui.i18n import i18n


def test_settings_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr('core.settings_store.SETTINGS_PATH', tmp_path / 'settings.json')
    monkeypatch.setattr('core.settings_store.DATA_DIR', tmp_path)
    data = load_settings()
    data['language'] = 'es'
    save_settings(data)
    loaded = load_settings()
    assert loaded['language'] == 'es'


def test_auth_create_and_verify(tmp_path, monkeypatch):
    monkeypatch.setattr('core.auth.USERS_PATH', tmp_path / 'users.json')
    monkeypatch.setattr('core.auth.DATA_DIR', tmp_path)
    create_user('admin', 'secret', is_admin=True)
    assert verify_user('admin', 'secret')
    assert not verify_user('admin', 'nope')


def test_currency_format_rules():
    assert format_money(1234.5, 'AUD').endswith('1,234.50')
    assert format_money(1234.5, 'CLP').endswith('1,234')


def test_i18n_fallback():
    i18n.set_language('es')
    assert i18n.tr('btn.generate')
    assert i18n.tr('nonexistent.key') == 'nonexistent.key'
    i18n.set_language('en')

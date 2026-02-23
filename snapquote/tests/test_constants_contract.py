from core.constants import (
    ASSETS_DIR,
    CLIENT_VAULT_PATH,
    DATA_DIR,
    DEFAULT_REGION,
    DEFAULT_TIER,
    DEFAULT_URGENCY,
    INDUSTRIES_DIR,
    ROOT_DIR,
    SETTINGS_PATH,
    SUPPORTED_TIERS,
    SUPPORTED_URGENCY,
    app_root,
    assets_dir,
    data_dir,
    industries_dir,
)


def test_constants_contract_exports():
    assert ROOT_DIR == app_root()
    assert INDUSTRIES_DIR == industries_dir()
    assert ASSETS_DIR == assets_dir()
    assert DATA_DIR == data_dir()
    assert CLIENT_VAULT_PATH.parent == DATA_DIR
    assert SETTINGS_PATH.parent == DATA_DIR
    assert DEFAULT_REGION == 'DEFAULT'
    assert DEFAULT_URGENCY in SUPPORTED_URGENCY
    assert DEFAULT_TIER in SUPPORTED_TIERS

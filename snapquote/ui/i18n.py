from __future__ import annotations

import json

from core.constants import ASSETS_DIR


class I18N:
    def __init__(self) -> None:
        self.language = "en"
        self._cache: dict[str, dict] = {}

    def set_language(self, language: str) -> None:
        self.language = language if language in {"en", "es"} else "en"

    def _load(self, language: str) -> dict:
        if language in self._cache:
            return self._cache[language]
        path = ASSETS_DIR / "locales" / f"{language}.json"
        if not path.exists():
            self._cache[language] = {}
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        self._cache[language] = data
        return data

    def tr(self, key: str) -> str:
        current = self._load(self.language)
        if key in current:
            return current[key]
        en = self._load("en")
        return en.get(key, key)


i18n = I18N()
tr = i18n.tr

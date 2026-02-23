from __future__ import annotations

import json
from datetime import datetime, timezone

from core.constants import RATES_PATH

CURRENCY_META = {
    "AUD": {"symbol": "A$", "decimals": 2},
    "NZD": {"symbol": "NZ$", "decimals": 2},
    "USD": {"symbol": "$", "decimals": 2},
    "EUR": {"symbol": "€", "decimals": 2},
    "GBP": {"symbol": "£", "decimals": 2},
    "CLP": {"symbol": "CLP$", "decimals": 0},
}


def format_money(amount: float, currency_code: str) -> str:
    meta = CURRENCY_META.get(currency_code, CURRENCY_META["AUD"])
    decimals = meta["decimals"]
    fmt = f"{{:,.{decimals}f}}"
    return f"{meta['symbol']}{fmt.format(amount)}"


def load_cached_rates() -> dict:
    if not RATES_PATH.exists():
        return {}
    try:
        return json.loads(RATES_PATH.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}


def save_rates(base: str, rates: dict[str, float]) -> None:
    payload = {"base": base, "rates": rates, "timestamp": datetime.now(timezone.utc).isoformat()}
    RATES_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8-sig")


def fetch_rates(base: str = "AUD") -> dict[str, float]:
    try:
        import requests

        res = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=4)
        res.raise_for_status()
        data = res.json()
        rates = data.get("rates", {})
        if rates:
            save_rates(base, rates)
            return rates
    except Exception:
        pass
    cached = load_cached_rates()
    return cached.get("rates", {})


def convert_amount(amount: float, from_currency: str, to_currency: str, rates: dict[str, float]) -> float | None:
    if from_currency == to_currency:
        return amount
    if not rates:
        return None
    if from_currency != "AUD":
        # use cross via AUD as cache base default
        if from_currency not in rates or to_currency not in rates or rates[from_currency] == 0:
            return None
        aud_amount = amount / rates[from_currency]
        return aud_amount * rates[to_currency]
    if to_currency not in rates:
        return None
    return amount * rates[to_currency]

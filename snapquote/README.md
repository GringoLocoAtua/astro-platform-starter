# SnapQuote v2.2 (Marketplace-Grade)

SnapQuote is an offline-first desktop quoting app with modular pricing, local auth, 80+ industries, live preview, photo tag confirmation, pricing studio, i18n, and multi-currency display.

## Setup (Windows PowerShell)

```powershell
cd snapquote
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Setup (macOS/Linux)

```bash
cd snapquote
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Desktop

```bash
python main.py
```

## Run Tests

```bash
python -m pytest -q
```

## Offline-first notes

- Login is fully local (`data/users.json`), no internet required.
- Currency rates use cached `data/rates.json`; if network is unavailable, app continues in base currency.
- Industry pack auto-seeds from `industries/_catalog.json` and preserves customized industry JSON files.

## Settings overview

- Language: English / Spanish
- Currency: AUD, NZD, USD, EUR, GBP, CLP
- Branding + logo for PRO PDFs
- Security toggle for login requirement + auto-lock minutes
- PDF controls for watermark/footer behavior by tier

## Windows cleanup tip

Use PowerShell-native removal commands:

```powershell
Remove-Item -Recurse -Force .\dist, .\build
```

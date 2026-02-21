# SnapQuote v2.1 (PRO PREMIUM DESKTOP)

SnapQuote v2.1 is an offline-first desktop quoting app with modular pricing JSON, live quote preview, photo tag confirmation, pricing studio versioning, and optional local web blueprint.

## Setup

```bash
cd snapquote
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run desktop

```bash
python main.py
```

Helper scripts:
- macOS/Linux: `./start.sh`
- Windows: `start.bat`

## Run tests

```bash
pytest -q
```

## Desktop v2.1 highlights

- Live quote preview with 350ms debounce.
- Photo panel with thumbnails, detected tags, confirmation checkboxes, and manual tags.
- Pricing Studio tab with versioning (`industries/_versions/<industry_id>/`) and live registry reload.
- Settings tab persisted in `data/settings.json`.
- PDF export:
  - FREE: watermark + `Powered by BU1ST SnapQuote™` footer (unchanged).
  - PRO: optional branding logo and optional footer (default off).

## Optional web backend

```bash
cd web/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

## Optional web frontend

```bash
cd web/frontend
npm install
npm run dev
```

## Build Windows executable (PyInstaller)

```powershell
cd snapquote
powershell -ExecutionPolicy Bypass -File .\package\build_windows.ps1
```

Output app is generated in `dist/SnapQuote/`.

## Offline and AI notes

- Desktop mode works fully offline.
- Optional Ollama integration exists in `ai/ai_bridge.py`; when unavailable it safely returns empty suggestions.
- `assets/logo.png` is a placeholder text file in this scaffold; replacing it with a real PNG is optional.

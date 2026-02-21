# SnapQuote v2

SnapQuote v2 is an offline-first desktop quoting app with modular pricing JSON, a pure pricing engine, PDF export, and optional local web blueprint.

## Setup

```bash
cd snapquote
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run desktop

```bash
python main.py
```

Or use helper scripts:
- macOS/Linux: `./start.sh`
- Windows: `start.bat`

## Run tests

```bash
pytest -q
```

## Optional web backend

```bash
cd web/backend
python3 -m venv .venv
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

## Offline and AI notes

- Desktop mode works fully offline.
- Optional Ollama integration exists in `ai/ai_bridge.py`; when unavailable it safely returns empty suggestions.
- `assets/logo.png` is a placeholder text file in this scaffold; replacing it with a real PNG is optional.

## Dist zip instructions

```bash
cd ..
zip -r dist/snapquote-v2.zip snapquote
```

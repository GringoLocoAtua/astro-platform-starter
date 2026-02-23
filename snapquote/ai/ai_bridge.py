from __future__ import annotations

import json

import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def analyze_scope_text(scope_text: str) -> dict:
    if not scope_text:
        return {"suggested_addons": [], "detected_recurring": False, "confidence": 0.0}
    prompt = (
        "Return JSON with keys suggested_addons(list), detected_recurring(bool), confidence(float 0-1) "
        f"for this service scope: {scope_text}"
    )
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": "llama3.1", "prompt": prompt, "stream": False},
            timeout=2,
        )
        response.raise_for_status()
        text = response.json().get("response", "{}")
        parsed = json.loads(text)
        return {
            "suggested_addons": parsed.get("suggested_addons", []),
            "detected_recurring": bool(parsed.get("detected_recurring", False)),
            "confidence": float(parsed.get("confidence", 0.0)),
        }
    except Exception:
        return {"suggested_addons": [], "detected_recurring": False, "confidence": 0.0}

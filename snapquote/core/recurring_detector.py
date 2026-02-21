from __future__ import annotations

import re

PATTERNS = [r"\bweekly\b", r"\bfortnightly\b", r"\bmonthly\b"]


def is_recurring(scope_text: str) -> bool:
    if not scope_text:
        return False
    text = scope_text.lower()
    return any(re.search(pattern, text) for pattern in PATTERNS)

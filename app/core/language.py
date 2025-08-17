#core/language.py
from typing import Optional
try:
    from langdetect import detect
except Exception:
    detect = None

def detect_language(text: Optional[str]) -> str:
    if not text:
        return "en"
    if detect:
        try:
            code = detect(text)
            # normalize common values
            if code.startswith("ar"):
                return "ar"
            if code.startswith("en"):
                return "en"
            return code
        except Exception:
            return "en"
    return "en"

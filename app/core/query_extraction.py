#query extraction
import re

# basic heuristic: strip leading “show me”, “i want”, Arabic equivalents; keep color + item words
# You can upgrade later with an LLM-based extractor.
STRIP_PATTERNS = [
    r"^\s*(show|find|recommend|i want|i need|please show|أرني|ابحث|أريد|أحتاج)\s+(me\s+)?",
]

def extract_product_query(text: str) -> str:
    q = text.strip().lower()
    for pat in STRIP_PATTERNS:
        q = re.sub(pat, "", q, flags=re.IGNORECASE)
    # remove trailing politeness
    q = re.sub(r"(?:please|من فضلك)\s*$", "", q).strip()
    # minimal cleanup punctuation
    q = re.sub(r"[^\w\s\u0600-\u06FF\-]+", " ", q)  # keep Arabic block
    q = re.sub(r"\s+", " ", q).strip()
    return q

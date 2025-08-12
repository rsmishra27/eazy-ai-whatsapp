# app/core/storage.py
import json
from pathlib import Path
from app.core import config

_storage_path = Path(config.STORAGE_FILE)
_storage_path.parent.mkdir(parents=True, exist_ok=True)

def _read_all():
    if not _storage_path.exists():
        return []
    with _storage_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def _write_all(data):
    with _storage_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def store_transcript(user_id: str, text: str):
    data = _read_all()
    data.append({"user": user_id, "text": text})
    _write_all(data)

def get_transcripts(limit: int = 50):
    data = _read_all()
    return data[-limit:]

# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env in project root if present

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "")

STORAGE_FILE = os.getenv("STORAGE_FILE", "./data/transcripts.json")

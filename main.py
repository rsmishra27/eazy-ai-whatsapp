# main.py
from fastapi import FastAPI
from app.api import whatsapp

app = FastAPI(title="Eazy AI WhatsApp Agent")

app.include_router(whatsapp.router, prefix="")

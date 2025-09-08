# main.py
import os
import sys
from fastapi import FastAPI
from app.api import whatsapp

print("🚀 Starting WhatsApp AI Agent...")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Environment variables loaded: {bool(os.getenv('TWILIO_ACCOUNT_SID'))}")

app = FastAPI(title="Eazy AI WhatsApp Agent")

# Add health check endpoint
@app.get("/health")
async def health_check():
    print("🏥 Health check called")
    try:
        # Test if core modules can be imported (lazy loading will handle model loading)
        from app.core import vector_search
        from app.core import embedding_model
        
        # Try to access the lazy-loaded components
        # This will trigger model loading if not already loaded
        _ = vector_search.get_products()
        
        return {"status": "healthy", "service": "whatsapp-ai-agent", "models": "ready"}
    except Exception as e:
        print(f"⚠️ Health check warning: {e}")
        return {"status": "starting", "service": "whatsapp-ai-agent", "models": "loading"}

@app.get("/")
async def root():
    return {"message": "WhatsApp AI Agent is running"}

print("📱 Loading WhatsApp router...")
app.include_router(whatsapp.router, prefix="")
print("✅ Application setup complete!")

import uvicorn
from fastapi import FastAPI
from app.api.whatsapp import router as whatsapp_router
from app.core.vector_search import initialize_vector_store

app = FastAPI(title="Eazy-AI WhatsApp Chatbot")

@app.on_event("startup")
async def startup_event():
    """Initializes the FAISS vector store on application startup."""
    print("Initializing FAISS vector store...")
    await initialize_vector_store()
    print("FAISS vector store initialized.")

app.include_router(whatsapp_router, prefix="/whatsapp")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
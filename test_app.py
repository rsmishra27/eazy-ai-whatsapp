#!/usr/bin/env python3
"""
Simple test application to debug Docker issues
"""
from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(title="Test App")

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Test app is working"}

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    print("Starting test app...")
    print(f"Environment variables: {os.environ.get('TWILIO_ACCOUNT_SID', 'NOT_SET')}")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

#state.py
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Turn(BaseModel):
    role: str
    content: str

class AgentState(BaseModel):
    # Input
    user_id: str
    text: Optional[str] = None
    media_url: Optional[str] = None
    language: Optional[str] = None  # 'ar', 'en', etc.

    # Derived
    intent: Optional[str] = None           # 'product_search' | 'greeting' | 'faq' | 'smalltalk'
    product_query: Optional[str] = None    # clean extracted query (e.g., 'white t-shirt')
    search_results: Optional[List[Dict[str, Any]]] = None  # products
    llm_reply: Optional[str] = None        # final text reply

    # Meta
    messages: List[Turn] = Field(default_factory=list)     # optional history (lightweight)
    debug: Dict[str, Any] = Field(default_factory=dict)    # for instrumentation

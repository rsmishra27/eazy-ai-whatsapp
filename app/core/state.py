# app/core/state.py
from typing import TypedDict, Optional, Any

class AgentState(TypedDict):
    """Represents the state of the LangGraph agent."""
    user_id: str
    text: str
    language: Optional[str]
    intent: Optional[str]
    query: Optional[str]
    llm_reply: Optional[str]
    debug: Optional[Any]
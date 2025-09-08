# app/core/langgraph_app.py
from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.core.language import detect_language
from app.core.intent import detect_intent_llm
from app.core.query_extraction import extract_query
from app.agents.tools import product_recommend, chat_greet
from typing import Any

def node_normalize(state: AgentState) -> dict:
    """Normalizes the input by detecting language."""
    state['language'] = state.get('language') or detect_language(state['text'])
    if 'debug' not in state:
        state['debug'] = {}
    state['debug']['language'] = state['language']
    return state

def node_intent(state: AgentState) -> dict:
    """Detects the intent of the message."""
    state['intent'] = detect_intent_llm(state['text'], state['language'])
    if 'debug' not in state:
        state['debug'] = {}
    state['debug']['intent'] = state['intent']
    return state

def node_query_extraction(state: AgentState) -> dict:
    """Extracts a search query from the user's text for product recommendation."""
    state['query'] = extract_query(state['text'], state['language'])
    if 'debug' not in state:
        state['debug'] = {}
    state['debug']['query'] = state['query']
    return state

def node_recommend(state: AgentState) -> dict:
    """Calls the product recommendation tool and saves the content to the state."""
    reply = product_recommend(state['query'], state['language'])
    state['llm_reply'] = reply.content
    return state

def node_chat_greet(state: AgentState) -> dict:
    """Calls the general chat/greet tool and saves the content to the state."""
    reply = chat_greet(state['text'], state['language'])
    state['llm_reply'] = reply.content
    return state

def router(state: AgentState) -> str:
    """Routes the graph based on the detected intent."""
    if state['intent'] in ["greet", "smalltalk"]:
        return "chat_greet"
    return "query_extraction"

graph = StateGraph(AgentState)
graph.add_node("normalize", node_normalize)
graph.add_node("intent", node_intent)
graph.add_node("query_extraction", node_query_extraction)
graph.add_node("recommend", node_recommend)
graph.add_node("chat_greet", node_chat_greet)

graph.set_entry_point("normalize")
graph.add_edge("normalize", "intent")
graph.add_conditional_edges("intent", router, {
    "query_extraction": "query_extraction",
    "chat_greet": "chat_greet",
})
graph.add_edge("query_extraction", "recommend")
graph.add_edge("recommend", END)
graph.add_edge("chat_greet", END)

app = graph.compile()

async def run_message(user_id: str, text: str, language: str = None) -> str:
    """Runs a message through the LangGraph and returns the reply."""
    state = AgentState(
        user_id=user_id,
        text=text,
        language=language,
        intent=None,
        query=None,
        llm_reply=None,
        debug={}
    )
    out = await app.ainvoke(state)
    print(f"Final LangGraph output: {out}")
    return out.get("llm_reply", "...")
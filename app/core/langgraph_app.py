# app/core/langgraph_app.py
from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.core.language import detect_language
from app.core.intent import detect_intent_llm
from app.core.query_extraction import extract_query
from app.agents.tools.chat_greet import chat_greet
from FAISSRecommenderTool import FAISSRecommenderTool
from typing import Any

# -----------------------------
# Initialize FAISS Recommender
# -----------------------------
product_recommender = FAISSRecommenderTool(
    dataset_path="electronics_demo_dataset.csv",
    index_path="electronics_demo_index.faiss"
)

# -----------------------------
# Graph nodes
# -----------------------------
def node_normalize(state: AgentState) -> dict:
    """Normalize input and detect language."""
    state['language'] = state.get('language') or detect_language(state['text'])
    state.setdefault('debug', {})['language'] = state['language']
    return state

def node_intent(state: AgentState) -> dict:
    """Detect intent via LLM."""
    state['intent'] = detect_intent_llm(state['text'], state['language'])
    state.setdefault('debug', {})['intent'] = state['intent']
    return state

def node_query_extraction(state: AgentState) -> dict:
    """Extract search query for recommendation."""
    state['query'] = extract_query(state['text'], state['language'])
    state.setdefault('debug', {})['query'] = state['query']
    return state

def node_recommend(state: AgentState) -> dict:
    """Calls the FAISS product recommendation tool and saves a simple string reply."""
    recommendations = product_recommend(state['query'], state['language'])
    
    # Format the recommendations into a readable string
    reply_text = "\n".join([f"{r['title']} ({r['category']})" for r in recommendations])
    
    state['llm_reply'] = reply_text
    return state


def node_chat_greet(state: AgentState) -> dict:
    """Call chat/greet tool."""
    reply = chat_greet(state['text'], state['language'])
    state['llm_reply'] = reply.content
    return state

def router(state: AgentState) -> str:
    """Route based on intent."""
    if state['intent'] in ["greet", "smalltalk"]:
        return "chat_greet"
    return "query_extraction"

# -----------------------------
# Build LangGraph
# -----------------------------
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

# -----------------------------
# Helper for WhatsApp
# -----------------------------
async def run_message(user_id: str, text: str, language: str = None) -> str:
    """Run a user message through LangGraph and return reply."""
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

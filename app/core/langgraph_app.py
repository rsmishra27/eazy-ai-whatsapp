from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.core.language import detect_language
from app.core.intent import detect_intent_llm
from app.agents.tools import product_recommend, chat_greet

def node_normalize(state: AgentState) -> AgentState:
    state.language = state.language or detect_language(state.text)
    state.debug["language"] = state.language
    return state

def node_intent(state: AgentState) -> AgentState:
    state.intent = detect_intent_llm(state.text, state.language)
    state.debug["intent"] = state.intent
    return state

def node_recommend(state: AgentState) -> AgentState:
    reply = product_recommend(state.text, state.language)
    state.llm_reply = reply
    return state

def node_chat_greet(state: AgentState) -> AgentState:
    reply = chat_greet(state.text, state.language)
    state.llm_reply = reply
    return state

def router(state: AgentState) -> str:
    if state.intent == "greet":
        return "chat_greet"
    return "recommend"

graph = StateGraph(AgentState)
graph.add_node("normalize", node_normalize)
graph.add_node("intent", node_intent)
graph.add_node("recommend", node_recommend)
graph.add_node("chat_greet", node_chat_greet)
graph.set_entry_point("normalize")
graph.add_edge("normalize", "intent")
graph.add_conditional_edges("intent", router, {
    "recommend": "recommend",
    "chat_greet": "chat_greet",
})
graph.add_edge("recommend", END)
graph.add_edge("chat_greet", END)

app = graph.compile()

def run_message(user_id: str, text: str, language: str = None) -> str:
    state = AgentState(user_id=user_id, text=text, language=language)
    out = app.invoke(state)
    return out.llm_reply or "..."

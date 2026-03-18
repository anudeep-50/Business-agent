import os
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from personas import AXIOM_SYSTEM, VECTOR_SYSTEM, CIPHER_SYSTEM, PROBE_SYSTEM
from database import insert, load_full_context

# State definition
class FounderState(TypedDict):
    context: dict
    probe_data: str
    axiom_output: str
    vector_task: str
    cipher_review: str
    final_memo: str
    loops: int

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
tavily = TavilySearchResults(max_results=5)

# Nodes
def probe_node(state: FounderState):
    query = "Indian startup market opportunities revenue growth"
    results = tavily.run(query)
    return {**state, "probe_data": results}

def axiom_node(state: FounderState):
    context = load_full_context()
    prompt = AXIOM_SYSTEM + f"\nContext: {context}\nProbe Data: {state['probe_data']}"
    resp = llm.invoke(prompt)
    return {**state, "axiom_output": resp.content}

def vector_node(state: FounderState):
    prompt = VECTOR_SYSTEM + f"\nAxiom said: {state['axiom_output']}\nContext: {state['context']}"
    resp = llm.invoke(prompt)
    return {**state, "vector_task": resp.content}

def cipher_node(state: FounderState):
    prompt = CIPHER_SYSTEM + f"\nVector suggested: {state['vector_task']}\nContext: {state['context']}"
    resp = llm.invoke(prompt)
    return {**state, "cipher_review": resp.content}

def synthesize_node(state: FounderState):
    return {**state, "final_memo": state["vector_task"]}

# Graph
graph = StateGraph(FounderState)

graph.add_node("PROBE", probe_node)
graph.add_node("AXIOM", axiom_node)
graph.add_node("VECTOR", vector_node)
graph.add_node("CIPHER", cipher_node)
graph.add_node("SYNTHESIZE", synthesize_node)

graph.set_entry_point("PROBE")
graph.add_edge("PROBE", "AXIOM")
graph.add_edge("AXIOM", "VECTOR")
graph.add_edge("VECTOR", "CIPHER")

def cipher_condition(state: FounderState) -> Literal["VECTOR", "SYNTHESIZE"]:
    if "reject" in state["cipher_review"].lower() and state["loops"] < 3:
        return "VECTOR"
    return "SYNTHESIZE"

graph.add_conditional_edges("CIPHER", cipher_condition)
graph.add_edge("SYNTHESIZE", END)

app = graph.compile()

# Public functions
def run_deliberation():
    init_state = {"context": load_full_context(), "loops": 0}
    result = app.invoke(init_state)
    return result["final_memo"]

def run_daily_memo():
    init_state = {"context": load_full_context(), "loops": 0}
    result = app.invoke(init_state)
    insert("task_log", task=result["final_memo"], report="", outcome="")
    return result["final_memo"]

def run_research(topic: str):
    results = tavily.run(topic + " India")
    return results

def handle_pushback(report: str):
    insert("lessons", text=report)
    return "Lesson stored."

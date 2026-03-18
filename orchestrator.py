import os
import logging
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from personas import AXIOM_SYSTEM, VECTOR_SYSTEM, CIPHER_SYSTEM, PROBE_SYSTEM
from database import insert, load_full_context

# Configure logging
logging.basicConfig(level=logging.INFO)

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
    logging.info("PROBE node started", extra={"query": query})
    results = tavily.run(query)
    logging.info("PROBE node finished", extra={"result_length": len(results)})
    return {**state, "probe_data": results}

def axiom_node(state: FounderState):
    logging.info("AXIOM node started")
    context = load_full_context()
    prompt = AXIOM_SYSTEM + f"\nContext: {context}\nProbe Data: {state['probe_data']}"
    resp = llm.invoke(prompt)
    logging.info("AXIOM node finished", extra={"output_preview": resp.content[:60]})
    return {**state, "axiom_output": resp.content}

def vector_node(state: FounderState):
    logging.info("VECTOR node started")
    prompt = VECTOR_SYSTEM + f"\nAxiom said: {state['axiom_output']}\nContext: {state['context']}"
    resp = llm.invoke(prompt)
    logging.info("VECTOR node finished", extra={"output_preview": resp.content[:60]})
    return {**state, "vector_task": resp.content}

def cipher_node(state: FounderState):
    logging.info("CIPHER node started", extra={"loops": state.get("loops", 0)})
    prompt = CIPHER_SYSTEM + f"\nVector suggested: {state['vector_task']}\nContext: {state['context']}"
    resp = llm.invoke(prompt)
    logging.info("CIPHER node finished", extra={"decision_preview": resp.content[:60]})
    return {**state, "cipher_review": resp.content}

def synthesize_node(state: FounderState):
    logging.info("SYNTHESIZE node started")
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
        logging.info("CIPHER requested revision", extra={"loops": state["loops"]})
        return "VECTOR"
    logging.info("CIPHER approved, moving to SYNTHESIZE")
    return "SYNTHESIZE"

graph.add_conditional_edges("CIPHER", cipher_condition)
graph.add_edge("SYNTHESIZE", END)

app = graph.compile()

# Public functions
def run_deliberation():
    logging.info("Deliberation started")
    init_state = {"context": load_full_context(), "loops": 0}
    result = app.invoke(init_state)
    logging.info("Deliberation finished", extra={"final_memo_preview": result["final_memo"][:80]})
    return result["final_memo"]

def run_daily_memo():
    logging.info("Daily memo started")
    init_state = {"context": load_full_context(), "loops": 0}
    result = app.invoke(init_state)
    insert("task_log", task=result["final_memo"], report="", outcome="")
    logging.info("Daily memo finished", extra={"final_memo_preview": result["final_memo"][:80]})
    return result["final_memo"]

def run_research(topic: str):
    logging.info("Research started", extra={"topic": topic})
    results = tavily.run(topic + " India")
    logging.info("Research finished", extra={"result_length": len(results)})
    return results

def handle_pushback(report: str):
    logging.info("Pushback logged", extra={"report_preview": report[:80]})
    insert("lessons", text=report)
    return "Lesson stored."

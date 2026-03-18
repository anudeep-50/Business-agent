import logging
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

# Nodes with logging + error handling
def probe_node(state: FounderState):
    logging.info("PROBE node started")
    try:
        query = "Indian startup market opportunities revenue growth"
        results = tavily.run(query)
        logging.info(f"PROBE node finished. Result length: {len(results)}")
        return {**state, "probe_data": results}
    except Exception as e:
        logging.exception("PROBE node failed")
        return {**state, "probe_data": f"ERROR: {e}"}

def axiom_node(state: FounderState):
    logging.info("AXIOM node started")
    try:
        context = load_full_context()
        prompt = AXIOM_SYSTEM + f"\nContext: {context}\nProbe Data: {state['probe_data']}"
        resp = llm.invoke(prompt)
        logging.info(f"AXIOM node finished. Preview: {resp.content[:60]}")
        return {**state, "axiom_output": resp.content}
    except Exception as e:
        logging.exception("AXIOM node failed")
        return {**state, "axiom_output": f"ERROR: {e}"}

def vector_node(state: FounderState):
    logging.info("VECTOR node started")
    try:
        prompt = VECTOR_SYSTEM + f"\nAxiom said: {state['axiom_output']}\nContext: {state['context']}"
        resp = llm.invoke(prompt)
        logging.info(f"VECTOR node finished. Preview: {resp.content[:60]}")
        return {**state, "vector_task": resp.content}
    except Exception as e:
        logging.exception("VECTOR node failed")
        return {**state, "vector_task": f"ERROR: {e}"}

def cipher_node(state: FounderState):
    logging.info(f"CIPHER node started (loop {state.get('loops', 0)})")
    try:
        prompt = CIPHER_SYSTEM + f"\nVector suggested: {state['vector_task']}\nContext: {state['context']}"
        resp = llm.invoke(prompt)
        logging.info(f"CIPHER node finished. Preview: {resp.content[:60]}")
        return {**state, "cipher_review": resp.content}
    except Exception as e:
        logging.exception("CIPHER node failed")
        return {**state, "cipher_review": f"ERROR: {e}"}

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
        logging.info(f"CIPHER requested revision (loop {state['loops']})")
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
    logging.info(f"Deliberation finished. Final memo preview: {result['final_memo'][:80]}")
    return result["final_memo"]

def run_daily_memo():
    logging.info("Daily memo started")
    init_state = {"context": load_full_context(), "loops": 0}
    result = app.invoke(init_state)
    insert("task_log", task=result["final_memo"], report="", outcome="")
    logging.info(f"Daily memo finished. Final memo preview: {result['final_memo'][:80]}")
    return result["final_memo"]

def run_research(topic: str):
    logging.info(f"Research started for topic: {topic}")
    results = tavily.run(topic + " India")
    logging.info(f"Research finished. Result length: {len(results)}")
    return results

def handle_pushback(report: str):
    logging.info(f"Pushback logged. Preview: {report[:80]}")
    insert("lessons", text=report)
    return "Lesson stored."

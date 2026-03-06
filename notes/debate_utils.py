import os
import operator
from typing import TypedDict, Annotated, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langchain_classic.callbacks.tracers import LangChainTracer
from dotenv import load_dotenv


load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
tracer = LangChainTracer(project_name=os.getenv("LANGSMITH_PROJECT"))

# 🔹 1. Define the Graph State
class DebateState(TypedDict):
    topic: str
    context: str             # Adding syllabus context so debaters stay on track!
    history: Annotated[List[str], operator.add]
    debater_models: List[str] 
    judge_model: str           
    round_count: int
    max_rounds: int
    current_speaker_idx: int
    verdict: str

# 🔹 2. Helper to get an LLM instance dynamically
def get_llm(model_name: str):
    return ChatOpenAI(
        model=model_name,
        base_url='https://openrouter.ai/api/v1',
        api_key=os.getenv('OPENROUTER_API_KEY'),
        temperature=0.3,
        callbacks=[tracer]
    )

# 🔹 3. Define the Nodes
def debater_node(state: DebateState):
    """Generic node handling the turn for ANY debater."""
    speaker_idx = state["current_speaker_idx"]
    model_name = state["debater_models"][speaker_idx]
    llm = get_llm(model_name)
    
    transcript = "\n".join(state["history"]) if state["history"] else "No arguments made yet."
    
    # Dynamic stance generation
    stance = (
        "You are an academic AI debater strictly bound by the provided Context. "
        "Use ONLY the terms used in the Context, but you can use outside examples to simplify."
    )
    if speaker_idx == 0 and state["round_count"] == 0:
        stance += " Provide a strong opening argument or explanation for the Topic based on the Context."
    else:
        stance += " Review the history, critique previous points, and offer a refined or counter-perspective based on the Context."

    sys_prompt = SystemMessage(content=stance)
    user_prompt = HumanMessage(
        content=f"Context:\n{state['context']}\n\nTopic: {state['topic']}\n\nDebate History so far:\n{transcript}\n\nProvide your next response."
    )
    
    response = llm.invoke([sys_prompt, user_prompt])
    
    # Format the name for readability
    clean_name = model_name.split('/')[-1]
    message = f"**Debater ({clean_name}):**\n{response.content}"
    
    next_idx = speaker_idx + 1
    next_round = state["round_count"]
    
    if next_idx >= len(state["debater_models"]):
        next_idx = 0
        next_round += 1

    return {
        "history": [message],
        "current_speaker_idx": next_idx,
        "round_count": next_round
    }

def judge_node(state: DebateState):
    """Evaluates the debate using the dynamically selected judge model."""
    judge_model = state["judge_model"]
    llm = get_llm(judge_model)
    
    transcript = "\n\n".join(state["history"])
    
    sys_prompt = SystemMessage(
        content=(
            "You are an impartial AI academic judge. Review the debate transcript and the syllabus context. "
            "Synthesize the best points to give a comprehensive, highly accurate final answer to the user's question. "
            "Do NOT mention the debate, the transcript, or the debaters directly. Just provide the final, polished educational answer."
        )
    )
    
    user_prompt = HumanMessage(
        content=f"Context:\n{state['context']}\n\nQuestion: {state['topic']}\n\nDebate Transcript:\n{transcript}\n\nProvide your final polished answer."
    )
    
    response = llm.invoke([sys_prompt, user_prompt])
    
    # 🔹 Just return the verdict content now
    return {"verdict": response.content}


# 🔹 4. Define Routing & Build Graph
def route_debate(state: DebateState):
    if state["round_count"] >= state["max_rounds"]:
        return "judge"
    return "debater"

def build_debate_graph():
    workflow = StateGraph(DebateState)
    workflow.add_node("debater", debater_node)
    workflow.add_node("judge", judge_node)
    
    workflow.add_edge(START, "debater")
    workflow.add_conditional_edges("debater", route_debate, {"debater": "debater", "judge": "judge"})
    workflow.add_edge("judge", END)
    
    return workflow.compile()

# Instantiate the compiled graph once
debate_app = build_debate_graph()


# ... (keep routing and build graph the same) ...

def run_debate(question: str, context: str, debater_models: list, judge_model: str, max_rounds: int = 1):
    """Helper function to execute the graph from views.py"""
    initial_state = {
        "topic": question,
        "context": context,
        "history": [],
        "debater_models": debater_models,
        "judge_model": judge_model,
        "round_count": 0,
        "max_rounds": max_rounds,
        "current_speaker_idx": 0
    }
    
    result = debate_app.invoke(initial_state)
    
    # 🔹 Return a structured dictionary instead of just a string
    return {
        "verdict": result["verdict"],
        "transcript": result["history"]  # This is a list of strings
    }
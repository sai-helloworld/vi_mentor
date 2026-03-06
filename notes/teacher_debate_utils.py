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

# 🔹 1. Graph State (Now includes past chat context)
class TeacherDebateState(TypedDict):
    topic: str
    chat_context: str          # <--- NEW: Holds past 5 messages
    history: Annotated[List[str], operator.add]
    debater_models: List[str] 
    judge_model: str           
    round_count: int
    max_rounds: int
    current_speaker_idx: int
    verdict: str

def get_llm(model_name: str):
    return ChatOpenAI(
        model=model_name,
        base_url='https://openrouter.ai/api/v1',
        api_key=os.getenv('OPENROUTER_API_KEY'),
        temperature=0.4, 
        callbacks=[tracer]
    )

# 🔹 2. Nodes
def debater_node(state: TeacherDebateState):
    speaker_idx = state["current_speaker_idx"]
    model_name = state["debater_models"][speaker_idx]
    llm = get_llm(model_name)
    
    transcript = "\n".join(state["history"]) if state["history"] else "No arguments made yet."
    
    stance = "You are an AI debater assisting a teacher. Use your general knowledge to provide accurate, logical, and educational arguments. "
    if speaker_idx == 0 and state["round_count"] == 0:
        stance += "Provide a strong opening argument or explanation for the Topic."
    else:
        stance += "Review the history, critique previous points, and offer a refined or counter-perspective."

    sys_prompt = SystemMessage(content=stance)
    
    # 🔹 Inject the past 5 messages into the user prompt
    context_block = f"Previous Conversation Context:\n{state['chat_context']}\n\n" if state.get('chat_context') else ""
    user_prompt = HumanMessage(
        content=f"{context_block}Topic: {state['topic']}\n\nDebate History so far:\n{transcript}\n\nProvide your next response."
    )
    
    response = llm.invoke([sys_prompt, user_prompt])
    
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

def judge_node(state: TeacherDebateState):
    judge_model = state["judge_model"]
    llm = get_llm(judge_model)
    transcript = "\n\n".join(state["history"])
    
    sys_prompt = SystemMessage(
        content=(
            "You are an impartial AI judge assisting a teacher. Review the debate transcript. "
            "Synthesize the best points to give a comprehensive, highly accurate final answer to the teacher's question. "
            "Do NOT mention the debate, the transcript, or the debaters directly. Just provide the final, polished answer."
        )
    )
    
    # 🔹 Inject past 5 messages for the judge too
    context_block = f"Previous Conversation Context:\n{state['chat_context']}\n\n" if state.get('chat_context') else ""
    user_prompt = HumanMessage(
        content=f"{context_block}Question: {state['topic']}\n\nDebate Transcript:\n{transcript}\n\nProvide your final polished answer."
    )
    
    response = llm.invoke([sys_prompt, user_prompt])
    return {"verdict": response.content}

# 🔹 3. Routing & Build
def route_debate(state: TeacherDebateState):
    if state["round_count"] >= state["max_rounds"]:
        return "judge"
    return "debater"

def build_teacher_debate_graph():
    workflow = StateGraph(TeacherDebateState)
    workflow.add_node("debater", debater_node)
    workflow.add_node("judge", judge_node)
    workflow.add_edge(START, "debater")
    workflow.add_conditional_edges("debater", route_debate, {"debater": "debater", "judge": "judge"})
    workflow.add_edge("judge", END)
    return workflow.compile()

teacher_debate_app = build_teacher_debate_graph()

# 🔹 Updated Helper Function
def run_teacher_debate(question: str, chat_context: str, debater_models: list, judge_model: str, max_rounds: int = 1):
    initial_state = {
        "topic": question,
        "chat_context": chat_context, # <--- Pass it into the state
        "history": [],
        "debater_models": debater_models,
        "judge_model": judge_model,
        "round_count": 0,
        "max_rounds": max_rounds,
        "current_speaker_idx": 0
    }
    result = teacher_debate_app.invoke(initial_state)
    return {
        "verdict": result["verdict"],
        "transcript": result["history"]
    }
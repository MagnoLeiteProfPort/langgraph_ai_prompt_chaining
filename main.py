from typing_extensions import TypedDict
from typing import Dict, Any
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
import os
import getpass
import dotenv

# --- Env setup ---

dotenv.load_dotenv()  # Load .env into os.environ

def _set_env(var: str):
    """Ensure an env var is set, ask interactively if missing."""
    if var not in os.environ or not os.environ[var]:
        os.environ[var] = getpass.getpass(f"Enter value for {var}: ")

_set_env("ANTHROPIC_API_KEY")

# --- LLM ---

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
)

# --- Graph State ---

class State(TypedDict, total=False):
    topic: str
    letter: str
    word: str
    phrase: str
    relevant: bool  # set by the checker


# --- Nodes ---

def generate_letter(state: State) -> Dict[str, Any]:
    """Generates a letter based on the topic."""
    topic = state.get("topic") or "Football"
    prompt = f"Generate a single letter that could start a word about the topic '{topic}'. Just return the letter."
    msg = llm.invoke(prompt)
    # msg.content may be a string or list; str(...) is safe
    letter = str(msg.content).strip()[0]
    return {"topic": topic, "letter": letter}


def generate_word(state: State) -> Dict[str, Any]:
    """Generates a word based on the letter and topic."""
    topic = state["topic"]
    letter = state["letter"]
    prompt = (
        f"Generate a single word about the topic '{topic}' that starts with the letter '{letter}'. "
        "Return only the word."
    )
    msg = llm.invoke(prompt)
    word = str(msg.content).strip().split()[0]
    return {"word": word}


def generate_phrase(state: State) -> Dict[str, Any]:
    """Generates a phrase that includes the word and is about the topic."""
    topic = state["topic"]
    word = state["word"]
    prompt = (
        f"Generate a short phrase about the topic '{topic}' that includes the word '{word}'. "
        "Keep it to one sentence."
    )
    msg = llm.invoke(prompt)
    phrase = str(msg.content).strip()
    return {"phrase": phrase}


def check_topic(state: State) -> Dict[str, Any]:
    """Checks if the generated phrase is relevant to the topic."""
    topic = state["topic"]
    phrase = state["phrase"]
    prompt = (
        f"Topic: {topic}\n"
        f"Phrase: {phrase}\n\n"
        "Is this phrase clearly relevant to the topic? Answer only 'yes' or 'no'."
    )
    msg = llm.invoke(prompt)
    answer = str(msg.content).strip().lower()
    relevant = answer.startswith("y")
    return {"relevant": relevant}


# --- Build the graph ---

workflow = StateGraph(State)

workflow.add_node("Generate Letter", generate_letter)
workflow.add_node("Generate Word", generate_word)
workflow.add_node("Generate Phrase", generate_phrase)
workflow.add_node("Check Topic", check_topic)

# Linear chain: START -> Letter -> Word -> Phrase -> Check
workflow.add_edge(START, "Generate Letter")
workflow.add_edge("Generate Letter", "Generate Word")
workflow.add_edge("Generate Word", "Generate Phrase")
workflow.add_edge("Generate Phrase", "Check Topic")

# Conditional routing based on relevance
workflow.add_conditional_edges(
    "Check Topic",
    # This function returns a label used to pick the edge below
    lambda state: "done" if state.get("relevant") else "retry",
    {
        "done": END,
        "retry": "Generate Letter",  # loop back if not relevant
    },
)

app = workflow.compile()

if __name__ == "__main__":
    # You can pass an initial topic; if missing/empty, generate_letter sets a default.
    initial_state: State = {"topic": "Football"}
    final_state = app.invoke(initial_state)
    print("Final state:")
    print(final_state)

from typing_extensions import TypedDict
from typing import Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
import os
import getpass
import dotenv
import logging

# ============================================================
# LOGGING SETUP
# ============================================================

LOGGER_NAME = "prompt_chaining"
logger = logging.getLogger(LOGGER_NAME)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure a clean, professional logger."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("langgraph").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


def banner(text: str) -> None:
    """Prints a nicely formatted section header."""
    sep = "─" * 70
    logger.info("\n%s\n▶ %s\n%s", sep, text, sep)


def log_state(prefix: str, state: Dict[str, Any]) -> None:
    """Pretty-print the core state fields."""
    summary = {
        "topic": state.get("topic"),
        "letter": state.get("letter"),
        "word": state.get("word"),
        "phrase": state.get("phrase"),
        "relevant": state.get("relevant"),
    }
    logger.info("\n🔸 %s State:\n%s\n", prefix, summary)


# ============================================================
# ENV
# ============================================================

dotenv.load_dotenv()


def _set_env(var: str) -> None:
    if var not in os.environ or not os.environ[var]:
        os.environ[var] = getpass.getpass(f"Enter value for {var}: ")


_set_env("ANTHROPIC_API_KEY")

# ============================================================
# MODEL
# ============================================================

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
)

# ============================================================
# STATE
# ============================================================

class State(TypedDict, total=False):
    topic: str
    letter: str
    word: str
    phrase: str
    relevant: bool


# ============================================================
# NODES
# ============================================================

def generate_letter(state: State) -> Dict[str, Any]:
    banner("Generate Letter")
    topic = state.get("topic") or "Football"
    prompt = (
        f"Generate a single letter that could start a word about the topic "
        f"'{topic}'. Only return the letter."
    )
    msg = llm.invoke(prompt)
    raw = str(msg.content).strip()
    letter = raw[0] if raw else "A"
    logger.info("Letter generated: %r (raw=%r)", letter, raw)
    return {"topic": topic, "letter": letter}


def generate_word(state: State) -> Dict[str, Any]:
    banner("Generate Word")
    topic = state["topic"]
    letter = state["letter"]
    prompt = (
        f"Generate a single word about '{topic}' starting with '{letter}'. "
        f"Return only the word."
    )
    msg = llm.invoke(prompt)
    raw = str(msg.content).strip()
    word = (raw.split() or [""])[0]
    logger.info("Word generated: %r (raw=%r)", word, raw)
    return {"word": word}


def generate_phrase(state: State) -> Dict[str, Any]:
    banner("Generate Phrase")
    topic = state["topic"]
    word = state["word"]
    prompt = (
        f"Generate a short phrase about '{topic}' including the word '{word}'. "
        f"One sentence only."
    )
    msg = llm.invoke(prompt)
    phrase = str(msg.content).strip()
    logger.info("Phrase generated: %r", phrase)
    return {"phrase": phrase}


def check_topic(state: State) -> Dict[str, Any]:
    banner("Check Topic")
    topic = state["topic"]
    phrase = state["phrase"]

    prompt = (
        f"Topic: {topic}\nPhrase: {phrase}\n\n"
        f"Is this phrase relevant to the topic? Answer 'yes' or 'no'."
    )
    msg = llm.invoke(prompt)
    raw = str(msg.content).strip().lower()
    relevant = raw.startswith("y")
    logger.info("Relevance: %r (model said: %r)", relevant, raw)
    return {"relevant": relevant}


# ============================================================
# GRAPH BUILD
# ============================================================

workflow = StateGraph(State)

workflow.add_node("Generate Letter", generate_letter)
workflow.add_node("Generate Word", generate_word)
workflow.add_node("Generate Phrase", generate_phrase)
workflow.add_node("Check Topic", check_topic)

workflow.add_edge(START, "Generate Letter")
workflow.add_edge("Generate Letter", "Generate Word")
workflow.add_edge("Generate Word", "Generate Phrase")
workflow.add_edge("Generate Phrase", "Check Topic")

workflow.add_conditional_edges(
    "Check Topic",
    lambda s: "done" if s.get("relevant") else "retry",
    {
        "done": END,
        "retry": "Generate Letter",
    },
)

app = workflow.compile()

# ============================================================
# GRAPH DIAGRAM EXPORT
# ============================================================

def render_graph_diagram(output_path: str = "workflow_graph.png") -> None:
    graph = app.get_graph()

    banner("Rendering Workflow Diagram")

    # Try Mermaid PNG export
    try:
        graph.draw_mermaid_png(output_path)
        logger.info("Diagram saved as PNG → %s", output_path)
        return
    except Exception as e:
        logger.warning("PNG export failed: %s", e)

    # Try .visualize() API used in older versions
    try:
        import tempfile
        viz = workflow.visualize()
        with open(output_path, "wb") as f:
            f.write(viz.render_png())
        logger.info("Diagram saved using fallback visualize() → %s", output_path)
        return
    except Exception as e:
        logger.warning("visualize() fallback failed: %s", e)

    # Last fallback → save Mermaid source as a Markdown file
    try:
        md_path = "workflow_graph.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("```mermaid\n")
            f.write(graph.draw_mermaid())
            f.write("\n```")
        logger.info("Saved Mermaid diagram source → %s", md_path)
    except Exception as e:
        logger.error("Could NOT generate any diagram: %s", e)


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    configure_logging()

    banner("WORKFLOW START")

    # Produce diagram
    render_graph_diagram("workflow_graph.png")

    initial_state: State = {"topic": "Football"}
    log_state("Initial", initial_state)

    logger.info("Running workflow...")

    final_state: Optional[State] = None
    step_counter = 0

    for update in app.stream(initial_state, stream_mode="values"):
        step_counter += 1
        log_state(f"Step {step_counter}", update)
        final_state = update

    banner("WORKFLOW COMPLETE")
    print("\nFinal State:\n", final_state)

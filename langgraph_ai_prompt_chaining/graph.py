from typing import Any, Tuple

from langgraph.graph import StateGraph, START, END

from .state import State
from .nodes import (
    generate_letter,
    generate_word,
    generate_phrase,
    check_topic,
)


def build_workflow() -> StateGraph[State]:
    """Create and configure the LangGraph StateGraph."""
    workflow: StateGraph[State] = StateGraph(State)

    # Nodes
    workflow.add_node("Generate Letter", generate_letter)
    workflow.add_node("Generate Word", generate_word)
    workflow.add_node("Generate Phrase", generate_phrase)
    workflow.add_node("Check Topic", check_topic)

    # Edges
    workflow.add_edge(START, "Generate Letter")
    workflow.add_edge("Generate Letter", "Generate Word")
    workflow.add_edge("Generate Word", "Generate Phrase")
    workflow.add_edge("Generate Phrase", "Check Topic")

    # Conditional routing
    workflow.add_conditional_edges(
        "Check Topic",
        # decide which branch label to follow
        lambda s: "done" if s.get("relevant") else "retry",
        {
            # ✅ use the END sentinel, not the string "END"
            "done": END,
            "retry": "Generate Letter",
        },
    )

    return workflow


def get_app_and_workflow() -> Tuple[Any, StateGraph[State]]:
    """
    Build the workflow and return both the compiled app and the underlying
    StateGraph (for visualization).

    We intentionally keep the compiled app type as `Any` to avoid relying
    on internal LangGraph types that may differ between versions.
    """
    workflow = build_workflow()
    app = workflow.compile()
    return app, workflow

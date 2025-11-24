from typing import Optional

from .state import State
from .graph import get_app_and_workflow
from .diagram import render_graph_diagram
from .logging_config import configure_logging, banner, log_state
from .config import DEFAULT_TOPIC


def main() -> None:
    """Entry point for running the prompt-chaining workflow."""
    configure_logging()

    banner("WORKFLOW START")

    # Build app & workflow
    app, workflow = get_app_and_workflow()

    # Render diagram
    render_graph_diagram(app, workflow, "workflow_graph.png")

    # Initial state
    initial_state: State = {"topic": DEFAULT_TOPIC}
    log_state("Initial", initial_state)

    # Stream execution
    final_state: Optional[State] = None
    step_counter = 0

    for update in app.stream(initial_state, stream_mode="values"):
        step_counter += 1
        log_state(f"Step {step_counter}", update)
        final_state = update

    banner("WORKFLOW COMPLETE")
    print("\nFinal State:\n", final_state)

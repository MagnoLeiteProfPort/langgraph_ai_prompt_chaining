from typing import Any

from langgraph.graph import StateGraph

from .logging_config import banner, logger


def render_graph_diagram(
    app: Any,
    workflow: StateGraph,
    output_path: str = "workflow_graph.png",
) -> None:
    """
    Render the LangGraph diagram.

    Your LangGraph version exposes:
        - app.get_graph().draw_mermaid_png() -> bytes
        - app.get_graph().draw_mermaid() -> str (Mermaid source)

    So we:
    1) Call draw_mermaid_png() with NO arguments, save the bytes to output_path.
    2) If that fails for any reason, fall back to saving Mermaid source into a
       Markdown file (workflow_graph.md).
    """
    banner("Rendering Workflow Diagram")

    # Try PNG export via draw_mermaid_png() (no args)
    try:
        graph = app.get_graph()
        png_bytes = graph.draw_mermaid_png()  # no output_path arg in this version
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        logger.info("Diagram saved as PNG → %s", output_path)
        return
    except Exception as e:
        logger.warning("PNG export via draw_mermaid_png() failed: %s", e)

    # Fallback: save Mermaid source as Markdown
    try:
        md_path = "workflow_graph.md"
        graph = app.get_graph()
        mermaid_src = graph.draw_mermaid()
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("```mermaid\n")
            f.write(mermaid_src)
            f.write("\n```")
        logger.info("Saved Mermaid diagram source → %s", md_path)
    except Exception as e:
        logger.error("Could NOT generate any diagram: %s", e)

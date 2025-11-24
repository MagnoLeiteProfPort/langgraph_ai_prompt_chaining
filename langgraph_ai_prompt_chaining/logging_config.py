import logging
from typing import Dict, Any

from .config import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure a clean, professional console logger."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Keep external libs quieter by default
    logging.getLogger("langgraph").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


def banner(text: str) -> None:
    """Print a nicely formatted section header."""
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

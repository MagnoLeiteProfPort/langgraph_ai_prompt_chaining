from typing import Dict, Any

from .state import State
from .llm_client import llm
from .logging_config import banner, logger
from .config import DEFAULT_TOPIC


def generate_letter(state: State) -> Dict[str, Any]:
    """Generates a letter based on the topic."""
    banner("Generate Letter")
    topic = state.get("topic") or DEFAULT_TOPIC

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
    """Generates a word based on the letter and topic."""
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
    """Generates a phrase that includes the word and is about the topic."""
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
    """Checks if the generated phrase is relevant to the topic."""
    banner("Check Topic")
    topic = state["topic"]
    phrase = state["phrase"]

    prompt = (
        f"Topic: {topic}\n"
        f"Phrase: {phrase}\n\n"
        f"Is this phrase relevant to the topic? Answer 'yes' or 'no'."
    )
    msg = llm.invoke(prompt)
    raw = str(msg.content).strip().lower()
    relevant = raw.startswith("y")

    logger.info("Relevance: %r (model said: %r)", relevant, raw)
    return {"relevant": relevant}

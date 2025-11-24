from langchain_anthropic import ChatAnthropic

from .config import ANTHROPIC_MODEL_ID


# Single shared LLM instance for the workflow
llm = ChatAnthropic(
    model=ANTHROPIC_MODEL_ID,
    max_tokens=1000,
)

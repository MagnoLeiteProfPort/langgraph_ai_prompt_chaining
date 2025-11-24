import os
import getpass
import dotenv

# Load environment variables from .env if present
dotenv.load_dotenv()

# Logger name used across the package
LOGGER_NAME = "prompt_chaining"

# Default topic used by the workflow
DEFAULT_TOPIC = "Football"

# Model ID for Anthropic – make sure this exists for your key
ANTHROPIC_MODEL_ID = "claude-sonnet-4-20250514"

# Name of the env var for the Anthropic API key
ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"


def ensure_env(var_name: str) -> None:
    """
    Ensure that an environment variable is set.
    If missing, interactively ask the user for a value.
    """
    if var_name not in os.environ or not os.environ[var_name]:
        os.environ[var_name] = getpass.getpass(f"Enter value for {var_name}: ")


# Ensure the Anthropic key is present
ensure_env(ANTHROPIC_API_KEY_ENV)

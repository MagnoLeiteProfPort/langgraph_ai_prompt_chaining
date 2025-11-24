# list_models.py
import os
from anthropic import Anthropic
import dotenv
dotenv.load_dotenv()  # Load .env into os.environ

def _set_env(var: str):
    """Ensure an env var is set, ask interactively if missing."""
    if var not in os.environ or not os.environ[var]:
        os.environ[var] = getpass.getpass(f"Enter value for {var}: ")

_set_env("ANTHROPIC_API_KEY")

# If you rely on .env, you can also call dotenv.load_dotenv() here
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise SystemExit("ANTHROPIC_API_KEY not set in environment")

client = Anthropic(api_key=api_key)

page = client.models.list()

print("Available Anthropic models for this key:\n")
for m in page.data:
    print("-", m.id)

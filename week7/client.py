import json
import os
from pathlib import Path
from openai import OpenAI

PROMPT_PATH = Path("prompts/enrich-v1.md")


def get_openai_client() -> OpenAI:
    """Instantiates the OpenAI-compatible client using environment variables."""
    return OpenAI(
        base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=os.getenv("LLM_API_KEY", "ollama"),
    )


def load_system_prompt() -> str:
    """Reads the versioned markdown prompt file from disk."""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt file not found at: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8")


def call_llm(user_payload: dict) -> str:
    """
    Sends system instructions and JSON-encoded user payload to the LLM.
    Returns the raw string output from the model.
    """
    client = get_openai_client()
    system_prompt = load_system_prompt()
    model_name = os.getenv("LLM_MODEL", "openrouter/free")

    # Anti-prompt injection: Serialize untrusted scraped data into the user message role
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
        temperature=0.1,  # Low temperature for deterministic output
    )

    return response.choices[0].message.content or ""
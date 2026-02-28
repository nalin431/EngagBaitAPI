"""OpenAI embeddings using text-embedding-3-small."""

import os
from typing import TYPE_CHECKING

from tenacity import retry, stop_after_attempt, wait_exponential

if TYPE_CHECKING:
    from openai import OpenAI


def _get_client() -> "OpenAI | None":
    """Return OpenAI client if API key is set, else None."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key or not key.startswith("sk-"):
        return None
    from openai import OpenAI
    return OpenAI(api_key=key)


def _call_api(client: "OpenAI", text: str) -> list[float]:
    r = client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8191],  # model limit
    )
    return r.data[0].embedding


def get_embedding(text: str, client: "OpenAI | None" = None) -> list[float] | None:
    """
    Embed text using OpenAI text-embedding-3-small.
    Returns None if OpenAI is unavailable or on error. Retries on rate limit.
    """
    c = client if client is not None else _get_client()
    if c is None:
        return None
    decorated = retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )(_call_api)
    try:
        return decorated(c, text)
    except Exception:
        return None

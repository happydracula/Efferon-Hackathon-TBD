"""
db/embeddings.py
----------------
Generates text embeddings via the OpenAI-compatible embeddings endpoint
on OpenRouter (or the real OpenAI API — same interface).

We embed the *concatenated evidence text* for each evidence row so that
semantic similarity search works across the entire Sepsis Atlas.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))

_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}
_URL = "https://openrouter.ai/api/v1/embeddings"


def embed_text(text: str) -> list[float]:
    """
    Return a 1536-dim (default) embedding for *text*.

    Falls back to a zero vector on failure so a single bad paper cannot
    block the entire ingestion run.
    """
    if not text or not text.strip():
        return [0.0] * EMBEDDING_DIM

    payload = {"model": EMBEDDING_MODEL, "input": text}
    try:
        resp = requests.post(_URL, headers=_HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]
    except Exception as exc:
        print(f"[embeddings] Warning – embedding failed: {exc}. Using zero vector.")
        return [0.0] * EMBEDDING_DIM


def build_evidence_text(evidence: dict) -> str:
    """
    Concatenate the human-readable fields of an evidence record into a
    single string suitable for embedding.
    """
    parts = [
        f"Population: {evidence.get('population_type', '')}",
        f"Predictors: {', '.join(evidence.get('predictors') or [])}",
        f"Outcome: {evidence.get('outcome', '')}",
        f"Effect size: {evidence.get('effect_size', '')}",
        f"Performance: {evidence.get('performance', '')}",
        f"Method: {evidence.get('method', '')}",
        f"Notes: {evidence.get('notes', '')}",
    ]
    return "\n".join(p for p in parts if p.split(": ", 1)[-1].strip())

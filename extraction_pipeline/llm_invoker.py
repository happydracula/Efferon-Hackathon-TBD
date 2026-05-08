"""
llm_invoker.py
--------------
Thin wrapper around the OpenRouter API.

Changed from original:
- Uses `requests` directly instead of an `openrouter` SDK (avoids an extra
  undocumented dependency). The HTTP call is identical to what the SDK does.
- Adds retry logic (3 attempts, exponential back-off) so transient 429/5xx
  errors don't abort a long batch run.
- Returns a Python object (dict/list) already parsed from JSON, exactly like
  the original.
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")  # override via .env
API_URL = "https://openrouter.ai/api/v1/chat/completions"

_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}


def call_llm(prompt: str, retries: int = 3) -> dict | list:
    """
    Send *prompt* to the configured LLM and return the parsed JSON response.

    Raises
    ------
    ValueError  – if the model output cannot be parsed as JSON after all retries.
    RuntimeError – if the HTTP request keeps failing.
    """
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }

    last_error = None
    for attempt in range(retries):
        try:
            resp = requests.post(API_URL, headers=_HEADERS, json=payload, timeout=60)
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            # Strip optional markdown code fences
            raw = raw.strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            if raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            return json.loads(raw.strip())
        except (requests.HTTPError, requests.Timeout) as exc:
            last_error = exc
            wait = 2 ** attempt
            print(f"[llm_invoker] HTTP error on attempt {attempt + 1}: {exc}. "
                  f"Retrying in {wait}s…")
            time.sleep(wait)
        except json.JSONDecodeError as exc:
            last_error = exc
            print(f"[llm_invoker] JSON parse error on attempt {attempt + 1}: {exc}")
            break  # no point retrying a malformed response

    raise ValueError(f"call_llm failed after {retries} attempts. Last error: {last_error}")

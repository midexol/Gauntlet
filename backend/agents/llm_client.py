"""
Single point of contact with the LLM provider. Both agents (strategy
compiler, crash analyst) go through this — never call the SDK directly.
Uses Gemini (LLM_MODEL e.g. 'gemini-3.6-flash') — only this file would
need to change to swap providers again.
"""
from google import genai
from google.genai import types

from config import settings


class LLMClientError(RuntimeError):
    pass


_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if not settings.LLM_API_KEY:
        raise LLMClientError("LLM_API_KEY is not set")
    if _client is None:
        _client = genai.Client(api_key=settings.LLM_API_KEY)
    return _client


def call_llm(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
    """
    Single call, no streaming, no tool use — both agents just need a
    text-in/text-out response. Raises LLMClientError on any failure
    rather than letting a downstream module silently treat an error as data.
    """
    client = _get_client()
    model = settings.LLM_MODEL or "gemini-3.6-flash"
    try:
        response = client.models.generate_content(
            model=model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=max_tokens,
            ),
        )
        text = response.text
        if not text:
            raise LLMClientError("LLM returned no text content")
        return text
    except LLMClientError:
        raise
    except Exception as e:  # noqa: BLE001 — deliberately broad: any SDK failure must surface, not be swallowed
        raise LLMClientError(f"LLM call failed: {e}") from e

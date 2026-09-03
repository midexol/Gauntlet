"""
Single point of contact with the LLM provider. Both agents (strategy
compiler, crash analyst) go through this — never call the SDK directly.
Defaults to Claude (LLM_MODEL e.g. 'claude-sonnet-4-5') since it's the
most natural fit, but only this file would need to change to swap providers.
"""
from anthropic import Anthropic

from config import settings


class LLMClientError(RuntimeError):
    pass


_client: Anthropic | None = None


def _get_client() -> Anthropic:
    global _client
    if not settings.LLM_API_KEY:
        raise LLMClientError("LLM_API_KEY is not set")
    if _client is None:
        _client = Anthropic(api_key=settings.LLM_API_KEY)
    return _client


def call_llm(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
    """
    Single call, no streaming, no tool use — both agents just need a
    text-in/text-in JSON response. Raises LLMClientError on any failure
    rather than letting a downstream module silently treat an error as data.
    """
    client = _get_client()
    model = settings.LLM_MODEL or "claude-sonnet-4-5"
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        text_blocks = [b.text for b in response.content if b.type == "text"]
        if not text_blocks:
            raise LLMClientError("LLM returned no text content")
        return "".join(text_blocks)
    except Exception as e:  # noqa: BLE001 — deliberately broad: any SDK failure must surface, not be swallowed
        raise LLMClientError(f"LLM call failed: {e}") from e

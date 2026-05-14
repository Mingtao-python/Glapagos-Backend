"""
Glapagos AI Provider Registry
api/api/ai/providers.py

Routes AI requests to the correct backend based on AI_PROVIDER env var.

Usage:
    AI_PROVIDER=openai  -> uses OpenAI GPT (default, existing behavior)
    AI_PROVIDER=ollama  -> uses local Ollama inference, no API key needed

The ChatAssistant in services.py calls get_provider() instead of
instantiating OpenAI directly.
"""

from __future__ import annotations

import os
import logging
from typing import Protocol

logger = logging.getLogger(__name__)

AI_PROVIDER = os.environ.get("AI_PROVIDER", "openai").lower()


class AIProvider(Protocol):
    """
    Interface that every AI provider must implement.
    ChatAssistant calls complete() — providers handle the rest.
    """

    def complete(self, prompt: str, **kwargs) -> str: ...


class OpenAIProvider:
    """
    Wraps the existing OpenAI integration.
    Preserves current ChatAssistant behavior exactly.
    """

    def __init__(self):
        import openai
        from django.conf import settings

        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def complete(self, prompt: str, system: str = "", **kwargs) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        completion = self.client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o-mini"),
            messages=messages,
        )
        return completion.choices[0].message.content or ""


class OllamaProvider:
    """
    Routes requests to local Ollama inference.
    No API key required — data never leaves the machine.
    """

    def __init__(self):
        from api.ai.clients.ollama_client import OllamaClient

        self.client = OllamaClient()

    def complete(self, prompt: str, system: str = "", **kwargs) -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        return self.client.complete(full_prompt, **kwargs)


def get_provider() -> AIProvider:
    """
    Factory — returns the correct provider based on AI_PROVIDER env var.
    Called by ChatAssistant on every request.
    """
    provider = AI_PROVIDER
    logger.debug("AI provider: %s", provider)

    if provider == "ollama":
        return OllamaProvider()
    elif provider == "openai":
        return OpenAIProvider()
    else:
        logger.warning("Unknown AI_PROVIDER=%r, falling back to OpenAI", provider)
        return OpenAIProvider()

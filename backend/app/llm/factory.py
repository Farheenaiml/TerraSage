from __future__ import annotations

from app.llm.base import LLMProvider
from app.llm.config import LLMConfig, llm_config
from app.llm.providers.mock_provider import MockLLMProvider
from app.llm.providers.openai_compatible import OpenAICompatibleProvider


def get_llm_provider(config: LLMConfig | None = None) -> LLMProvider | None:
    """Returns the configured LLMProvider instance, or None if unconfigured.

    Application startup never fails if unconfigured.
    """
    cfg = config or llm_config
    if not cfg.is_configured:
        return None

    provider = cfg.provider
    if provider == "mock":
        return MockLLMProvider(model_name=cfg.model or "mock-grounded-v1")

    if provider in {"openai", "groq", "together", "ollama", "openai_compatible"}:
        base_url = cfg.base_url
        if provider == "groq" and not base_url:
            base_url = "https://api.groq.com/openai/v1"
        return OpenAICompatibleProvider(
            api_key=cfg.api_key or "",
            model_name=cfg.model or "default-model",
            base_url=base_url,
            provider_name=provider,
        )

    return OpenAICompatibleProvider(
        api_key=cfg.api_key or "",
        model_name=cfg.model or "custom-model",
        base_url=cfg.base_url,
        provider_name=provider,
    )

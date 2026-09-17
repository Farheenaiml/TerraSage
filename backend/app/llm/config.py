from __future__ import annotations

import os


class LLMConfig:
    """Reads LLM configuration safely without enforcing required keys."""

    def __init__(
        self,
        provider: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ):
        self._provider = provider
        self._api_key = api_key
        self._model = model
        self._base_url = base_url

    @property
    def provider(self) -> str:
        if self._provider is not None:
            return self._provider.strip().lower()
        return os.getenv("LLM_PROVIDER", "").strip().lower()

    @property
    def model(self) -> str:
        if self._model is not None:
            return self._model.strip()
        return os.getenv("LLM_MODEL", "").strip()

    @property
    def api_key(self) -> str | None:
        if self._api_key is not None:
            return self._api_key if self._api_key.strip() else None
        key = os.getenv("LLM_API_KEY", "").strip()
        return key if key else None

    @property
    def base_url(self) -> str | None:
        if self._base_url is not None:
            return self._base_url if self._base_url.strip() else None
        url = os.getenv("LLM_BASE_URL", "").strip()
        return url if url else None

    @property
    def is_configured(self) -> bool:
        """Returns True only if an explicit provider and non-empty key (or mock) is set."""
        if self.provider == "mock":
            return True
        return bool(self.provider and self.api_key)


llm_config = LLMConfig()

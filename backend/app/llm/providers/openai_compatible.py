from __future__ import annotations

import re
from typing import Any
import httpx

from app.llm.base import LLMProvider, LLMResult


class OpenAICompatibleProvider(LLMProvider):
    """Universal provider for OpenAI, Groq, Together, Ollama, or any standard /v1/chat/completions API."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4o-mini",
        base_url: str | None = None,
        provider_name: str = "openai",
    ):
        self._api_key = api_key
        self._model = model_name or "gpt-4o-mini"
        self._base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self._provider_name = provider_name

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self._model

    def generate_response(
        self,
        prompt: str,
        system_instruction: str,
        context: dict[str, Any],
    ) -> LLMResult:
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Supplied TerraSage Context:\n{context}\n\nUser Inquiry: {prompt}"},
        ]

        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": 0.2,  # Low temperature for strict factual grounding
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]

                # Extract any chunk citations if mentioned (e.g. [chunk-uuid])
                found_ids = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', content, re.IGNORECASE)

                return LLMResult(
                    content=content,
                    model_name=self._model,
                    provider_name=self._provider_name,
                    referenced_evidence_ids=found_ids,
                    raw_response=data,
                )
        except Exception as err:
            raise RuntimeError(f"LLM provider '{self._provider_name}' request failed: {err}")

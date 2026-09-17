from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMMessage:
    role: str
    content: str


@dataclass
class LLMResult:
    content: str
    model_name: str
    provider_name: str
    referenced_evidence_ids: list[str] = field(default_factory=list)
    raw_response: dict[str, Any] = field(default_factory=dict)

    @property
    def provider(self) -> str:
        return self.provider_name

    @property
    def model(self) -> str:
        return self.model_name


class LLMProvider(ABC):
    """Abstract interface for conversational LLM generation."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'openai', 'mock', 'groq')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the configured model."""
        pass

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        system_instruction: str,
        context: dict[str, Any],
    ) -> LLMResult:
        """Generates a conversational explanation grounded strictly in context."""
        pass

    def generate(self, messages: list[LLMMessage]) -> LLMResult:
        """Compatibility method for standard message sequences."""
        system_msgs = [m.content for m in messages if m.role == "system"]
        user_msgs = [m.content for m in messages if m.role == "user"]
        sys_inst = system_msgs[0] if system_msgs else ""
        prompt = user_msgs[-1] if user_msgs else ""
        return self.generate_response(prompt=prompt, system_instruction=sys_inst, context={})

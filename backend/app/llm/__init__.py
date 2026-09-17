"""TerraSage LLM Abstraction Layer (Chunk 6).

Provides an unforced, unkeyed abstraction over external LLMs.
The system starts cleanly without any API keys configured.
"""
from app.llm.base import LLMProvider, LLMResult
from app.llm.config import llm_config
from app.llm.factory import get_llm_provider

__all__ = ["LLMProvider", "LLMResult", "llm_config", "get_llm_provider"]

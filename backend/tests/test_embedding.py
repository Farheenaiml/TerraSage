import pytest
from app.core.config import settings
from app.knowledge.embedding import EmbeddingConfigurationError, EmbeddingProvider


def test_local_embedding_provider_configuration():
    provider = EmbeddingProvider()
    assert provider.provider == "local"
    assert provider.model == "sentence-transformers/all-MiniLM-L6-v2"
    assert provider.api_key is None


def test_local_embedding_generation():
    provider = EmbeddingProvider()
    sentence = "Soil organic carbon can influence soil structure, water retention and ecosystem functioning."
    vectors = provider.embed([sentence])

    assert len(vectors) == 1
    assert len(vectors[0]) == 384
    assert all(isinstance(val, float) for val in vectors[0])


def test_api_provider_without_key_raises_error(monkeypatch):
    monkeypatch.setattr(settings, "embedding_provider", "openai")
    monkeypatch.setattr(settings, "embedding_api_key", None)

    provider = EmbeddingProvider()
    with pytest.raises(EmbeddingConfigurationError, match="EMBEDDING_API_KEY is not configured"):
        provider.embed(["Some environmental text"])

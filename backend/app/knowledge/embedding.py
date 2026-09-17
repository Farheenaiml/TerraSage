from typing import Any

import httpx

from app.core.config import settings


class EmbeddingConfigurationError(RuntimeError):
    pass


class EmbeddingProvider:
    def __init__(self) -> None:
        self.provider = settings.embedding_provider
        self.url = settings.embedding_api_url
        self.model = settings.embedding_model
        self.api_key = settings.embedding_api_key
        self._local_model = None

    def _get_local_model(self):
        if self._local_model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as error:
                raise EmbeddingConfigurationError(
                    "sentence-transformers is not installed for the local embedding provider."
                ) from error
            self._local_model = SentenceTransformer(self.model)
        return self._local_model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self.provider == "local":
            vectors = self._get_local_model().encode(texts, normalize_embeddings=False).tolist()
            if any(len(vector) != settings.embedding_dimension for vector in vectors):
                raise EmbeddingConfigurationError("Local embedding dimension does not match EMBEDDING_DIMENSION.")
            return vectors
        if not self.api_key:
            raise EmbeddingConfigurationError(
                "EMBEDDING_API_KEY is not configured; refusing to generate fabricated embeddings."
            )
        response = httpx.post(
            self.url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": texts},
            timeout=60,
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        vectors = [item["embedding"] for item in sorted(payload["data"], key=lambda item: item["index"])]
        if any(len(vector) != settings.embedding_dimension for vector in vectors):
            raise EmbeddingConfigurationError("Embedding dimension does not match EMBEDDING_DIMENSION.")
        return vectors

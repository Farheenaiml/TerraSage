from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.environment import ProviderCache


class CacheRepository:
    def __init__(self, db: Session | None):
        self.db = db

    def get(self, provider: str, latitude: float, longitude: float, params: str, period: str, dataset_version: str) -> dict[str, Any] | None:
        if self.db is None:
            return None
        key = f"{provider}:{latitude:.6f}:{longitude:.6f}:{params}:{period}:{dataset_version}"
        cached = self.db.query(ProviderCache).filter(ProviderCache.cache_key == key).first()
        if cached is None:
            return None
        now = datetime.now(timezone.utc)
        if cached.expires_at is not None:
            exp = cached.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < now:
                return None
        return cached.response_json

    def set(self, provider: str, latitude: float, longitude: float, params: str, period: str, dataset_version: str, response: dict[str, Any], ttl_hours: int = 24) -> dict[str, Any]:
        if self.db is None:
            return response
        key = f"{provider}:{latitude:.6f}:{longitude:.6f}:{params}:{period}:{dataset_version}"
        cached = self.db.query(ProviderCache).filter(ProviderCache.cache_key == key).first()
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=ttl_hours)
        if cached is None:
            cached = ProviderCache(
                cache_key=key,
                provider=provider,
                latitude=latitude,
                longitude=longitude,
                parameters=params,
                time_period=period,
                dataset_version=dataset_version,
                response_json=response,
                expires_at=expires_at,
            )
            self.db.add(cached)
        else:
            cached.response_json = response
            cached.expires_at = expires_at
        self.db.commit()
        return response

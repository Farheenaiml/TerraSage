from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    provider_name: str = "base"

    @abstractmethod
    def get_data(self, latitude: float, longitude: float, **options: Any) -> dict[str, Any]:
        raise NotImplementedError

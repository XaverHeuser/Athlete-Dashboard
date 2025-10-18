"""This module defines the base interface for all data extractors."""

from abc import ABC, abstractmethod
from typing import Any


class BaseExtractor(ABC):
    """An abstract base class for Extractor."""

    @abstractmethod
    def fetch_all_activities(self) -> list[dict[str, Any]]:
        """Fetches new activities and returns them in a standard format."""
        pass

"""This module defines the base interface for all data extractors."""

from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar


T = TypeVar("T")

class BaseExtractor(ABC, Generic[T]):
    """An abstract base class for Extractor."""

    @abstractmethod
    def fetch_all_activities(self) -> Sequence[T]:
        """Fetches new activities and returns them in a standard format."""
        pass

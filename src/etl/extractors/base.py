"""This file implements ."""

from abc import ABC, abstractmethod
from typing import Any


class BaseExtractor(ABC):
    @abstractmethod
    def fetch_all_activities(self) -> list[dict[str, Any]]:
        """Fetches new activities and returns them in a standard format."""
        pass

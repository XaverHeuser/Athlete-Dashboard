"""This file implements ."""

from abc import ABC, abstractmethod
from typing import Any


class BaseLoader(ABC):
    @abstractmethod
    def load_data(self, data: list[dict[str, Any]]) -> None:
        """Takes transformed data and loads it into the data store."""
        pass

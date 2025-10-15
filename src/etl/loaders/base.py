"""This file implements ."""

from abc import ABC, abstractmethod


class BaseLoader(ABC):
    @abstractmethod
    def load_data(self) -> None:
        """Takes transformed data and loads it into the data store."""
        pass

"""This file implements ."""

from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    @abstractmethod
    def fetch_all_activities(self) -> None:
        """Fetches new activities and returns them in a standard format."""
        pass

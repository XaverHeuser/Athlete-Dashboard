"""This file implements ."""

from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    @abstractmethod
    def fetch_activities(self):
        """Fetches new activities and returns them in a standard format."""
        pass

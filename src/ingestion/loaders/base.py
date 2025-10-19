"""This module defines the base interface for all data loaders."""

from abc import ABC, abstractmethod

import pandas as pd


class BaseLoader(ABC):
    @abstractmethod
    def load_data(self, data: pd.DataFrame) -> None:
        """Takes data and loads it into the data store."""
        pass

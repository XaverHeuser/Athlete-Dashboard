"""This file implements ."""

from abc import ABC, abstractmethod

import pandas as pd


class BaseLoader(ABC):
    @abstractmethod
    def load_data(self, data: pd.DataFrame) -> None:
        """Takes transformed data and loads it into the data store."""
        pass

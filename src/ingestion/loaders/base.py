"""This module defines the base interface for all data loaders."""

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BaseLoader(ABC):
    @abstractmethod
    def load_data(
        self,
        data: pd.DataFrame,
        dataset: str,
        table_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Takes data and loads it into the data store."""
        pass

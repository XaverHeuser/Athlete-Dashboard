"""This module contains the loader for interacting with Google's BigQuery."""

from collections.abc import Mapping, Sequence
import os
from typing import Any, Optional, Union

from google.cloud import bigquery
import pandas as pd

from .base import BaseLoader


JsonRows = Sequence[Mapping[str, Any]]
Loadable = Union[pd.DataFrame, JsonRows]


class BigQueryLoader(BaseLoader):
    """Load data into a Google BigQuery table."""

    def __init__(self) -> None:
        """Initializes the BigQueryLoader."""
        self.project_id = os.environ.get('GCP_PROJECT_ID')
        self.client = bigquery.Client(project=self.project_id)

    def load_data(
        self,
        data: Loadable,
        dataset: str,
        table_name: str,
        write_disposition: str = 'WRITE_APPEND',
        schema: Optional[list[bigquery.SchemaField]] = None,
    ) -> None:
        """Loads data into the specified BigQuery table."""
        table_id = f'{self.project_id}.{dataset}.{table_name}'

        if isinstance(data, pd.DataFrame):
            if data.empty:
                print(f'No data provided for table {table_name}. Skipping.')
                return
            record_count = len(data)
        else:
            if not data:
                print(f'No data provided for table {table_name}. Skipping.')
                return
            record_count = len(data)

        print(f'Loading {record_count} records into {table_id}...')

        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition, create_disposition='CREATE_IF_NEEDED'
        )
        # If a schema is provided, use it; otherwise, enable autodetect
        if schema is not None:
            job_config.schema = schema
            job_config.autodetect = False
        else:
            job_config.autodetect = isinstance(data, pd.DataFrame)

        try:
            if isinstance(data, pd.DataFrame):
                job = self.client.load_table_from_dataframe(
                    data, table_id, job_config=job_config
                )
            else:
                job = self.client.load_table_from_json(
                    data, table_id, job_config=job_config
                )

            job.result()
        except Exception as e:
            print(f'Failed to load data into {table_id}: {e}')
            raise

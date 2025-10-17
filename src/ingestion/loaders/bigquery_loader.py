"""This module ."""

from google.cloud import bigquery
import pandas as pd

from .base import BaseLoader


class BigQueryLoader(BaseLoader):
    """Load data into a Google BigQuery table."""

    def __init__(self, gcp_project_id: str, dataset: str, table: str) -> None:
        """Initializes the BigQueryLoader."""
        # TODO: Improve code
        self.client = bigquery.Client(project=gcp_project_id)

        self.table_id = f'{gcp_project_id}.{dataset}.{table}'

        self.job_config = bigquery.LoadJobConfig(
            write_disposition='WRITE_TRUNCATE',
            create_disposition='CREATE_IF_NEEDED',
            autodetect=True,
        )

    def load_data(self, data: pd.DataFrame) -> None:
        # TODO: Implement and improve code
        if data.empty:
            print('No data provided to load. Skipping.')
            return

        print(f'Loading {len(data)} records into BigQuery table: {self.table_id}...')

        # Start the load job
        job = self.client.load_table_from_dataframe(
            data, self.table_id, job_config=self.job_config
        )

        job.result()  # Wait for the job to complete
        print(f'Successfully loaded data into {self.table_id}.')

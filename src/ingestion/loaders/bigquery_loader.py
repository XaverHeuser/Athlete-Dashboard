"""This module ."""

from google.cloud import bigquery
import pandas as pd

from .base import BaseLoader


class BigQueryLoader(BaseLoader):
    """Load data into a Google BigQuery table."""

    def __init__(self, project_id: str, dataset: str, table: str) -> None:
        """Initializes the BigQueryLoader."""
        # TODO: Add handling for local vs. Cloud
        # TODO: Improve code
        CREDENTIALS_PATH = '../credentials/sa-athlete-dashboard.json'

        self.client = bigquery.Client.from_service_account_json(
            CREDENTIALS_PATH, project='athlete-dashboard-467718'
        )
        self.table_id = f'{project_id}.{dataset}.{table}'

        self.job_config = bigquery.LoadJobConfig(
            write_disposition='WRITE_TRUNCATE',
            create_disposition='CREATE_IF_NEEDED',
            autodetect=True,
        )

    def load_data(self, data: pd.DataFrame) -> None:
        # TODO: Implement and improve code
        if not data:
            print('No data provided to load. Skipping.')
            return

        print(f'Loading {len(data)} records into BigQuery table: {self.table_id}...')

        # Start the load job
        job = self.client.load_table_from_dataframe(
            data, self.table_id, job_config=self.job_config
        )

        job.result()
        print(f'Successfully loaded data into {self.table_id}.')

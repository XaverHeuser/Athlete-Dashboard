"""This module ."""

import os

from google.cloud import bigquery
import pandas as pd

from .base import BaseLoader


class BigQueryLoader(BaseLoader):
    """Load data into a Google BigQuery table."""

    def __init__(self) -> None:
        """Initializes the BigQueryLoader."""
        # TODO: Improve code
        GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
        DATASET = os.environ.get('BIGQUERY_DATASET')
        TABLE_RAW = os.environ.get('BIGQUERY_TABLE_ACTIVITIES_RAW')

        self.client = bigquery.Client(
            project=GCP_PROJECT_ID,
        )

        self.table_id = f'{GCP_PROJECT_ID}.{DATASET}.{TABLE_RAW}'

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

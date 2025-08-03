import os
import re

from dotenv import load_dotenv
from google.cloud import bigquery
import pandas as pd

from src.strava.strava_utils import fetch_all_activities, get_access_token
from src.utils.utils import set_proxy


def first_test():
    print('This is the first test function.')
    set_proxy()

    load_dotenv()

    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
    GRANT_TYPE = os.getenv('GRANT_TYPE')

    PROJECT_ID = 'athlete-dashboard-467718'
    DATASET_ID = 'strava_data_overview'
    TABLE_ID = 'activities_strava'

    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, GRANT_TYPE)

    activities = fetch_all_activities(access_token)
    df_activities = pd.json_normalize(activities)
    print('The length of all activies is: ', len(df_activities))

    df_activities.columns = [
        re.sub(r'[^a-zA-Z0-9_]', '_', col) for col in df_activities.columns
    ]

    client = bigquery.Client.from_service_account_json(
        'C:/Users/A200162055/Downloads/athlete-dashboard-467718-d5f31b294e6f.json',
        project='athlete-dashboard-467718',
    )

    job_config = bigquery.LoadJobConfig(write_disposition='WRITE_TRUNCATE')
    full_table_id = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'
    client.load_table_from_dataframe(
        df_activities, full_table_id, job_config=job_config
    ).result()
    print(f'Data loaded to {full_table_id} successfully.')


if __name__ == '__main__':
    first_test()
    print('First test completed successfully.')

import datetime
import os
import json
import pandas as pd
import re
from google.cloud import bigquery
from src.strava_utils import get_access_token, fetch_all_activities
from src.utils import set_proxy_if_needed
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s - %(message)s')

# .env nur lokal laden
if os.path.exists(".env"):
    load_dotenv()
    print("[DEBUG] .env geladen für lokalen Test")

def run_script(request):
    now = datetime.datetime.now()
    logging.info(f'Script gestartet um {now}')
    logging.info('Toll')

    # Proxy setzen (nur lokal)
    set_proxy_if_needed()

    # 1️⃣ Secrets laden
    secret_json = os.getenv("STRAVA_OAUTH_CREDENTIALS")
    if not secret_json:
        raise RuntimeError("Secret STRAVA_OAUTH_CREDENTIALS nicht gefunden!")
    creds = json.loads(secret_json)
    logging.debug(f'Secret geladen, Client ID beginnt mit: {creds["client_id"][:5]}')

    client_id = creds["client_id"]
    client_secret = creds["client_secret"]
    refresh_token = creds["refresh_token"]
    print("Secret geladen, Client ID beginnt mit:", client_id[:5])

    # 2️⃣ Strava Access Token holen
    access_token = get_access_token(
        client_id, client_secret, refresh_token, 'refresh_token'
    )
    print('Access Token geladen')
    logging.info("Access Token geladen")

    # 3️⃣ Aktivitäten laden
    activities = fetch_all_activities(access_token)
    print(f"Activities geladen: {len(activities)}")
    df_activities = pd.json_normalize(activities)
    df_activities.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', col) for col in df_activities.columns]

    # 4️⃣ BigQuery Credentials laden
    sa_json_str = os.getenv("SERVICE_ACC_JSON")
    if not sa_json_str:
        raise RuntimeError("Secret SERVICE_ACC_JSON nicht gefunden!")
    sa_info = json.loads(sa_json_str)

    client = bigquery.Client.from_service_account_info(sa_info)
    print('BigQuery Client erfolgreich erstellt')
    logging.info("BigQuery Client erfolgreich erstellt")

    # 5️⃣ DataFrame in BigQuery laden
    full_table_id = 'athlete-dashboard-467718.strava_data_overview.activities_strava'
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    client.load_table_from_dataframe(df_activities, full_table_id, job_config=job_config).result()
    print(f'[DEBUG] Data loaded to {full_table_id} successfully.')
    logging.info(f"Data loaded to {full_table_id} successfully.")

    return "Data loaded successfully", 200

# Optional: Direkter Test lokal
if __name__ == "__main__":
    run_script()

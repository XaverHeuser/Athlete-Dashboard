import json

import requests


def get_access_token(
    client_id: str, client_secret: str, refresh_token: str, grant_type: str
) -> str:
    """Fetches a new access token using the refresh token."""
    # Read auth url from config
    with open('../config/config.json') as f:
        config = json.load(f)

    auth_url = config.get('auth_url')

    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': grant_type,
        'f': 'json',
    }

    res = requests.post(auth_url, data=payload, verify=False)
    return res.json()['access_token']


def fetch_all_activities(access_token: str) -> list:
    """Fetches all activities for the authenticated user."""
    # Read api url from config
    with open('../config/config.json') as f:
        config = json.load(f)

    activities_url = config.get('activities_url')

    header = {'Authorization': f'Bearer {access_token}'}

    request_page_num = 1
    all_activities = []

    while True:
        param = {'per_page': 200, 'page': request_page_num}
        my_dataset = requests.get(activities_url, headers=header, params=param).json()

        if len(my_dataset) == 0:
            break

        if all_activities:
            all_activities.extend(my_dataset)

        else:
            all_activities = my_dataset

        request_page_num += 1

    return all_activities

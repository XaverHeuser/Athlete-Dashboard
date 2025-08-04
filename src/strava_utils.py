import requests


def get_access_token(client_id: str, client_secret: str, refresh_token: str, grant_type: str) -> str:
    """Fetches a new access token using the refresh token."""
    auth_url = 'https://www.strava.com/oauth/token'

    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': grant_type,
        'f': 'json'
    }

    res = requests.post(auth_url, data=payload, verify=False)
    return res.json()['access_token']


def fetch_all_activities(access_token: str) -> list:
    """Fetches all activities for the authenticated user."""
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'

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

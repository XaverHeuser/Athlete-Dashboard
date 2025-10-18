"""This module."""

import os

import requests

AUTH_URL = 'https://www.strava.com/oauth/token'


def _load_strava_credentials() -> tuple[str, str, str]:
    """Helper to securely load credentials from environment."""

    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
    refresh_token = os.environ['REFRESH_TOKEN']

    print(client_id, client_secret, refresh_token)

    if not all([client_id, client_secret, refresh_token]):
        raise OSError('Missing Strava authentication environment variables.')

    return client_id, client_secret, refresh_token


def _get_fresh_access_token(
    client_id: str, client_secret: str, refresh_token: str
) -> str:
    """Fetches a new access token using the refresh token."""
    print('Refreshing Strava access token...')
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'f': 'json',
    }
    try:
        response = requests.post(AUTH_URL, data=payload, timeout=10)
        response.raise_for_status()
        new_token: str = response.json()['access_token']
        print('Successfully refreshed access token.')
        return new_token
    except requests.exceptions.HTTPError as e:
        print(f'Error refreshing token: {e.response.text}')
        raise


# This is the primary function other modules will call
def get_access_token() -> str:
    """Loads credentials and returns a fresh access token."""
    client_id, client_secret, refresh_token = _load_strava_credentials()
    return _get_fresh_access_token(client_id, client_secret, refresh_token)

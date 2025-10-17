"""This module."""

import os

from dotenv import load_dotenv
import requests

AUTH_URL = 'https://www.strava.com/oauth/token'  # For token refresh logic later


def load_strava_auth(mode: str) -> tuple[str, str, str]:
    """Load Strava auth details from environment variables."""

    if mode == 'local':
        load_dotenv()
    elif mode != 'cloud':
        raise ValueError(f'Invalid mode given: {mode}')

    required_vars = ['CLIENT_ID', 'CLIENT_SECRET', 'REFRESH_TOKEN']
    values = [os.environ.get(var) for var in required_vars]

    if not all(values):
        missing = [v for v, val in zip(required_vars, values) if not val]
        raise OSError(f'Missing environment variables: {", ".join(missing)}')

    return tuple(values)


def get_fresh_access_token(
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

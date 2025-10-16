"""This module ."""

from typing import Any

import requests

from .base import BaseExtractor

AUTH_URL = 'https://www.strava.com/oauth/token'  # For token refresh logic later


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


class StravaEndpoints:
    """A helper class as a central Strava API URL management."""

    BASE_URL = 'https://www.strava.com/api/v3'
    AUTH_URL = 'https://www.strava.com/oauth/token'

    @staticmethod
    def get_activities() -> str:
        """URL zum Abrufen von Aktivitäten."""
        return f'{StravaEndpoints.BASE_URL}/athlete/activities'

    @staticmethod
    def get_athlete_stats(athlete_id: int) -> str:
        """URL zum Abrufen der Statistiken eines Athleten."""
        return f'{StravaEndpoints.BASE_URL}/athletes/{athlete_id}/stats'

    @staticmethod
    def get_activity_stream(activity_id: int) -> str:
        """URL zum Abrufen der Datenströme einer Aktivität."""
        return f'{StravaEndpoints.BASE_URL}/activities/{activity_id}/streams'


class StravaExtractor(BaseExtractor):
    """Extracts data from Strava API"""

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    def fetch_all_activities(self) -> list[dict[str, Any]]:
        """Fetches all activities."""
        print('Start fetching all activities.')

        activities_url = StravaEndpoints.get_activities()
        headers = {'Authorization': f'Bearer {self.access_token}'}

        all_activities: list[dict[str, Any]] = []
        page = 1

        while True:
            params = {'per_page': 200, 'page': page}

            response = requests.get(
                activities_url, headers=headers, params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json()

            if not data:
                break

            all_activities.extend(data)
            page += 1

        print(f'All activities fetched. Found {len(all_activities)} activities.')
        return all_activities

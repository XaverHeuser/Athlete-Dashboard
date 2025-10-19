"""This module contains the extractor for interacting with the Strava API."""

from typing import Any

import requests

from src.ingestion.extractors.base import BaseExtractor


class StravaEndpoints:
    """A helper class as a central Strava API URL management."""

    BASE_URL = 'https://www.strava.com/api/v3'

    @staticmethod
    def get_activities() -> str:
        """URL to fetch activities."""
        return f'{StravaEndpoints.BASE_URL}/athlete/activities'


class StravaExtractor(BaseExtractor):  # type: ignore
    """Extracts data from Strava API"""

    def __init__(self, access_token: str) -> None:
        self.headers = {'Authorization': f'Bearer {access_token}'}

    def fetch_all_activities(self) -> list[dict[str, Any]]:
        """Fetches all activities."""
        print('Start fetching all activities.')

        activities_url = StravaEndpoints.get_activities()
        all_activities: list[dict[str, Any]] = []
        page = 1

        while True:
            params = {'per_page': 200, 'page': page}

            response = requests.get(
                activities_url, headers=self.headers, params=params, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            all_activities.extend(data)
            page += 1

        print(f'All activities fetched. Found {len(all_activities)} activities.')
        return all_activities

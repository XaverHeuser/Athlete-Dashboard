"""This module contains the extractor for interacting with the Strava API."""

from pydantic import ValidationError
import requests

from src.models.strava_activity_model import StravaActivity
from src.ingestion.extractors.base import BaseExtractor


class StravaEndpoints:
    """A helper class as a central Strava API URL management."""

    BASE_URL = 'https://www.strava.com/api/v3'

    @staticmethod
    def get_activities() -> str:
        """URL to fetch activities."""
        return f'{StravaEndpoints.BASE_URL}/athlete/activities'


class StravaExtractor(BaseExtractor):
    """Extracts and validates data from Strava API"""

    def __init__(self, access_token: str) -> None:
        self.headers = {'Authorization': f'Bearer {access_token}'}

    def fetch_all_activities(self) -> list[StravaActivity]:
        """Fetches all activities."""
        print('Start fetching all activities.')

        activities_url = StravaEndpoints.get_activities()
        all_activities: list[StravaActivity] = []
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

            invalid_count = 0
            for item in data:
                try:
                    all_activities.append(StravaActivity(**item))
                except ValidationError as e:
                    invalid_count += 1
                    print(f'Validation error: {e.errors()}')

            page += 1

        print(f'All activities fetched: {len(all_activities)} valid, {invalid_count} invalid.')
        return all_activities

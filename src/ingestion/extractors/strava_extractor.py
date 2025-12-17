"""This module contains the extractor for interacting with the Strava API."""

from datetime import datetime, timezone
from typing import Any, cast

from pydantic import ValidationError
import requests

from ingestion.extractors.base import BaseExtractor
from models.strava_activity_model import StravaActivity
from models.strava_athlete_info_model import StravaAthleteInfo
from models.strava_athlete_stats_model import StravaAthleteStats
from models.strava_gear_model import StravaGear


class StravaEndpoints:
    """A helper class as a central Strava API URL management."""

    BASE_URL = 'https://www.strava.com/api/v3'

    @staticmethod
    def get_athlete() -> str:
        """URL to fetch athlete information."""
        return f'{StravaEndpoints.BASE_URL}/athlete'

    @staticmethod
    def get_athlete_stats(athlete_id: str) -> str:
        """URL to fetch athlete stats."""
        return f'{StravaEndpoints.BASE_URL}/athletes/{athlete_id}/stats'

    @staticmethod
    def get_activities() -> str:
        """URL to fetch activities."""
        return f'{StravaEndpoints.BASE_URL}/athlete/activities'

    @staticmethod
    def get_gear_details(gear_id: str) -> str:
        """URL to fetch gear details."""
        return f'{StravaEndpoints.BASE_URL}/gear/{gear_id}'


class StravaExtractor(BaseExtractor):
    """Extracts and validates data from Strava API"""

    def __init__(self, access_token: str) -> None:
        self.headers = {'Authorization': f'Bearer {access_token}'}

    def fetch_athlete_info(self) -> StravaAthleteInfo:
        """Fetches athlete information."""
        print('Start fetching athlete information.')
        athlete_url = StravaEndpoints.get_athlete()

        try:
            response = requests.get(athlete_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            athlete_info = StravaAthleteInfo(**data)
        except requests.RequestException as e:
            print(f'HTTP error occurred: {e}')
            raise
        except ValidationError as e:
            print(f'Validation error: {e.errors()}')
            raise
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            raise
        return athlete_info

    def fetch_athlete_stats(self, athlete_id: str) -> StravaAthleteStats:
        """Fetches athlete statistics."""
        print('Start fetching athlete statistics.')
        stats_url = StravaEndpoints.get_athlete_stats(athlete_id)

        try:
            response = requests.get(stats_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            data['athlete_id'] = int(athlete_id)
            data['fetched_at'] = datetime.now(timezone.utc).isoformat()
            athlete_stats = StravaAthleteStats(**data)
        except requests.RequestException as e:
            print(f'HTTP error occurred: {e}')
            raise
        except ValidationError as e:
            print(f'Validation error: {e.errors()}')
            raise
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            raise
        return athlete_stats

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

        print(
            f'All activities fetched: {len(all_activities)} valid, {invalid_count} invalid.'
        )
        return all_activities

    def fetch_activity_streams(self, activity_id: str) -> dict[str, Any]:
        """Fetches activity streams by activity ID and stream types."""
        stream_url = f'https://www.strava.com/api/v3/activities/{activity_id}/streams'
        params = {
            'keys': 'time,distance,latlng,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving,grade_smooth',
            'key_by_type': 'true',
        }

        try:
            response = requests.get(
                stream_url, headers=self.headers, params=params, timeout=10
            )
            if response.status_code == 404:
                print(f'No streams available for activity {activity_id}')
                return {}

            response.raise_for_status()
            return cast(dict[str, Any], response.json())
        except requests.RequestException as e:
            print(f'HTTP error occurred: {e}')
            raise
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            raise

    def fetch_gear_details(self, gear_id: str) -> StravaGear:
        """Fetches gear details by gear ID."""
        print(f'Start fetching gear details for gear ID: {gear_id}')
        gear_url = StravaEndpoints.get_gear_details(gear_id)

        try:
            response = requests.get(gear_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return StravaGear(**response.json())
        except requests.RequestException as e:
            print(f'HTTP error occurred: {e}')
            raise
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            raise

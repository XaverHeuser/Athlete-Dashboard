"""This module."""

import os


def load_strava_auth(mode: str) -> tuple[str, str, str]:
    """Load Strava auth details from environment variables."""

    if mode == 'local':
        from dotenv import load_dotenv
        load_dotenv()
    elif mode != 'cloud':
        raise ValueError(f'Invalid mode given: {mode}')

    required_vars = ['CLIENT_ID', 'CLIENT_SECRET', 'REFRESH_TOKEN']
    values = [os.getenv(var) for var in required_vars]

    if not all(values):
        missing = [v for v, val in zip(required_vars, values) if not val]
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

    return tuple(values)

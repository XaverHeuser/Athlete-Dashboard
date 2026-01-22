"""This file contains general Google API connections."""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import Resource, build


def load_creds(TOKEN_FILE: str, SCOPES: list[str]) -> Credentials | None:
    """This function loads credentials for Google Auth."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())

    return creds


def make_flow(CLIENT_SECRET_FILE: str, SCOPES: list[str]) -> Flow:
    """Create and configure an OAuth 2.0 Flow using client secrets and scopes."""
    flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES)
    flow.redirect_uri = 'http://localhost:8501/Calendar'
    return flow


def get_service(creds: Credentials) -> Resource:
    """Build and return an authenticated Google Calendar API service resource."""
    return build('calendar', 'v3', credentials=creds)

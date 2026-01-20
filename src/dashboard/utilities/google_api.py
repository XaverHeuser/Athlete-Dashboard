"""File for..."""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import Resource, build


def load_creds(TOKEN_FILE: str, SCOPES: list[str]) -> Credentials | None:
    """TODO: Add."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)  # type: ignore[no-untyped-call]

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())  # type: ignore[no-untyped-call]
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())

    return creds


def make_flow(CLIENT_SECRET_FILE: str, SCOPES: list[str]) -> Flow:
    """TODO: Add."""
    flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES)
    flow.redirect_uri = 'http://localhost:8501/Calendar'
    return flow


def get_service(creds: Credentials) -> Resource:
    """TODO: Add"""
    return build('calendar', 'v3', credentials=creds)

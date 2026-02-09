"""This file contains streamlit authentication functions."""

import streamlit as st


def _get_allowed_emails() -> set[str]:
    """Get the set of allowed emails from secrets.toml."""
    # secrets.toml: [authz].allowed_emails = ["a@b.com", ...]
    emails = st.secrets.get('authz', {}).get('allowed_emails', [])
    return {e.strip().lower() for e in emails if isinstance(e, str) and e.strip()}


def require_login() -> None:
    """This functions handles the app login for via Google."""
    # If Streamlit auth isn't configured, is_logged_in won't exist.
    if not hasattr(st, "user") or not hasattr(st.user, "is_logged_in"):
        st.error("Authentication is not configured for this app run (missing [auth] in secrets.toml or wrong app root).")
        st.stop()

    # Authenticate user
    if not st.user.is_logged_in:
        st.header('This app is private.')
        st.subheader('Please log in.')

        if st.button('Log in with Google'):
            st.login()

        st.stop()

    # Authorization check
    email = (getattr(st.user, 'email', '') or '').strip().lower()
    allowed = _get_allowed_emails()

    if not email:
        st.error('Signed in, but no email claim was provided by the identity provider.')
        if st.button('Log out'):
            st.logout()
        st.stop()

    if not allowed:
        st.error('Access control is not configured. Contact the administrator.')
        st.caption(f'Signed in as: {email}')
        if st.button('Log out'):
            st.logout()
        st.stop()

    if email not in allowed:
        st.error('You are signed in, but not authorized to access this app.')
        st.caption(f'Signed in as: {email}')
        if st.button('Log out'):
            st.logout()
        st.stop()


def logout_button(location: str = 'sidebar') -> None:
    target = st.sidebar if location == 'sidebar' else st

    email = (getattr(st.user, 'email', '') or '').strip().lower()

    with target:
        if email:
            st.caption('Signed in as')
            st.markdown(f'**{email}**')

        if st.button('Log out'):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.logout()

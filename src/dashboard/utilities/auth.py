"""This file contains streamlit authentication functions."""

import streamlit as st


def _get_allowed_emails() -> set[str]:
    """Get the set of allowed emails from secrets.toml."""
    # secrets.toml: [authz].allowed_emails = ["a@b.com", ...]
    emails = st.secrets.get('authz', {}).get('allowed_emails', [])
    return {e.strip().lower() for e in emails if isinstance(e, str) and e.strip()}


def require_login() -> None:

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
    if target.button('Log out'):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.logout()

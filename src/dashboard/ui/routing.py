"""UI routing and query param helpers."""

from typing import Optional

import streamlit as st


ACTIVITY_ID_PARAM = 'activity_id'


# ------------------------------
# General query param helpers
# ------------------------------
def get_query_param(name: str) -> Optional[str]:
    """Return a query param as a single string (first element if list)."""
    val = st.query_params.get(name)

    if isinstance(val, list):
        return val[0] if val else None

    if isinstance(val, str):
        return val

    return None


def set_query_param(name: str, value: str) -> None:
    """Set a query param to a single string value."""
    st.query_params[name] = value


def clear_query_param(name: str) -> None:
    """Remove a query param."""
    qp = dict(st.query_params)
    qp.pop(name, None)
    st.query_params.clear()
    for key, value in qp.items():
        st.query_params[key] = value


# --------------------------
# Activity ID helpers
# --------------------------
def get_selected_activity_id() -> str | None:
    """Return the selected activity_id from query params."""
    return get_query_param(ACTIVITY_ID_PARAM)


def set_selected_activity_id(activity_id: str) -> None:
    """Set the selected activity_id in query params."""
    set_query_param(ACTIVITY_ID_PARAM, activity_id)


def clear_selected_activity_id() -> None:
    """Clear the selected activity_id from query params."""
    clear_query_param(ACTIVITY_ID_PARAM)


def get_selected_activity_id_int() -> int | None:
    """Convenience: parse activity_id as INT64-compatible int."""
    val = get_selected_activity_id()
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        clear_selected_activity_id()
        return None

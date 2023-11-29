import streamlit as st
from functools import wraps as _wraps


def _track_forbidden_keys(element):
    if "__track_forbidden_keys__" not in element.__dict__:
        element.__dict__["__track_forbidden_keys__"] = True

        @_wraps(element)
        def wrapper_element(*args, **kwargs):
            if "key" in kwargs:
                st.session_state._forbidden_keys.add(kwargs["key"])
            return element(*args, **kwargs)

        return wrapper_element

    return element


def legacy_session_state():
    # Initialize forbidden keys set.
    if "_forbidden_keys" not in st.session_state:
        st.session_state._forbidden_keys = set()

    # Self-assign session state items that are not in our forbidden set.
    # This actually translates widget state items to user-defined session
    # state items internally, which makes widget states persistent.
    for key, value in st.session_state.items():
        if key not in st.session_state._forbidden_keys:
            st.session_state[key] = value

    # We don't want to self-assign keys from the following widgets
    # to avoid a Streamlit API exception.
    # So we wrap them and save any used key in our _forbidden_keys set.
    st.button = _track_forbidden_keys(st.button)
    st.download_button = _track_forbidden_keys(st.download_button)
    st.file_uploader = _track_forbidden_keys(st.file_uploader)
    st.form = _track_forbidden_keys(st.form)

    # We can clear our set to avoid keeping unused widget keys over time.
    st.session_state._forbidden_keys.clear()
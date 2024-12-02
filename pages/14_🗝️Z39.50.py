import aiohttp
import asyncio
import json
import streamlit as st
from legacy_session_state import legacy_session_state
import requests
import logging
legacy_session_state()
import time

if 'allow_tenant' not in st.session_state:
    st.session_state['allow_tenant'] = False

if 'Allow_rest' not in st.session_state:
    st.session_state['Allow_rest'] = False

logging.basicConfig(level=logging.DEBUG)
hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_menu_style, unsafe_allow_html=True)
def Add_z39():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

st.title('Add Z39.5')



if st.session_state.allow_tenant:
    Add_z39()
else:
    st.warning("Please Connect to Tenant First.")
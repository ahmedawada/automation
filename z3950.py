import pandas as pd
from datetime import datetime
import streamlit as st
import json
import requests
from legacy_session_state import legacy_session_state
legacy_session_state()



hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_menu_style, unsafe_allow_html=True)


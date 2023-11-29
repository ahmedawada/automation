import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml import SafeLoader
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_title="KAM TEAM", layout="wide", initial_sidebar_state="expanded"
)


if 'new_tenant' not in st.session_state:
    st.session_state['new_tenant'] = False

if 'clone' not in st.session_state:
    st.session_state['clone'] = False

if 'backup_ten' not in st.session_state:
    st.session_state['backup_ten'] = False

with open('authentication.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],

)
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:

    authenticator.logout('Logout', 'sidebar')


    New_Tenant = st.button("Configure New Tenant")
    if New_Tenant:
        st.session_state.clone = False
        st.session_state.new_tenant = True
        st.session_state['backup_ten'] = False
        switch_page('Tenant')



    Clone_Tenant = st.button("Clone Existing Tenant")
    if Clone_Tenant:
        st.session_state.clone = True
        st.session_state.new_tenant = False
        st.session_state['backup_ten'] = False

        switch_page("Tenant")


    backup = st.button("Backup Tenant")
    if backup:
        st.session_state.backup_ten = True
        st.session_state.clone = False
        st.session_state.new_tenant = False
        switch_page('Tenant')



elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml import SafeLoader
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_title="KAM TEAM", layout="wide", initial_sidebar_state="expanded"
)

# Inject CSS styles
st.markdown(
    """
    <style>
    .button-container {
        display: flex;
        justify-content: space-around;
        margin-top: 20px;
    }
    .button-container div {
        flex: 1;
        margin: 0 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
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

    # Wrap buttons in a container
    st.markdown('<div class="button-container">', unsafe_allow_html=True)

    # Individual buttons in separate divs for styling
    st.markdown('<div>', unsafe_allow_html=True)
    New_Tenant = st.button("Login to Tenant")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div>', unsafe_allow_html=True)
    Clone_Tenant = st.button("Clone Existing Tenant")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div>', unsafe_allow_html=True)
    backup = st.button("Backup Tenant")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if New_Tenant:
        st.session_state.clone = False
        st.session_state.new_tenant = True
        st.session_state['backup_ten'] = False
        switch_page('tenant')

    if Clone_Tenant:
        st.session_state.clone = True
        st.session_state.new_tenant = False
        st.session_state['backup_ten'] = False
        switch_page('tenant')

    if backup:
        st.session_state.backup_ten = True
        st.session_state.clone = False
        st.session_state.new_tenant = False
        switch_page('tenant')

elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')

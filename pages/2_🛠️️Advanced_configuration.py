from Upload import upload_file
import streamlit as st
from Material_types import mtypes
from Statistical_Codes import stat_types
from user_group import user_groups
from Department import dept
from Location import loc
from Calendar import calendar, exceptions
from Column_Configuration import columns_config
from legacy_session_state import legacy_session_state
legacy_session_state()

if 'allow_tenant' not in st.session_state:
    st.session_state['allow_tenant'] = False

if 'allow_calendar' not in st.session_state:
    st.session_state['allow_calendar'] = False

hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_menu_style, unsafe_allow_html=True)
# st.session_state.update(st.session_state)
st.subheader('Advanced Configuration')
# if st.session_state.allow_tenant:
st.caption('Kindly Upload the Master Profilling document and insure all the sheets are filled properly!')
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(["Upload", "Material Types", "Statistical Codes", "User Groups",
                                                          "Location", "Departments", "Calendar", "Exceptions", "Configuration Columns"])

with tab1:
    if st.session_state.allow_tenant:
        upload_file()
    else:
        st.warning("Please Connect to Tenant First.")


with tab2:
    if st.session_state.allow_tenant:
        if st.session_state.profiling is not None and st.session_state['key'] is True:
            mtypes()
    else:
        st.warning("Please Connect to Tenant First.")

with tab3:
    if st.session_state.allow_tenant:

        if st.session_state.profiling is not None and st.session_state['key'] is True:
            stat_types()
    else:
        st.warning("Please Connect to Tenant First.")

with tab4:
    if st.session_state.allow_tenant:
        if st.session_state.profiling is not None and st.session_state['key'] is True:
            if 'Disdur' not in st.session_state:
                st.session_state.Disdur=False

            col1, col2 = st.columns(2)
            with col1:
                st.slider('Expiration Duration Offset', min_value=1, max_value=360, value=None, key='offsetduration',disabled=st.session_state.Disdur)
            with col2:
                st.checkbox('Disable Expiration Duration Offset',value=False, key='Disdur')
            user_groups()
    else:
        st.warning("Please Connect to Tenant First.")


with tab5:
    if st.session_state.allow_tenant:
        if st.session_state.profiling is not None and st.session_state['key'] is True:
            loc()
    else:
        st.warning("Please Connect to Tenant First.")

with tab6:
    if st.session_state.allow_tenant:
        if st.session_state.profiling is not None and st.session_state['key'] is True:
            dept()
    else:
        st.warning("Please Connect to Tenant First.")
with tab7:
    if st.session_state.allow_tenant:
    #     if st.session_state.profiling is not None and st.session_state['key'] is True:
        calendar()
    else:
        st.warning("Please Connect to Tenant First.")

with tab8:
    if st.session_state.allow_tenant:
        if st.session_state.profiling is not None and st.session_state['key'] is True:
            exceptions()
    else:
        st.warning("Please Connect to Tenant First.")
with tab9:
    if st.session_state.allow_tenant:
        if st.session_state.profiling is not None and st.session_state['key'] is True:
            columns_config()
    else:
        st.warning("Please Connect to Tenant First.")

import streamlit as st
from Upload import upload
import requests
from pandas import json_normalize
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import json

from legacy_session_state import legacy_session_state

# Get session state of legacy session
legacy_session_state()

if "department_activate" not in st.session_state:
    st.session_state.department_activate = True

def create_ugroup(df, expirationOffsetInDays):

    ugroupurl=f'{st.session_state.okapi}/groups'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

    if st.session_state.Disdur is False:
        for i in df.Medad:
            to_do={
          "group" : f"{i}",
          "desc" : f"{i}",
          "expirationOffsetInDays" : expirationOffsetInDays}


            requests.post(ugroupurl, data=json.dumps(to_do), headers=headers)
    elif st.session_state.Disdur is True:
        for i in df.Medad:
            to_do = {
                "group": f"{i}",
                "desc": f"{i}"}

            requests.post(ugroupurl, data=json.dumps(to_do), headers=headers)

def departments(df):
    department = f'{st.session_state.okapi}/departments'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    for index, row in df.iterrows():
        if row['Department'] is None:
            pass
        else:
            to_do = {
                "name": f"{row['Department']}",
                "code": f"{row['Department_code']}"}

            requests.post(department, data=json.dumps(to_do), headers=headers)

def user_groups():
    df = upload('User_groups')
    # Remove any rows with null values
    # df.dropna(inplace=True)
    # Strip leading and trailing whitespaces from "Medad" column
    df['Medad'] = df.Medad.str.strip()
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    # GET request to get current material types
    response = requests.get(f"{st.session_state.okapi}/groups", headers=headers).json()
    df_group = json_normalize(response['usergroups'])
    # Create an editable grid of the uploaded CSV data
    builder = GridOptionsBuilder.from_dataframe(df)
    builder.configure_selection(selection_mode='multiple', use_checkbox=True, header_checkbox=True)
    builder.configure_pagination(enabled=True)
    builder.configure_column('Medad', editable=True)
    builder.configure_column('Department', editable=True)
    builder.configure_column('Department_code', editable=True)
    go = builder.build()
    grid_return = AgGrid(df, editable=True, theme='balham', gridOptions=go)

    selected_rows = grid_return['selected_rows']
    # st.write(selected_rows)
    if bool(selected_rows):
        selection = pd.DataFrame(selected_rows)
        department_selection = selection.copy()
        AgGrid(selection[['Legacy System', 'Description', 'Medad','Department','Department_code']], theme='balham')
        medadlist = df_group.group.tolist()
        # Exclude already existing material types from the selection
        selection = selection[~selection['Medad'].isin(medadlist)]
        postit = st.button('Create User Groups', on_click=create_ugroup, args=[selection, st.session_state.offsetduration], )
        if postit:
            st.success('User Groups are Created')
            st.session_state.department_activate=False
        depart = st.button('Create Departments', on_click=departments, args=[department_selection],disabled=st.session_state.department_activate)
        if depart:
            st.success('Departments are created')
            st.session_state.department_activate = True

    else:
        st.warning('Please Select Required User Groups!!')


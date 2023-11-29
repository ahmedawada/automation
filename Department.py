import streamlit as st
from Upload import upload
import pandas as pd
import requests
import json
from st_aggrid import AgGrid, GridOptionsBuilder
from legacy_session_state import legacy_session_state

legacy_session_state()

def dept():
    st.title("Departments")
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    file = upload('Department')

    builder = GridOptionsBuilder.from_dataframe(file)
    builder.configure_selection(selection_mode='multiple', use_checkbox=True, header_checkbox=True)
    builder.configure_pagination(enabled=True)

    myList = ['Department name', 'Department Code']
    for item in myList:
        builder.configure_column(item, editable=True)

    go = builder.build()
    grid_return = AgGrid(file, editable=True, theme='balham', gridOptions=go)

    selected_rows = grid_return['selected_rows']

    if bool(selected_rows):
        selection = pd.DataFrame(selected_rows)
        createDept = st.button("Create Department")

        if createDept:
            with st.spinner(f'Creating Selected Departments..'):
                for index, row in selection.iterrows():
                    data = {
                        "name": row["Name"],
                        "code": row["Code"]
                    }
                    res = requests.post(f'{st.session_state.okapi}/departments', data=json.dumps(data), headers=headers)
                    st.success("Departments have been created.")
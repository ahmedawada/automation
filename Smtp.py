import streamlit as st
from Upload import upload
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import json
from legacy_session_state import legacy_session_state

legacy_session_state()
def post_smtp(df, headers):
    data = {
        "module": "SMTP_SERVER",
        "configName": "smtp",
        "code": "EMAIL_SMTP_HOST",
        "enabled": "true",
        "value": " smtp.gmail1.com"
    }
    data = json.dumps(data)
    response = requests.post(st.session_state.okapi + "/configurations/entries", data=data, headers=headers)
    return response

def smtp():
    df = upload('SMTP')
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    builder = GridOptionsBuilder.from_dataframe(df)
    builder.configure_selection(selection_mode='multiple', use_checkbox=True)
    #builder.set_selected_rows([0])
    go = builder.build()
    grid_return = AgGrid(df, editable=True, theme='balham', gridOptions=go)
    selected_rows = grid_return['selected_rows']
    # st.write(selected_rows)
    if bool(selected_rows):
        selection = pd.DataFrame(selected_rows)
        response = post_smtp(selection, headers)
        postit = st.button('Create SMTP ', on_click=post_smtp, args=[selection, headers],)
        if response.status_code == 201 and postit:
            st.success('SMTP Created')
        else:
            st.write(response)
            st.warning('Somthing went wrong !!')
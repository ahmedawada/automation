import requests
import json
import streamlit as st
from legacy_session_state import legacy_session_state

legacy_session_state()


def columns_config():

    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

    entries_endpoint = "/configurations/entries"

    # CHECK IF USER DISPLAY_COL EXISTS
    entries = requests.get(f'{st.session_state.okapi}{entries_endpoint}?query=(name==DISPLAY_COLUMNS)', headers=headers)


    # GET ALL CLASSIFICATION TYPES
    response = requests.get(f'{st.session_state.okapi}/classification-types', headers=headers).json()
    # ?query=cql.allRecords=1%20sortby%20name&limit=2000

    if not response["classificationTypes"]:
        st.warning("No classification types found.")
    else:
        types = []
        for i in response['classificationTypes']:
            types.append(i['name'])

        option = st.selectbox(
        'Classification Types:',
        (types))
        create_column = st.button("Create")

        if create_column:
            if option:
                class_id = ""
                # GET THE ID OF CHOSEN CLASSIFICATION TYPE
                for j in response['classificationTypes']:
                    if j['name'] == option:
                        class_id = j['id']

                config_res = requests.get(f'{st.session_state.okapi}{entries_endpoint}?query=(module== "CONFIGURATION_COLUMNS")', headers=headers).json()
                # st.write(config_res)
                data = {
                    "module": "CONFIGURATION_COLUMNS",
                    "configName": "DISPLAY_COLUMNS",
                    "value": "{\"cover\":true,\"publishers\":true,\"title\":true,\"indexTitle\":false,\"callNumber\":{\"classificationIdentifierType\":\"" + class_id + "\"},\"contributors\":false,\"publicationDate\":true,\"relation\":false}",
                }
                # if exists ,get Id and put, if not post without id
                if not config_res['configs']:
                    # CREATE NEW
                    res = requests.post(f'{st.session_state.okapi}{entries_endpoint}', data=json.dumps(data), headers=headers)
                    # st.write(res.content)
                    st.success('User (DISPLAY_COLUMNS) added successfully.')

                else:
                    config_id = config_res['configs'][0]['id']
                    res = requests.put(f'{st.session_state.okapi}{entries_endpoint}', data=json.dumps(data),
                                        headers=headers)
                    # st.write(res.content)
                    st.success('User (DISPLAY_COLUMNS) Updated successfully.')



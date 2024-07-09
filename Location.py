import streamlit as st
from Service_points import create_sp, create_institutions, create_campuses, create_libraries, create_locations
from Upload import upload
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder
from legacy_session_state import legacy_session_state

legacy_session_state()

def loc():

    st.title("Location")
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    file = upload('Location')

    builder = GridOptionsBuilder.from_dataframe(file)
    builder.configure_selection(selection_mode='multiple', use_checkbox=True, header_checkbox=True)
    builder.configure_pagination(enabled=True)

    myList = ['ServicePoints name', 'CampusNames', 'LibrariesName', 'LocationsName', 'InstitutionsName']
    for item in myList:
        builder.configure_column(item, editable=True)
    go = builder.build()
    grid_return = AgGrid(file, editable=True, theme='balham', gridOptions=go)

    selected_rows = grid_return['selected_rows']

    if bool(selected_rows):
        selection = pd.DataFrame(selected_rows)

        createLoc = st.button("Create locations")
        if createLoc:
            # CREATE EMPTY DICTIONARIES TO STORE DATA IN
            locations = {}
            locations_code = {}
            locations_lib = {}
            locations_camp = {}
            locations_inst = {}

            with st.spinner(f'Creating Selected Locations..'):
                for index, row in selection.iterrows():

                    name_result = requests.get(f'{st.session_state.okapi}/service-points?query=(name = {row["ServicePoints name"]})', headers=headers).json()
                    code_result = requests.get(f'{st.session_state.okapi}/service-points?query=(code = {row["ServicePoints Codes"]})', headers=headers).json()
                    empty = []

                    #------------------TEST------------------------
                    testVal = row["ServicePoints name"].strip()

                    st.write("the count is "+str(testVal.count('  '))+" and the trimmed value is "+testVal)

                    create_sp(row["ServicePoints name"], row["ServicePoints Codes"], row["ServicePoints name"],
                              row["ServicePoints name"])



                    result = requests.get(
                        f'{st.session_state.okapi}/location-units/institutions?query=(name=={row["InstitutionsName"]})',
                        headers=headers).json()

                    if result['locinsts'] == empty:
                        create_institutions(row["InstitutionsName"], row["InstitutionsCodes"])


                    # GET INSTITUTION ID
                    result = requests.get(
                        f'{st.session_state.okapi}/location-units/institutions?query=(name=={row["InstitutionsName"]})',
                        headers=headers).json()
                    insID = result['locinsts'][0]['id']


                    result2 = requests.get(
                        f'{st.session_state.okapi}/location-units/campuses?query=(name=={row["CampusNames"]})',
                        headers=headers).json()

                    if result2['loccamps'] == empty:
                        create_campuses(row["CampusNames"], row["CampusCodes"], insID)


                    # CREATING LIBRARIES
                    result = requests.get(
                        f'{st.session_state.okapi}/location-units/campuses?query=(name=={row["CampusNames"]})',
                        headers=headers).json()

                    campusID = result['loccamps'][0]['id']

                    result2 = requests.get(
                        f'{st.session_state.okapi}/location-units/libraries?query=(name=={row["LibrariesName"]})',
                        headers=headers).json()

                    if result2['loclibs'] == empty:
                        create_libraries(row['LibrariesName'], row['LibrariesCodes'], campusID)

                    # else:
                        # st.warning(f'Libary ({row["LibrariesName"]}) already exists.')

                    # FILL LOCATION DICTIONARY
                    result = requests.get(
                        f'{st.session_state.okapi}/service-points?query=(name=={row["ServicePoints name"]})',
                        headers=headers).json()

                    spid = result['servicepoints'][0]['id']
                    if locations.get(row['LocationsName']) is not None:
                        locations_code[row['LocationsName']].append(row['LocationsCodes'])
                        locations_lib[row['LocationsName']].append(row['LibrariesName'])
                        locations_camp[row['LocationsName']].append(campusID)
                        locations_inst[row['LocationsName']].append(insID)

                        if spid not in locations[row['LocationsName']]:
                            locations[row['LocationsName']].append(spid)

                    else:
                        locations[row['LocationsName']] = [spid]
                        locations_code[row['LocationsName']] = [row['LocationsCodes']]
                        locations_lib[row['LocationsName']] = [row['LibrariesName']]
                        locations_camp[row['LocationsName']] = [campusID]
                        locations_inst[row['LocationsName']] = [insID]

                for key in locations:
                    for i in range(0, len(locations_code[key])):
                        code = locations_code[key][i]
                        camp_id = locations_camp[key][i]
                        inst_id = locations_inst[key][i]

                        # GET LIBRARY ID
                        res = requests.get(f'{st.session_state.okapi}/location-units/libraries?query=(name=={locations_lib[key][i]})',
                                           headers=headers).json()
                        lib_ID = res['loclibs'][0]['id']

                        create_locations(key, code, key, inst_id, camp_id, lib_ID, locations[key][0], locations[key])

            st.success("Locations have been created.")
            st.session_state['allow_calendar'] = True
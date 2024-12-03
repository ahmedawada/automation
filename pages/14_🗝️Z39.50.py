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
    # Checkbox group
    # options = ["NLM", "APL", "American University of Beirut - AUB (Lebanon)", "British Library", "OCLC", "OhioLink",
    #            "Yale University", "Indiana"]
    # selected_options = []
    profiles = requests.get(f'{st.session_state.okapi}/copycat/profiles?limit=200', headers=headers).json()
    pro_names = []
    for l in profiles['profiles']:
        pro_names.append(l['name'])

    options = st.multiselect(
        'Please choose Profiles to create',
        ['NLM', 'APL', 'American University of Beirut - AUB (Lebanon)', 'British Library', 'OCLC',
         'OhioLink', "Yale University", "Indiana"])
    if st.button("Create"):
        with st.spinner(f'Creating Profiles....'):
            # time.sleep(5)
            if options:
                for i in range(0, len(options)):
                    lib = options[i]
                    if lib in pro_names:
                        st.warning(f'{lib} Already exists.')
                    else:
                        if lib == 'NLM':
                            data = {
                                "name": "NLM",
                                "url": "na91.alma.exlibrisgroup.com:1921/01NLM_INST",
                                "externalIdQueryMap": "@attr 1=7 $identifier",
                                "internalIdEmbedPath": "999ff$i",
                                "createJobProfileId": "d0ebb7b0-2f0f-11eb-adc1-0242ac120002",
                                "updateJobProfileId": "91f9b8d6-d80e-4727-9783-73fb53e3c786",
                                "allowedCreateJobProfileIds": [
                                    "d0ebb7b0-2f0f-11eb-adc1-0242ac120002"
                                ],
                                "allowedUpdateJobProfileIds": [
                                    "91f9b8d6-d80e-4727-9783-73fb53e3c786"
                                ],
                                "targetOptions": {
                                    "preferredRecordSyntax": "MARC21"
                                },
                                "externalIdentifierType": "8261054f-be78-422d-bd51-4ed9f33c3422",
                                "enabled": True,
                                "isBib": True
                            }
                        elif lib == 'APL':
                            data = {
                                "name": "APL",
                                "url": "unicorn.alc.org:2200/PUBLIC",
                                "externalIdQueryMap": "@attr 1=9 $identifier",
                                "internalIdEmbedPath": "999ff$i",
                                "createJobProfileId": "d0ebb7b0-2f0f-11eb-adc1-0242ac120002",
                                "updateJobProfileId": "91f9b8d6-d80e-4727-9783-73fb53e3c786",
                                "allowedCreateJobProfileIds": [
                                    "d0ebb7b0-2f0f-11eb-adc1-0242ac120002"
                                ],
                                "allowedUpdateJobProfileIds": [
                                    "91f9b8d6-d80e-4727-9783-73fb53e3c786"
                                ],
                                "targetOptions": {
                                    "preferredRecordSyntax": "USMARC"
                                },
                                "externalIdentifierType": "c858e4f2-2b6b-4385-842b-60732ee14abb",
                                "enabled": True,
                                "isBib": True
                            }
                        elif lib == 'American University of Beirut - AUB (Lebanon)':
                            data = {
                                "name": "American University of Beirut - AUB (Lebanon)",
                                "url": "libcat.aub.edu.lb:210/INNOPAC",
                                "externalIdQueryMap": "@attr 1=7 $identifier",
                                "internalIdEmbedPath": "999ff$i",
                                "createJobProfileId": "d0ebb7b0-2f0f-11eb-adc1-0242ac120002",
                                "updateJobProfileId": "91f9b8d6-d80e-4727-9783-73fb53e3c786",
                                "allowedCreateJobProfileIds": [
                                    "d0ebb7b0-2f0f-11eb-adc1-0242ac120002"
                                ],
                                "allowedUpdateJobProfileIds": [
                                    "91f9b8d6-d80e-4727-9783-73fb53e3c786"
                                ],
                                "targetOptions": {
                                    "charset": "UTF8",
                                    "prefferedRecordSyntax": "USMARC"
                                },
                                "externalIdentifierType": "8261054f-be78-422d-bd51-4ed9f33c3422",
                                "enabled": True,
                                "isBib": True
                            }
                        elif lib == 'British Library':
                            data = {
                                "name": "British Library",
                                "url": "z3950cat.bl.uk:9909/BNB03U",
                                "externalIdQueryMap": "@attr 1=9 $identifier",
                                "internalIdEmbedPath": "999ff$i",
                                "createJobProfileId": "d0ebb7b0-2f0f-11eb-adc1-0242ac120002",
                                "updateJobProfileId": "91f9b8d6-d80e-4727-9783-73fb53e3c786",
                                "allowedCreateJobProfileIds": [
                                    "d0ebb7b0-2f0f-11eb-adc1-0242ac120002"
                                ],
                                "allowedUpdateJobProfileIds": [
                                    "91f9b8d6-d80e-4727-9783-73fb53e3c786"
                                ],
                                "targetOptions": {
                                    "preferredRecordSyntax": "MARC21"
                                },
                                "externalIdentifierType": "c858e4f2-2b6b-4385-842b-60732ee14abb",
                                "enabled": True,
                                "isBib": True
                            }
                        elif lib == 'OCLC':
                            data = {
                                "name": "OCLC",
                                "url": "zcat.oclc.org:210/OLUCWorldCat",
                                "externalIdQueryMap": "@attr 1=9 $identifier",
                                "internalIdEmbedPath": "999ff$i",
                                "createJobProfileId": "d0ebb7b0-2f0f-11eb-adc1-0242ac120002",
                                "updateJobProfileId": "91f9b8d6-d80e-4727-9783-73fb53e3c786",
                                "allowedCreateJobProfileIds": [
                                    "d0ebb7b0-2f0f-11eb-adc1-0242ac120002"
                                ],
                                "allowedUpdateJobProfileIds": [
                                    "91f9b8d6-d80e-4727-9783-73fb53e3c786"
                                ],
                                "targetOptions": {
                                    "preferredRecordSyntax": "usmarc"
                                },
                                "externalIdentifierType": "8261054f-be78-422d-bd51-4ed9f33c3422",
                                "enabled": True,
                                "isBib": True
                            }
                        elif lib == 'OhioLink':
                            data = {
                                "name": "OhioLink",
                                "url": "olc1.ohiolink.edu:210/INNOPAC",
                                "externalIdQueryMap": "@attr 1=7 $identifier",
                                "internalIdEmbedPath": "999ff$i",
                                "createJobProfileId": "d0ebb7b0-2f0f-11eb-adc1-0242ac120002",
                                "updateJobProfileId": "91f9b8d6-d80e-4727-9783-73fb53e3c786",
                                "allowedCreateJobProfileIds": [
                                    "d0ebb7b0-2f0f-11eb-adc1-0242ac120002"
                                ],
                                "allowedUpdateJobProfileIds": [
                                    "91f9b8d6-d80e-4727-9783-73fb53e3c786"
                                ],
                                "targetOptions": {
                                    "preferredRecordSyntax": "MARC21"
                                },
                                "externalIdentifierType": "8261054f-be78-422d-bd51-4ed9f33c3422",
                                "enabled": True,
                                "isBib": True
                            }
                        elif lib == 'Yale University':
                            data = {
                                "name": "Yale University",
                                "url": "z3950.library.yale.edu:7090/voyager",
                                "externalIdQueryMap": "@attr 1=7 $identifier",
                                "internalIdEmbedPath": "999ff$i",
                                "createJobProfileId": "d0ebb7b0-2f0f-11eb-adc1-0242ac120002",
                                "updateJobProfileId": "91f9b8d6-d80e-4727-9783-73fb53e3c786",
                                "allowedCreateJobProfileIds": [
                                    "d0ebb7b0-2f0f-11eb-adc1-0242ac120002"
                                ],
                                "allowedUpdateJobProfileIds": [
                                    "91f9b8d6-d80e-4727-9783-73fb53e3c786"
                                ],
                                "targetOptions": {
                                    "preferredRecordSyntax": "USMARC"
                                },
                                "externalIdentifierType": "8261054f-be78-422d-bd51-4ed9f33c3422",
                                "enabled": True,
                                "isBib": True
                            }
                        elif lib == 'Indiana':
                            data = {
                                "name": "Indiana",
                                "url": "libprd.uits.indiana.edu:2200/UNICORN",
                                "externalIdQueryMap": "@attr 1=9 $identifier",
                                "internalIdEmbedPath": "999ff$i",
                                "createJobProfileId": "d0ebb7b0-2f0f-11eb-adc1-0242ac120002",
                                "updateJobProfileId": "91f9b8d6-d80e-4727-9783-73fb53e3c786",
                                "allowedCreateJobProfileIds": [
                                    "d0ebb7b0-2f0f-11eb-adc1-0242ac120002"
                                ],
                                "allowedUpdateJobProfileIds": [
                                    "91f9b8d6-d80e-4727-9783-73fb53e3c786"
                                ],
                                "targetOptions": {
                                    "preferredRecordSyntax": "USMARC"
                                },
                                "externalIdentifierType": "c858e4f2-2b6b-4385-842b-60732ee14abb",
                                "enabled": True,
                                "isBib": True
                            }
                        post_z = requests.post(f'{st.session_state.okapi}/copycat/profiles', headers=headers, data=json.dumps(data))
                        st.success(f"{lib} created.")
            else:
                st.warning('No Library Chosen')






        # if selected_options:
        #     for i in range(0, len(options)):
        #         z39 = options[i]


st.title('Add Z39.5')


if st.session_state.allow_tenant:
    Add_z39()
else:
    st.warning("Please Connect to Tenant First.")
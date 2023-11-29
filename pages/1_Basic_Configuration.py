import streamlit as st
import requests
import json
from legacy_session_state import legacy_session_state
legacy_session_state()
from permissions import apiperm, fullperms, circ, Acquisition, cataloging, admins, search
from Notices import send_notice
from extras import profile_picture,price_note,sources_config,loan_type,default_job_profile,api_key_check,alt_types, post_locale, addDepartments,circ_other,circ_loanhist,export_profile,auc,default_sources,local_validation,validation_types
import time


hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_menu_style, unsafe_allow_html=True)






def configure_tenant():
    Config_url = f"{st.session_state.okapi}/configurations/entries?limit=1000"
    post_url = f"{st.session_state.okapi}/configurations/entries"
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    response = requests.get(Config_url, headers=headers).json()

    reset = {
        "module": "USERSBL",
        "configName": "smtp",
        "code": "FOLIO_HOST",
        "description": "email reset host",
        "default": "true",
        "enabled": "true",
        "value": f"{st.session_state.clienturl}",
    }

    tagput = {
        "module": "HEADING_VERIFICATION",
        "configName": "tagMappings",
        "enabled": "true",
        "value": '{"100":{"mapTo":"Author","mapSubfields":["b","c","d","f","g","j","l","n","q","u","p","a","e"],"replacedSubfields":["b","c","d","f","g","j","l","n","p","q","u","a","e"]},"110":{"mapTo":"Author","mapSubfields":["a","b","c","d","e","f","g","k","l","n","p","t","u"],"replacedSubfields":["a","b","c","d","e","f","g","k","l","n","p","t","u"]},"111":{"mapTo":"Author","mapSubfields":["a","c","d","e","f","g","j","k","l","n","p","q","t"],"replacedSubfields":["a","c","d","e","f","g","j","k","l","n","p","q","t"]},"130":{"mapTo":"Series","mapSubfields":["a","d","f","g","h","k","l","m"],"replacedSubfields":["a","d","f","g","h","k","l","m","n"]},"600":{"mapTo":"Subject","mapSubfields":["a","b","c","d","e","f","g","h","j","k","l","m","n","o","v","x","y","z","t"],"replacedSubfields":["a","b","c","d","e","f","g","h","j","k","t","x","y","z","v"]},"610":{"mapTo":"Subject","mapSubfields":["a","b","c","d","v","x","y","z"],"replacedSubfields":["a","b","c","d","x","y","z","v"]},"611":{"mapTo":"Subject","mapSubfields":["a","c","d","e","f","g","x","y","z","v"],"replacedSubfields":["a","c","d","e","f","g","x","y","z","v"]},"650":{"mapTo":"Subject","mapSubfields":["a","b","c","d","e","g","v","x","y","z"],"replacedSubfields":["a","b","c","d","e","g","v","x","y","z"]},"651":{"mapTo":"Subject","mapSubfields":["a","e","g","v","x","y","z"],"replacedSubfields":["a","e","g","v","x","y","z"]},"700":{"mapTo":"Author","mapSubfields":["a","b","c","d","t","e"],"replacedSubfields":["a","b","c","d","t","e"]},"710":{"mapTo":"Author","mapSubfields":["a","b","c","d","t"],"replacedSubfields":["a","b","c","d","t"]},"711":{"mapTo":"Author","mapSubfields":["a","c","d","e","f","g","t"],"replacedSubfields":["a","c","d","e","f","g","t"]},"830":{"mapTo":"Series","mapSubfields":["a","d","f","g","h","k","l","m"],"replacedSubfields":["a","d","f","g","h","k","l","m"]}}',
    }

    marc = {
      "module": "MARCEDITOR",
      "configName": "default_job_profile_id",
      "enabled": "true",
      "value": "e34d7b92-9b83-11eb-a8b3-0242ac130003"
}

    n = 0
    for r in response["configs"]:
        if "USERSBL" in response["configs"][n]["module"]:
            userid = response["configs"][n]["id"]

            requests.put(
                post_url + "/" + userid, data=json.dumps(reset), headers=headers
            )
        else:
            responsepost = requests.post(
                post_url, data=json.dumps(reset), headers=headers
            )
        n += 1

    n = 0
    for r in response["configs"]:
        if "HEADING_VERIFICATION" in response["configs"][n]["module"]:

            tagid = response["configs"][n]["id"]

            requests.put(
                post_url + "/" + tagid, data=json.dumps(tagput), headers=headers
            )

        else:
            requests.post(
                post_url, data=json.dumps(tagput), headers=headers)
        n += 1

    n = 0
    for r in response["configs"]:
        if "MARCEDITOR" in response["configs"][n]["module"]:
            if 'e34d7b92-9b83-11eb-a8b3-0242ac130003' != response['configs'][n]['module']['MARCEDITOR']['value']:
                st.warning('Please Check Your Job Load Profile Manually!')
            else:
                requests.post(post_url, data=json.dumps(marc), headers=headers)

    n += 1
    return responsepost.json()


def perm():

    perm_sets = [
        {"displayName": "Naseej", "description": "Naseej", "subPermissions": fullperms},
        {"displayName": "UserAPI", "description": "User API", "subPermissions": apiperm},
        {"displayName": "Circulation", "description": "Circulation Permissions", "subPermissions": circ},
        {"displayName": "Cataloging", "description": "Cataloging Permissions", "subPermissions": cataloging},
        {"displayName": "Acquisition", "description": "Acquisition Permissions", "subPermissions": Acquisition},
        {"displayName": "admin", "description": "admin Permissions", "subPermissions": admins},
        {"displayName": "search", "description": "Search Permissions", "subPermissions": search}
    ]

    headers = {
        "x-okapi-tenant": f"{st.session_state.tenant}",
        "x-okapi-token": f"{st.session_state.token}"
    }

    for perm_set in perm_sets:
        # Make a GET request to check if the permission set already exists
        response = requests.get(
            f"{st.session_state.okapi}/perms/permissions?query=(displayName=={perm_set['displayName']})",
            headers=headers)

        if len(response.content) == 47:  # Assuming the length 47 indicates the absence of the permission set
            try:
                # Post the permission set if it doesn't exist
                perm_post=requests.post(f"{st.session_state.okapi}/perms/permissions", headers=headers,
                              data=json.dumps(perm_set))

            except requests.exceptions.RequestException as err:
                st.write(f"Failed to post permission set '{perm_set['displayName']}': {err}")

st.subheader("Basic Tenant Configuration")
st.caption("in Order to start tenant configuration, kindly paste Medad ILS url (ex https://medad.ils.com ) and click on start configuration button.")
if st.session_state.allow_tenant:
    c1,c2=st.columns(2)

    with c1:
        st.text_input("Enter Client URL", key="clienturl")
        headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

        check_api = requests.get(f'{st.session_state.okapi}/configurations/entries?query=configName==apiKey', headers=headers).json()
        check_api = check_api['configs']

        if 'api_check_flag' not in st.session_state:
            st.session_state['api_check_flag'] = False

        # check if no api key configured
        if not check_api:
            st.text_input("Enter API Key", key="apiKey")
            st.session_state['api_check_flag'] = True
        else:
            st.warning(f"API Key Already Configured ({check_api[0]['value']})")
            st.session_state['Allow_rest'] = True

        st.write('---')

    with c2:

        st.selectbox('TimeZone',options=('Asia/Kuwait','Asia/Riyadh','Asia/Bahrain','Asia/Dubai','Asia/Muscat','Asia/Qatar'),key='Timezone')
        st.selectbox('Currency',options=('KWD','SAR','BHD','AED','OMR','QAR'),key='currency')

    start = st.button("Start")
    if 'btn2' not in st.session_state:
        st.session_state['btn2'] = False

    if st.session_state.get('start_btn') != True:
        st.session_state.start_btn = start

    if start:
        if st.session_state.start_btn is True:
            with st.spinner(f'Configuring the {st.session_state.tenant} Tenant'):
                time.sleep(5)
                api_key_check()
                if st.session_state.Allow_rest and st.session_state.allow_tenant:

                    configure_tenant()
                    st.success("Reset Password Link has Been Fixed and Tag Mappings are added")
                    perm()
                    st.success('Permission Sets Are Created')
                    send_notice()
                    st.success('Notices Templates are Created')
                    price_note()
                    loan_type()
                    st.success('Price Note and Loan Type are Created')
                    default_job_profile()
                    st.success('Default Job Profile has been Modified')
                    alt_types()
                    st.success('Alternative Titles Have been Added')
                    api_key_check()
                    post_locale(st.session_state.Timezone, st.session_state.currency)
                    st.success('Session Locale is configured')
                    addDepartments()
                    st.success("Depatment added successfully.")
                    circ_other()
                    circ_loanhist()
                    export_profile()
                    auc()
                    default_sources()
                    local_validation()
                    validation_types()
                    sources_config()
                    profile_picture()

                    st.success("Tenant is now Configured", icon="✅")
                    st.session_state['btn2'] = True
else:
    st.warning("Please Connect to Tenant First.")









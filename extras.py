import requests
import json
import pandas as pd
import streamlit as st
from legacy_session_state import legacy_session_state
legacy_session_state()

if 'Allow_rest' not in st.session_state:
    st.session_state['Allow_rest'] = False

def price_note():
    price = {"source": "automation", "name": "price"}
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    requests.post(f"{st.session_state.okapi}/item-note-types", headers=headers,
                              data=json.dumps(price))

def api_key_check():
    if st.session_state.allow_tenant:
        headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

        if st.session_state['api_check_flag']:
            key = st.session_state.apiKey
            if len(key) != 48:
                st.warning("Please Validate API Key.")
                st.session_state['Allow_rest'] = False

            else:
                st.session_state['Allow_rest'] = True
                data = {
                    "module": "HEADING_VERIFICATION",
                    "configName": "apiKey",
                    "enabled": True,
                    "value": key
                }
                requests.post(f"{st.session_state.okapi}/configurations/entries", data=json.dumps(data), headers=headers)
                st.session_state['api_check_flag'] = False
                st.success('Api Key has been Created')


def loan_type():
    loantype = {"name": "Non circulating"}
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    requests.post(f"{st.session_state.okapi}/loan-types", headers=headers, data=json.dumps(loantype))

def default_job_profile():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    response = requests.get(f"{st.session_state.okapi}/configurations/entries?query=(module=MARCEDITOR and configName=default_job_profile_id)",headers=headers)
    data = response.json()
    default_job = {"module": "MARCEDITOR", "configName": "default_job_profile_id", "value": "e34d7b92-9b83-11eb-a8b3-0242ac130003"}
    empty = []

    if data['configs'] == empty:
        requests.post(f"{st.session_state.okapi}/configurations/entries", data=json.dumps(default_job),headers=headers)

    else:

        requests.put(f"{st.session_state.okapi}/configurations/entries/{data['configs'][0]['id']}",
                     data=json.dumps(default_job), headers=headers)
def alt_types():
    alt_typesurl=f"{st.session_state.okapi}/alternative-title-types"
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    altlist=['Uniform title','Variant title', 'General topology', 'Former title']

    for i in altlist:
        to_do={
      "name" : f"{i}",
      "source" : "Automation"
}
        requests.post(alt_typesurl, data=json.dumps(to_do), headers=headers)

def addDepartments():

    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    data = {
        "name": "Main",
        "code": "main"
    }
    res = requests.post(f'{st.session_state.okapi}/departments', data=json.dumps(data),headers=headers)

def post_locale(timezone,currency):


    #post /configurations/entries
    get_config = f"{st.session_state.okapi}/configurations/entries?query=(module==ORG and configName==localeSettings)"
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    response = requests.get(get_config, headers=headers).json()
    # st.write(response)
    if not response['configs']:
        st.write('here')
        to_do = {
            "module": "ORG",
            "configName": "localeSettings",
            "enabled": True,
            "value": f'{{"locale":"en-US","timezone":"{timezone}","currency":"{currency}"}}'
        }
        test = requests.post(f"{st.session_state.okapi}/configurations/entries", headers=headers, data=json.dumps(to_do))
        # st.write(test.content)
        response = requests.get(get_config, headers=headers).json()
        # st.write(response)
    id = response['configs'][0]['id']
    update_config = f"{st.session_state.okapi}/configurations/entries/{id}"
    to_do = {"configName": "localeSettings" , "enabled": True , "id": f"{id}" , "module": "ORG" ,
    "value": f'{{"locale":"en-US","timezone":"{timezone}","currency":"{currency}"}}'}
    resp = requests.put(update_config , data=json.dumps(to_do) , headers=headers)


def circ_other():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    body =  {"module": "CHECKOUT", "configName": "other_settings",
         "enabled": True,
         "value": "{\"audioAlertsEnabled\":True,\"audioTheme\":\"modern\",\"checkoutTimeout\":True,\"checkoutTimeoutDuration\":3,\"prefPatronIdentifier\":\"barcode,username\",\"useCustomFieldsAsIdentifiers\":false,\"wildcardLookupEnabled\":True}"}

    try:
        # GET request to check if the configuration entry exists
        validation_response = requests.get(
            f'{st.session_state.okapi}/configurations/entries?query=(module=CHECKOUT and configName=other_settings)',
            headers=headers
        )
        validation_response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        configs = validation_response.json().get('configs',
                                                 [])  # Get the 'configs' list or an empty list if it doesn't exist

        if configs:  # Check if the 'configs' list is not empty
            config_id = configs[0]['id']  # Access the first element if it exists

            # Perform a PUT request to update the existing entry
            validation_response_post = requests.put(
                f'{st.session_state.okapi}/configurations/entries/{config_id}',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        else:
            # Perform a POST request to create a new entry if 'configs' list is empty
            validation_response_post = requests.post(
                f'{st.session_state.okapi}/configurations/entries',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

    except requests.exceptions.RequestException as err:
        print("Oops! Something went wrong:", err)

def circ_loanhist():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    body =  {"module":"LOAN_HISTORY","configName":"loan_history","enabled":True,"value":"{\"closingType\":{\"loan\":\"never\",\"feeFine\":null,\"loanExceptions\":[]},\"loan\":{},\"feeFine\":{},\"loanExceptions\":[],\"treatEnabled\":false}"}

    try:
        # GET request to check if the configuration entry exists
        validation_response = requests.get(
            f'{st.session_state.okapi}/configurations/entries?query=(module=LOAN_HISTORY and configName=loan_history)',
            headers=headers
        )
        validation_response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        configs = validation_response.json().get('configs',
                                                 [])  # Get the 'configs' list or an empty list if it doesn't exist

        if configs:  # Check if the 'configs' list is not empty
            config_id = configs[0]['id']  # Access the first element if it exists

            # Perform a PUT request to update the existing entry
            validation_response_post = requests.put(
                f'{st.session_state.okapi}/configurations/entries/{config_id}',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        else:
            # Perform a POST request to create a new entry if 'configs' list is empty
            validation_response_post = requests.post(
                f'{st.session_state.okapi}/configurations/entries',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

    except requests.exceptions.RequestException as err:
        print("Oops! Something went wrong:", err)

def export_profile():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    body = {"transformations":[{"fieldId":"holdings.callnumber","path":"$.holdings[*].callNumber","recordType":"HOLDINGS","transformation":"99900$a","enabled":True},{"fieldId":"holdings.callnumbertype","path":"$.holdings[*].callNumberTypeId","recordType":"HOLDINGS","transformation":"99900$w","enabled":True},{"fieldId":"item.barcode","path":"$.holdings[*].items[*].barcode","recordType":"ITEM","transformation":"99900$i","enabled":True},{"fieldId":"item.copynumber","path":"$.holdings[*].items[*].copyNumber","recordType":"ITEM","transformation":"99900$c","enabled":True},{"fieldId":"item.effectivelocation.name","path":"$.holdings[*].items[*].effectiveLocationId","recordType":"ITEM","transformation":"99900$l","enabled":True},{"fieldId":"item.materialtypeid","path":"$.holdings[*].items[*].materialTypeId","recordType":"ITEM","transformation":"99900$t","enabled":True},{"fieldId":"item.itemnotetypeid.price","path":"$.holdings[*].items[*].notes[?(@.itemNoteTypeId=='bd68d7f1-2535-48af-bfac-c554cf8204f6' && (!(@.staffOnly) || @.staffOnly == false))].note","recordType":"ITEM","transformation":"99900$p","enabled":True},{"fieldId":"item.status","path":"$.holdings[*].items[*].status.name","recordType":"ITEM","transformation":"99900$s","enabled":True},{"fieldId":"item.volume","path":"$.holdings[*].items[*].volume","recordType":"ITEM","transformation":"99900$v","enabled":True}],"recordTypes":["SRS","HOLDINGS","ITEM"],"outputFormat":"MARC","name":"Medad Export"}
    export_pro = requests.post(f'{st.session_state.okapi}/data-export/mapping-profiles',data=json.dumps(body),headers=headers)

def auc():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    body={"id":None,"name":"AUC","externalIdQueryMap":"@attr 1=12 $identifier","internalIdEmbedPath":"999ff$a","createJobProfileId":"d0ebb7b0-2f0f-11eb-adc1-0242ac120002","updateJobProfileId":"91f9b8d6-d80e-4727-9783-73fb53e3c786","externalIdentifierType":"d678f0d3-6cb2-4dbc-94b0-6e6a091d615a","enabled":True}
    auc_put = requests.put(f'{st.session_state.okapi}/copycat/auc-profile',data=json.dumps(body),headers=headers)

def default_sources():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    body =  {"module":"HEADING_VERIFICATION","configName":"defaultSourceConfig","enabled":True,"value":"{\"ar\":[\"AUC\"],\"en\":[\"LC\"]}"}

    try:
        # GET request to check if the configuration entry exists
        validation_response = requests.get(
            f'{st.session_state.okapi}/configurations/entries?query=(module=HEADING_VERIFICATION and configName=defaultSourceConfig)',
            headers=headers
        )
        validation_response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        configs = validation_response.json().get('configs',
                                                 [])  # Get the 'configs' list or an empty list if it doesn't exist

        if configs:  # Check if the 'configs' list is not empty
            config_id = configs[0]['id']  # Access the first element if it exists

            # Perform a PUT request to update the existing entry
            validation_response_post = requests.put(
                f'{st.session_state.okapi}/configurations/entries/{config_id}',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        else:
            # Perform a POST request to create a new entry if 'configs' list is empty
            validation_response_post = requests.post(
                f'{st.session_state.okapi}/configurations/entries',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

    except requests.exceptions.RequestException as err:
        print("Oops! Something went wrong:", err)


def local_validation():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

    body ={"module":"HEADING_VERIFICATION","configName":"localValidationConfig","enabled":True,"value":"{\"enabled\":true}"}
    try:
        # GET request to check if the configuration entry exists
        validation_response = requests.get(
            f'{st.session_state.okapi}/configurations/entries?query=(module=HEADING_VERIFICATION and configName=localValidationConfig)',
            headers=headers
        )
        validation_response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        configs = validation_response.json().get('configs',
                                                 [])  # Get the 'configs' list or an empty list if it doesn't exist

        if configs:  # Check if the 'configs' list is not empty
            config_id = configs[0]['id']  # Access the first element if it exists

            # Perform a PUT request to update the existing entry
            validation_response_post = requests.put(
                f'{st.session_state.okapi}/configurations/entries/{config_id}',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        else:
            # Perform a POST request to create a new entry if 'configs' list is empty
            validation_response_post = requests.post(
                f'{st.session_state.okapi}/configurations/entries',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

    except requests.exceptions.RequestException as err:
        print("Oops! Something went wrong:", err)


def validation_types():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    body = {"module":"HEADING_VERIFICATION","configName":"localValidationTypesConfig","enabled":True,"value":"{\"types\":[{\"name\":\"Author\"},{\"name\":\"Subject\"},{\"name\":\"Series\"}]}"}

    try:
        # GET request to check if the configuration entry exists
        validation_response = requests.get(
            f'{st.session_state.okapi}/configurations/entries?query=(module=HEADING_VERIFICATION and configName=localValidationTypesConfig)',
            headers=headers
        )
        validation_response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        configs = validation_response.json().get('configs',
                                                 [])  # Get the 'configs' list or an empty list if it doesn't exist

        if configs:  # Check if the 'configs' list is not empty
            config_id = configs[0]['id']  # Access the first element if it exists

            # Perform a PUT request to update the existing entry
            validation_response_post = requests.put(
                f'{st.session_state.okapi}/configurations/entries/{config_id}',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        else:
            # Perform a POST request to create a new entry if 'configs' list is empty
            validation_response_post = requests.post(
                f'{st.session_state.okapi}/configurations/entries',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

    except requests.exceptions.RequestException as err:
        print("Oops! Something went wrong:", err)

def sources_config():

    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    body = {"module":"HEADING_VERIFICATION","configName":"sourceConfigs","enabled":True,"value":"{\"AUC\":{\"secondIndicator\":\"7\",\"verificationSourceIdentifier\":\"AUCSH\"},\"LC\":{\"secondIndicator\":\"1\"}}"}

    try:
        # GET request to check if the configuration entry exists
        validation_response = requests.get(
            f'{st.session_state.okapi}/configurations/entries?query=(module=HEADING_VERIFICATION and configName=sourceConfigs)',
            headers=headers
        )
        validation_response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        configs = validation_response.json().get('configs',
                                                 [])  # Get the 'configs' list or an empty list if it doesn't exist

        if configs:  # Check if the 'configs' list is not empty
            config_id = configs[0]['id']  # Access the first element if it exists

            # Perform a PUT request to update the existing entry
            validation_response_post = requests.put(
                f'{st.session_state.okapi}/configurations/entries/{config_id}',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        else:
            # Perform a POST request to create a new entry if 'configs' list is empty
            validation_response_post = requests.post(
                f'{st.session_state.okapi}/configurations/entries',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

    except requests.exceptions.RequestException as err:
        print("Oops! Something went wrong:", err)

def profile_picture():

    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    body = {
    "module": "USERS",
    "configName": "profile_pictures",
    "enabled": True,
    "value": True
}

    try:
        # GET request to check if the configuration entry exists
        validation_response = requests.get(
            f'{st.session_state.okapi}/configurations/entries?query=(module=USERS and configName=profile_pictures)',
            headers=headers
        )
        validation_response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        configs = validation_response.json().get('configs',
                                                 [])  # Get the 'configs' list or an empty list if it doesn't exist

        if configs:  # Check if the 'configs' list is not empty
            config_id = configs[0]['id']  # Access the first element if it exists

            # Perform a PUT request to update the existing entry
            validation_response_post = requests.put(
                f'{st.session_state.okapi}/configurations/entries/{config_id}',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

        else:
            # Perform a POST request to create a new entry if 'configs' list is empty
            validation_response_post = requests.post(
                f'{st.session_state.okapi}/configurations/entries',
                data=json.dumps(body),
                headers=headers
            )
            validation_response_post.raise_for_status()  # Raise an exception for 4XX or 5XX status codes

    except requests.exceptions.RequestException as err:
        print("Oops! Something went wrong:", err)
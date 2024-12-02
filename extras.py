import aiohttp
import asyncio
import json
import streamlit as st
from legacy_session_state import legacy_session_state
import requests
import logging
legacy_session_state()

if 'Allow_rest' not in st.session_state:
    st.session_state['Allow_rest'] = False


logging.basicConfig(level=logging.DEBUG)

async def async_request(method, url, headers=None, data=None):
    if headers is None:
        headers = {}
    headers['Content-Type'] = 'application/json'

    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, headers=headers, data=data) as response:
            logging.debug(f"URL: {url}")
            logging.debug(f"Method: {method}")
            logging.debug(f"Headers: {headers}")
            logging.debug(f"Data: {data}")
            logging.debug(f"Status: {response.status}")
            if response.status != 200:
                logging.error(f"Response: {await response.text()}")
            response.raise_for_status()
            return await response.json() if method == "GET" else await response.text()


async def configure_tenant():
    Config_url = f"{st.session_state.okapi}/configurations/entries?limit=1000"
    post_url = f"{st.session_state.okapi}/configurations/entries"
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    response = await async_request("GET", Config_url, headers=headers)
    logging.debug(f"Configurations response: {response}")

    reset = {
        "module": "USERSBL",
        "configName": "smtp",
        "code": "FOLIO_HOST",
        "description": "email reset host",
        "default": "true",
        "enabled": "true",
        "value": f"{st.session_state.clienturl}",
    }

    marc = {
        "module": "MARCEDITOR",
        "configName": "default_job_profile_id",
        "enabled": "true",
        "value": "e34d7b92-9b83-11eb-a8b3-0242ac130003"
    }

    tasks = []
    smtp_exists = False
    marc_exists = False

    for config in response["configs"]:
        if config["module"] == "USERSBL" and config["configName"] == "smtp" and config["code"] == "FOLIO_HOST":
            smtp_exists = True
            tasks.append(async_request("PUT", f"{post_url}/{config['id']}", headers=headers, data=json.dumps(reset)))
        elif config["module"] == "MARCEDITOR" and config["configName"] == "default_job_profile_id":
            marc_exists = True
            if config["value"] != "e34d7b92-9b83-11eb-a8b3-0242ac130003":
                st.warning('Please Check Your Job Load Profile Manually!')
            # Update existing marc configuration
            tasks.append(async_request("PUT", f"{post_url}/{config['id']}", headers=headers, data=json.dumps(marc)))

    if not smtp_exists:
        tasks.append(async_request("POST", post_url, headers=headers, data=json.dumps(reset)))

    if not marc_exists:
        tasks.append(async_request("POST", post_url, headers=headers, data=json.dumps(marc)))

    await asyncio.gather(*tasks)

async def price_note():
    item_note_types_url = f"{st.session_state.okapi}/item-note-types"
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

    # Fetch existing item note types
    existing_item_note_types_response = await async_request("GET", item_note_types_url, headers=headers)
    logging.debug(f"Existing item note types response: {existing_item_note_types_response}")

    if isinstance(existing_item_note_types_response, dict) and 'itemNoteTypes' in existing_item_note_types_response:
        existing_item_note_types = {note_type["name"].lower() for note_type in
                                    existing_item_note_types_response['itemNoteTypes']}
    else:
        existing_item_note_types = set()

    item_note_name = "price"
    if item_note_name.lower() not in existing_item_note_types:
        data = {"source": "automation", "name": item_note_name}
        await async_request("POST", item_note_types_url, headers=headers, data=json.dumps(data))
    else:
        logging.info(f"Item note type '{item_note_name}' already exists. Skipping.")


async def loan_type():
    loan_types_url = f"{st.session_state.okapi}/loan-types"
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

    # Fetch existing loan types
    existing_loan_types_response = await async_request("GET", loan_types_url, headers=headers)
    logging.debug(f"Existing loan types response: {existing_loan_types_response}")

    if isinstance(existing_loan_types_response, dict) and 'loantypes' in existing_loan_types_response:
        existing_loan_types = {loan_type["name"].lower() for loan_type in existing_loan_types_response['loantypes']}
    else:
        existing_loan_types = set()

    loan_type_name = "Non circulating"
    if loan_type_name.lower() not in existing_loan_types:
        data = {"name": loan_type_name}
        await async_request("POST", loan_types_url, headers=headers, data=json.dumps(data))
    else:
        logging.info(f"Loan type '{loan_type_name}' already exists. Skipping.")


async def default_job_profile():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    config_url = f"{st.session_state.okapi}/configurations/entries?query=(module==MARCEDITOR and configName==default_job_profile_id)"

    # Fetch existing configuration entries
    response = await async_request("GET", config_url, headers=headers)
    logging.debug(f"Existing default job profile response: {response}")

    default_job = {
        "module": "MARCEDITOR",
        "configName": "default_job_profile_id",
        "enabled": "true",
        "value": "e34d7b92-9b83-11eb-a8b3-0242ac130003"
    }

    if response and 'configs' in response and len(response['configs']) > 0:
        config_id = response['configs'][0]['id']
        logging.debug(f"Updating existing configuration with id: {config_id}")
        update_url = f"{st.session_state.okapi}/configurations/entries/{config_id}"
        await async_request("PUT", update_url, headers=headers, data=json.dumps(default_job))
    else:
        logging.debug("Creating new configuration entry")
        await async_request("POST", f"{st.session_state.okapi}/configurations/entries", headers=headers,
                            data=json.dumps(default_job))
async def alt_types():
    alt_typesurl = f"{st.session_state.okapi}/alternative-title-types"
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    altlist = ['Uniform title', 'Variant title', 'General topology', 'Former title']

    # Fetch existing alternative title types
    existing_types_response = await async_request("GET", alt_typesurl, headers=headers)
    logging.debug(f"Existing types response: {existing_types_response}")

    existing_types = set()
    if isinstance(existing_types_response, dict) and 'alternativeTitleTypes' in existing_types_response:
        for alt_type in existing_types_response['alternativeTitleTypes']:
            logging.debug(f"Alternative title type found: {alt_type}")
            if isinstance(alt_type, dict) and 'name' in alt_type:
                existing_types.add(alt_type["name"].strip().lower())

    logging.debug(f"Existing types set: {existing_types}")

    tasks = []
    for alt in altlist:
        alt_lower = alt.strip().lower()
        if alt_lower not in existing_types:
            data = json.dumps({"name": alt, "source": "Automation"})
            logging.debug(f"Adding new alternative title type: {data}")
            tasks.append(async_request("POST", alt_typesurl, headers=headers, data=data))
        else:
            logging.info(f"Alternative title type '{alt}' already exists. Skipping.")

    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                logging.error(f"Error during task execution: {result}")
async def addDepartments():
    departments_url = f"{st.session_state.okapi}/departments"
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

    # Fetch existing departments
    existing_departments_response = await async_request("GET", departments_url, headers=headers)
    logging.debug(f"Existing departments response: {existing_departments_response}")

    if isinstance(existing_departments_response, dict) and 'departments' in existing_departments_response:
        existing_departments = {dept["name"].lower() for dept in existing_departments_response['departments']}
    else:
        existing_departments = set()

    department_name = "Main"
    if department_name.lower() not in existing_departments:
        data = {"name": department_name, "code": "main"}
        await async_request("POST", departments_url, headers=headers, data=json.dumps(data))
    else:
        logging.info(f"Department '{department_name}' already exists. Skipping.")


async def post_locale(timezone, currency):
    get_config = f"{st.session_state.okapi}/configurations/entries?query=(module==ORG and configName==localeSettings)"
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    response = await async_request("GET", get_config, headers=headers)

    to_do = {
        "module": "ORG",
        "configName": "localeSettings",
        "enabled": True,
        "value": f'{{"locale":"en-US","timezone":"{timezone}","currency":"{currency}"}}'
    }

    if not response['configs']:
        await async_request("POST", f"{st.session_state.okapi}/configurations/entries", headers=headers,
                            data=json.dumps(to_do))
    else:
        config_id = response['configs'][0]['id']
        await async_request("PUT", f"{st.session_state.okapi}/configurations/entries/{config_id}", headers=headers,
                            data=json.dumps(to_do))


async def circ_other():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    value = {
        "audioAlertsEnabled": False,
        "audioTheme": "classic",
        "checkoutTimeout": True,
        "checkoutTimeoutDuration": 3,
        "prefPatronIdentifier": "barcode,username",
        "useCustomFieldsAsIdentifiers": False,
        "wildcardLookupEnabled": False
    }
    body = {
        "module": "CHECKOUT",
        "configName": "other_settings",
        "enabled": True,
        "value": json.dumps(value)}  # Convert the value object to a JSON string

    response = await async_request("GET",
                                   f"{st.session_state.okapi}/configurations/entries?query=(module=CHECKOUT and configName=other_settings)",
                                   headers=headers)
    if response['configs']:
        config_id = response['configs'][0]['id']
        await async_request("PUT", f"{st.session_state.okapi}/configurations/entries/{config_id}", headers=headers,
                            data=json.dumps(body))
    else:
        await async_request("POST", f"{st.session_state.okapi}/configurations/entries", headers=headers,
                            data=json.dumps(body))


async def circ_loanhist():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    body = {
        "module": "LOAN_HISTORY",
        "configName": "loan_history",
        "enabled": True,
        "value": "{\"closingType\":{\"loan\":\"never\",\"feeFine\":null,\"loanExceptions\":[]},\"loan\":{},\"feeFine\":{},\"loanExceptions\":[],\"treatEnabled\":false}"
    }

    response = await async_request("GET",
                                   f"{st.session_state.okapi}/configurations/entries?query=(module=LOAN_HISTORY and configName=loan_history)",
                                   headers=headers)
    if response['configs']:
        config_id = response['configs'][0]['id']
        await async_request("PUT", f"{st.session_state.okapi}/configurations/entries/{config_id}", headers=headers,
                            data=json.dumps(body))
    else:
        await async_request("POST", f"{st.session_state.okapi}/configurations/entries", headers=headers,
                            data=json.dumps(body))


async def export_profile():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    profile_url = f"{st.session_state.okapi}/data-export/mapping-profiles"

    # Fetch existing mapping profiles
    existing_profiles_response = await async_request("GET", profile_url, headers=headers)
    logging.debug(f"Existing profiles response: {existing_profiles_response}")

    existing_profiles = set()
    if isinstance(existing_profiles_response, dict) and 'mappingProfiles' in existing_profiles_response:
        for profile in existing_profiles_response['mappingProfiles']:
            logging.debug(f"Mapping profile found: {profile}")
            if isinstance(profile, dict) and 'name' in profile:
                existing_profiles.add(profile["name"].lower())

    logging.debug(f"Existing profiles set: {existing_profiles}")

    profile_name = "Medad Export"
    if profile_name.lower() not in existing_profiles:
        data = json.dumps({
            "transformations": [
                {"fieldId": "holdings.callnumber", "path": "$.holdings[*].callNumber", "recordType": "HOLDINGS",
                 "transformation": "99900$a", "enabled": True},
                {"fieldId": "holdings.callnumbertype", "path": "$.holdings[*].callNumberTypeId",
                 "recordType": "HOLDINGS", "transformation": "99900$w", "enabled": True},
                {"fieldId": "item.barcode", "path": "$.holdings[*].items[*].barcode", "recordType": "ITEM",
                 "transformation": "99900$i", "enabled": True},
                {"fieldId": "item.copynumber", "path": "$.holdings[*].items[*].copyNumber", "recordType": "ITEM",
                 "transformation": "99900$c", "enabled": True},
                {"fieldId": "item.effectivelocation.name", "path": "$.holdings[*].items[*].effectiveLocationId",
                 "recordType": "ITEM", "transformation": "99900$l", "enabled": True},
                {"fieldId": "item.materialtypeid", "path": "$.holdings[*].items[*].materialTypeId",
                 "recordType": "ITEM", "transformation": "99900$t", "enabled": True},
                {"fieldId": "item.itemnotetypeid.price",
                 "path": "$.holdings[*].items[*].notes[?(@.itemNoteTypeId=='bd68d7f1-2535-48af-bfac-c554cf8204f6' && (!(@.staffOnly) || @.staffOnly == false))].note",
                 "recordType": "ITEM", "transformation": "99900$p", "enabled": True},
                {"fieldId": "item.status", "path": "$.holdings[*].items[*].status.name", "recordType": "ITEM",
                 "transformation": "99900$s", "enabled": True},
                {"fieldId": "item.volume", "path": "$.holdings[*].items[*].volume", "recordType": "ITEM",
                 "transformation": "99900$v", "enabled": True}
            ],
            "recordTypes": ["SRS", "HOLDINGS", "ITEM"],
            "outputFormat": "MARC",
            "name": profile_name
        })
        await async_request("POST", profile_url, headers=headers, data=data)
    else:
        logging.info(f"Mapping profile '{profile_name}' already exists. Skipping.")


async def profile_picture():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    body = {
        "module": "USERS",
        "configName": "profile_pictures",
        "enabled": True,
        "value": True
    }

    response = await async_request("GET",
                                   f"{st.session_state.okapi}/configurations/entries?query=(module=USERS and configName=profile_pictures)",
                                   headers=headers)
    if response['configs']:
        config_id = response['configs'][0]['id']
        await async_request("PUT", f"{st.session_state.okapi}/configurations/entries/{config_id}", headers=headers,
                            data=json.dumps(body))
    else:
        await async_request("POST", f"{st.session_state.okapi}/configurations/entries", headers=headers,
                            data=json.dumps(body))


def get_location_id():
    url = f'{st.session_state.okapi}/locations?limit=3000&query=cql.allRecords%3D1%20sortby%20name'

    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes

    data = response.json()

    # Extract any location ID
    if 'locations' in data and data['locations']:
        return data['locations'][0]['id']  # Return the first location ID
    else:
        return None


def get_material_type_id():
    url = f'{st.session_state.okapi}/material-types?query=cql.allRecords=1%20sortby%20name&limit=2000'

    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes

    data = response.json()

    # Extract any material type ID
    if 'mtypes' in data and data['mtypes']:
        return data['mtypes'][0]['id']  # Return the first material type ID
    else:
        return None


def get_loan_type_id():
    url = f'{st.session_state.okapi}/loan-types?query=cql.allRecords=1%20sortby%20name&limit=2000'

    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes

    data = response.json()

    # Extract any loan type ID
    if 'loantypes' in data and data['loantypes']:
        return data['loantypes'][0]['id']  # Return the first loan type ID
    else:
        return None


def post_record():
    url = f'{st.session_state.okapi}/records-editor/records'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    data = {
        "leader": "00000cam a2200000 a 4500",
        "fields": [
            {"tag": "005", "content": "20240402140414.1", "indicators": [" ", " "]},
            {"tag": "008", "content": {
                "Type": "a", "BLvl": "m", "ELvl": " ", "Desc": "a", "DtSt": "s", "Entered": "240402", "Srce": "d", "MRec": " ",
                "Date2": "    ", "Ctry": "su ", "Lang": "ara", "Date1": "2020", "Biog": "c", "Audn": "d", "Fest": "0",
                "Cont": [" ", " ", " ", " "], "Conf": "0", "Form": " ", "GPub": " ", "Ills": [" ", " ", " ", " "],
                "Indx": "0", "LitF": "0"
            }, "indicators": [" ", " "]},
            {"tag": "100", "content": "$akamautomation", "indicators": [" ", " "]},
            {"tag": "245", "content": "$akamautomation", "indicators": ["1", "0"]}
        ],
        "marcFormat": "BIBLIOGRAPHIC",
        "parsedRecordDtoId": "b47f566c-923d-4de5-b1ff-358cceb7e119",
        "externalId": "bab27c2b-57c9-45e5-9f4f-a30c9275d142",
        "relatedRecordVersion": "null"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print("Record posted successfully.")
    else:
        print(f"Failed to post record: {response.status_code} - {response.text}")


def modify_instance():
    base_url = f'{st.session_state.okapi}/inventory/instances'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}


    # Step 1: GET request to retrieve instance by title
    query = 'query=title==kamautomation'
    get_url = f"{base_url}?{query}"

    get_response = requests.get(get_url, headers=headers)
    print(get_response.content)

    if get_response.status_code != 200:
        print(f"Failed to get instance: {get_response.status_code} - {get_response.text}")
        return

    instance_data = get_response.json()
    if not instance_data['instances']:
        print("No instances found with the specified title.")
        return

    instance = instance_data['instances'][0]
    instance_id = instance['id']


    # Step 2: Modify the discoverySuppress field
    instance['discoverySuppress'] = True

    # Step 3: PUT request to update the instance data
    put_url = f"{base_url}/{instance_id}"
    put_response = requests.put(put_url, headers=headers, json=instance)

    if put_response.status_code == 204:
        print("Instance updated successfully.")
        return instance_id
    else:
        print(f"Failed to update instance: {put_response.status_code} - {put_response.text}")


def post_holdings(instance_id):
    url = f'{st.session_state.okapi}/holdings-storage/holdings'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    location_id = get_location_id()

    data = {
        "instanceId": instance_id,
        "permanentLocationId": str(location_id),
        "discoverySuppress": True
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Holdings posted successfully.")
    else:
        print(f"Failed to post holdings: {response.status_code} - {response.text}")


def get_holdings_id(instance_id):
    url = f'{st.session_state.okapi}/holdings-storage/holdings?limit=1000&query=instanceId%3D%3D{instance_id}'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}


    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        holdings_data = response.json()
        if holdings_data['holdingsRecords']:
            holding_id = holdings_data['holdingsRecords'][0]['id']
            print(f"Holdings ID: {holding_id}")
            return holding_id
        else:
            print("No holdings records found.")
            return None
    else:
        print(f"Failed to get holdings: {response.status_code} - {response.text}")
        return None

def post_inventory_item(holding_id):
    url = f'{st.session_state.okapi}/inventory/items'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    location_id = get_location_id()
    material_type_id = get_material_type_id()
    loan_type_id = get_loan_type_id()

    data = {
        "status": {"name": "Available"},
        "holdingsRecordId": holding_id,
        "permanentLocation": {"id": str(location_id)},
        "temporaryLocation": {},
        "discoverySuppress": True,
        "barcode": "kamautomation",
        "materialType": {"id": str(material_type_id)},
        "permanentLoanType": {"id": str(loan_type_id)}
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Inventory item posted successfully.")
    else:
        print(f"Failed to post inventory item: {response.status_code} - {response.text}")

def post_loan_period():

    url = f'{st.session_state.okapi}/loan-policy-storage/loan-policies?limit=1000&query=cql.allRecords%3D1'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    data = {
        "name": f"{st.session_state.tenant} Loan Policy",
        "loanable": False,
        "renewable": False
    }

    response = requests.post(url, headers=headers, json=data)
    st.write(response)
    st.write(response.status_code)

def post_overdue_fines_policy():
    url = f'{st.session_state.okapi}/overdue-fines-policies?limit=1000&query=cql.allRecords%3D1'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    data = {
        "countClosed": True,
        "forgiveOverdueFine": True,
        "gracePeriodRecall": True,
        "maxOverdueFine": "0.00",
        "maxOverdueRecallFine": "0.00",
        "name": f"{st.session_state.tenant} Loan Policy"
    }

    response = requests.post(url, headers=headers, json=data)
    st.write(response)
    st.write(response.status_code)

def post_lost_item_fees_policy():
    url = f'{st.session_state.okapi}/lost-item-fees-policies?limit=1000&query=cql.allRecords%3D1'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    data = {
        "chargeAmountItem": {
            "amount": "0.00",
            "amountWithoutVat": "0.00",
            "vat": "0.00",
            "chargeType": "anotherCost"
        },
        "lostItemProcessingFee": "0.00",
        "chargeAmountItemPatron": False,
        "chargeAmountItemSystem": False,
        "returnedLostItemProcessingFee": False,
        "replacedLostItemProcessingFee": False,
        "replacementProcessingFee": "0.00",
        "replacementAllowed": False,
        "lostItemReturned": "Charge",
        "name": f"{st.session_state.tenant} Lost Policy",
        "vat": "0",
        "lostItemProcessingFeeWithoutVat": "0.00",
    }

    response = requests.post(url, headers=headers, json=data)
    st.write(response.content)
    st.write(response.status_code)

def post_patron_notice_policy():
    url = f'{st.session_state.okapi}/patron-notice-policy-storage/patron-notice-policies?limit=1000&query=cql.allRecords%3D1'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    data = {
        "name": f"{st.session_state.tenant} Notice Policy"
    }

    response = requests.post(url, headers=headers, json=data)

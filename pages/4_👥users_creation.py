import streamlit as st
import requests
import json
from legacy_session_state import legacy_session_state
import string
import secrets
from permissions import apiperm, fullperms, circ, Acquisition, cataloging, admins, search, sip

legacy_session_state()


hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_menu_style, unsafe_allow_html=True)


def perm():

    perm_sets = [
        {"displayName": "Naseej", "description": "Naseej", "subPermissions": fullperms},
        {"displayName": "UserAPI", "description": "User API", "subPermissions": apiperm},
        {"displayName": "Circulation", "description": "Circulation Permissions", "subPermissions": circ},
        {"displayName": "Cataloging", "description": "Cataloging Permissions", "subPermissions": cataloging},
        {"displayName": "Acquisition", "description": "Acquisition Permissions", "subPermissions": Acquisition},
        {"displayName": "admin", "description": "admin Permissions", "subPermissions": admins},
        {"displayName": "search", "description": "Search Permissions", "subPermissions": search},
        {"displayName": "SIP", "description": "SIP Permissions", "subPermissions": sip}
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
                perm_post = requests.post(f"{st.session_state.okapi}/perms/permissions", headers=headers,
                              data=json.dumps(perm_set))
                # st.write(perm_post.content)
                # st.write(perm_post.status_code)
            except requests.exceptions.RequestException as err:
                st.write(f"Failed to post permission set '{perm_set['displayName']}': {err}")

def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

# if 'btn2' not in st.session_state:
#     st.session_state['btn2'] = False

# if st.session_state['btn2'] is True:


def create_user():
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

    # All API url
    group_url = f"{st.session_state.okapi}/groups"
    users_url = f"{st.session_state.okapi}/users"
    password_url = f"{st.session_state.okapi}/authn/credentials"
    permission_link = f"{st.session_state.okapi}/perms/users?full=true&indexField=userId"
    permissions_url1 = f"{st.session_state.okapi}/perms/permissions?query=(displayName==Naseej)"
    permissions_url2 = f"{st.session_state.okapi}/perms/permissions?query=(displayName==UserAPI)"
    permissions_url3 = f"{st.session_state.okapi}/perms/permissions?query=(displayName==SIP)"

    # Create patron group and get its ID
    data = {
        "group": "Naseej"
    }
    requests.post(group_url, headers=headers, data=json.dumps(data))

    response = requests.get(group_url + r"?query=(group==Naseej)", headers=headers).json()
    group_id = response["usergroups"][0]["id"]

    # Get id of admin permission set
    permission_Admin_res = requests.get(permissions_url1, headers=headers).json()
    admin_id = permission_Admin_res['permissions'][0]["id"]


    # Get id of API_User
    permission_user_res = requests.get(permissions_url2, headers=headers).json()
    APIuser_id = permission_user_res['permissions'][0]["id"]

    # Get id of API_User
    permission_sip_res = requests.get(permissions_url3, headers=headers).json()
    SIPuser_id = permission_sip_res['permissions'][0]["id"]


    for i in range(0, len(options)):
        username = options[i]
        # user data
        user_data = {
            "username": username,
            "patronGroup": group_id,
            "active": True,
            "personal": {
                "lastName": username,
                "email": username,
                "addresses": [],
                "preferredContactTypeId": "002"
            }
        }

        # Post user (create user)
        create_user_res1 = requests.post(users_url, data=json.dumps(user_data), headers=headers)
        # st.write(create_user_res1)

        #if username exists
        if "username already exists" in str(create_user_res1.content):
            st.warning("Username ("+username+") already exists.")
        elif create_user_res1.status_code == 400:
            st.warning("Bad request")
        elif create_user_res1.status_code == 401:
            st.warning("unable to create users -- unauthorized")
        elif create_user_res1.status_code == 422:
            msg = create_user_res1.json()
            msg = msg["errors"]["message"]
            st.warning(msg)
        elif create_user_res1.status_code == 500:
            st.warning("Internal server error, contact administrator.")
        else:
            #if no errors found

            # Get user id
            create_user_res = requests.get(users_url + f"?query=(username =={username})", headers=headers).json()
            user_id = create_user_res["users"][0]["id"]

            random_password = generate_password()
            # create user password
            password_data = {
                "username": username,
                "password": random_password,
                "userId": user_id
            }

            if username.__eq__("kam_admin") or username.__eq__("helpdesk_admin") or username.__eq__("data_migration_user"):
                perm_data = {
                    "userId": user_id,
                    "permissions": [admin_id]
                }
            elif username.__eq__("portal_integration"):
                perm_data = {
                    "userId": user_id,
                    "permissions": []
                }
            elif username.__eq__(f"sip_{st.session_state.tenant}"):
                perm_data = {
                    "userId": user_id,
                    "permissions": [SIPuser_id]
                }
            else:
                perm_data = {
                    "userId": user_id,
                    "permissions": [APIuser_id]
                }
            # Add permissions
            requests.post(permission_link, headers=headers, data=json.dumps(perm_data))

            # Add password to user
            pwdd = requests.post(password_url, headers=headers, data=json.dumps(password_data))
            st.write(pwdd.content)
            st.success(f"User ({username}) have been created! password : {random_password}", icon="✅")

st.title("User Creation")
options = st.multiselect(
    'Please choose users to create',
    ['portal_integration', 'kam_admin', 'helpdesk_admin', 'data_migration_user', 'api_user', f'sip_{st.session_state.tenant}'])

result = st.button("Create users")

if result:
    perm()
    create_user()

# else:
#     st.warning("Please complete basic configuration first.")
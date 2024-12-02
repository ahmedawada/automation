import json
import requests
import streamlit as st
from legacy_session_state import legacy_session_state

legacy_session_state()

if 'allow_tenant' not in st.session_state:
    st.session_state['allow_tenant'] = False
def get_all(endpoint, key, query, okapi_url, okapi_headers):
    url = f"{okapi_url}{endpoint}{query}"
    response = requests.get(url, headers=okapi_headers)
    response.raise_for_status()
    return response.json()[key]


def add_permission_to_user(okapi_url, tenant_id, token, username, permission_name):
    okapi_headers = {
        "X-Okapi-Tenant": tenant_id,
        "X-Okapi-Token": token,
        "Content-Type": "application/json"
    }

    try:
        st.write(f"Adding {permission_name} to {username}")

        # get user uuid
        user_id_query = f'?query=(username=="{username}")'
        users = get_all('/users', "users", user_id_query, okapi_url, okapi_headers)
        if not users:
            st.error(f"No user found with username {username}")
            return
        user_uuid = users[0]["id"]
        st.write(f"User UUID is {user_uuid}")

        # Get permissions user
        query = f'?query=(userId=="{user_uuid}")'
        perms_users = get_all('/perms/users', "permissionUsers", query, okapi_url, okapi_headers)
        if not perms_users:
            st.error(f"No permissions user found with user id {user_uuid}")
            return
        perms_user = perms_users[0]
        st.write(f"Permissions user {perms_user['id']} found with {len(perms_user['permissions'])} permissions")

        # Add the permission and put the user
        perms_user["permissions"].append(permission_name)
        resp = requests.put(
            f"{okapi_url}/perms/users/{perms_user['id']}",
            data=json.dumps(perms_user),
            headers=okapi_headers
        )
        resp.raise_for_status()
        st.success(f"Permission {permission_name} successfully added to user {username}")
        st.write(resp.status_code)
    except ValueError as value_error:
        st.error(value_error)
    except requests.HTTPError as http_error:
        st.error(f"HTTP error occurred: {http_error}")
        st.error(f"Permission Name is Incorrect")


# Streamlit UI
def main():

    okapi_url = st.session_state.okapi
    tenant_id = st.session_state.tenant
    token = st.session_state.token

    username = st.text_input("Username")
    permission_name = st.text_input("Permission Name")

    if st.button("Add Permission"):
        add_permission_to_user(okapi_url, tenant_id, token, username, permission_name)


if __name__ == "__main__":
    st.title("Add Permission to User")
    if st.session_state.allow_tenant:
        main()
    else:
        st.warning("Please Connect to Tenant First.")


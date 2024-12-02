import streamlit as st
import pandas as pd
import requests
import json
# Use legacy_session_state to ensure compatibility
from legacy_session_state import legacy_session_state

if 'allow_tenant' not in st.session_state:
    st.session_state['allow_tenant'] = False

legacy_session_state()

# Set headers for API requests
if st.session_state.allow_tenant:
    headers = {
        "x-okapi-tenant": f"{st.session_state.tenant}",
        "x-okapi-token": f"{st.session_state.token}"
    }
    # Define the API endpoint
    users_endpoint = f"{st.session_state.okapi}/users"  # Adjust the base URL if needed

st.markdown("""**This App is used to load users to Medad ILS.**

It is important to note that:
- The app will first try to find a match based on the username.
- If a match is found, it will update the existing user.
- Otherwise, it will add the new user to Medad ILS.
- Custom Labels are still not implemented.
- Make sure to use UUID values in columns like Patron Groups, Service Points ..etc
""", unsafe_allow_html=True)

# Define the predefined column names
predefined_columns = [
    "username",
    "id",
    "externalSystemId",
    "barcode",
    "active",
    "patronGroup",
    "departments",
    "proxyFor",
    "personal.lastName",
    "personal.firstName",
    "personal.middleName",
    "personal.preferredFirstName",
    "personal.email",
    "personal.phone",
    "personal.mobilePhone",
    "personal.dateOfBirth",
    "personal.addresses.countryId",
    "personal.addresses.addressLine1",
    "personal.addresses.addressLine2",
    "personal.addresses.city",
    "personal.addresses.region",
    "personal.addresses.postalCode",
    "personal.addresses.addressTypeId",
    "personal.addresses.primaryAddress",
    "personal.preferredContactTypeId",
    "enrollmentDate",
    "expirationDate",
    "createdDate",
    "updatedDate",
    "metadata.createdDate",
    "metadata.createdByUserId",
    "metadata.updatedDate",
    "metadata.updatedByUserId",
    "libraryId",
    "scopes"
]



def empty_permissions(user_id):
    perm_data = {
        "userId": user_id,
        "permissions": []
    }
    perm = requests.post(f"{st.session_state.okapi}/perms/users?full=true&indexField=userId", data=json.dumps(perm_data), headers=headers)
    # st.write(perm.content)

def user_exists(username):
    response = requests.get(f"{users_endpoint}?query=username=={username}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "users" in data and len(data["users"]) > 0:
            return True, data["users"][0]  # Return the first user found
    return False, None

def post_user_to_api(user_data):
    response = requests.post(users_endpoint, json=user_data, headers=headers)
    # st.write(response.content)
    return response

def put_user_to_api(user_data, user_id):
    response = requests.put(f"{users_endpoint}/{user_id}", json=user_data, headers=headers)
    return response

def format_timestamp(ts):
    if pd.notna(ts):
        return ts.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return None

def build_user_json(row, user_id=None):
    user_json = {}
    if user_id:
        user_json["id"] = user_id

    if pd.notna(row.get("username")):
        user_json["username"] = row.get("username")
    if pd.notna(row.get("id")):
        user_json["id"] = row.get("id")
    if pd.notna(row.get("externalSystemId")):
        user_json["externalSystemId"] = row.get("externalSystemId")
    if pd.notna(row.get("barcode")):
        user_json["barcode"] = row.get("barcode")
    if pd.notna(row.get("active")):
        user_json["active"] = row.get("active")
    if pd.notna(row.get("patronGroup")):
        user_json["patronGroup"] = row.get("patronGroup")
    if isinstance(row.get("departments"), str):
        user_json["departments"] = row.get("departments").split(",")
    if isinstance(row.get("proxyFor"), str):
        user_json["proxyFor"] = row.get("proxyFor").split(",")

    personal = {}
    if pd.notna(row.get("personal.lastName")):
        personal["lastName"] = row.get("personal.lastName")
    if pd.notna(row.get("personal.firstName")):
        personal["firstName"] = row.get("personal.firstName")
    if pd.notna(row.get("personal.middleName")):
        personal["middleName"] = row.get("personal.middleName")
    if pd.notna(row.get("personal.preferredFirstName")):
        personal["preferredFirstName"] = row.get("personal.preferredFirstName")
    if pd.notna(row.get("personal.email")):
        personal["email"] = row.get("personal.email")
    if pd.notna(row.get("personal.phone")):
        personal["phone"] = row.get("personal.phone")
    if pd.notna(row.get("personal.mobilePhone")):
        personal["mobilePhone"] = row.get("personal.mobilePhone")
    if pd.notna(row.get("personal.dateOfBirth")):
        personal["dateOfBirth"] = format_timestamp(row.get("personal.dateOfBirth"))

    personal["preferredContactTypeId"] = "002"

    addresses = []
    address = {}
    if pd.notna(row.get("personal.addresses.countryId")):
        address["countryId"] = row.get("personal.addresses.countryId")
    if pd.notna(row.get("personal.addresses.addressLine1")):
        address["addressLine1"] = row.get("personal.addresses.addressLine1")
    if pd.notna(row.get("personal.addresses.addressLine2")):
        address["addressLine2"] = row.get("personal.addresses.addressLine2")
    if pd.notna(row.get("personal.addresses.city")):
        address["city"] = row.get("personal.addresses.city")
    if pd.notna(row.get("personal.addresses.region")):
        address["region"] = row.get("personal.addresses.region")
    if pd.notna(row.get("personal.addresses.postalCode")):
        address["postalCode"] = row.get("personal.addresses.postalCode")
    if pd.notna(row.get("personal.addresses.addressTypeId")):
        address["addressTypeId"] = row.get("personal.addresses.addressTypeId")
    if pd.notna(row.get("personal.addresses.primaryAddress")):
        address["primaryAddress"] = row.get("personal.addresses.primaryAddress")

    if address:
        addresses.append(address)

    if addresses:
        personal["addresses"] = addresses

    if personal:
        user_json["personal"] = personal

    if pd.notna(row.get("enrollmentDate")):
        user_json["enrollmentDate"] = format_timestamp(row.get("enrollmentDate"))
    if pd.notna(row.get("expirationDate")):
        user_json["expirationDate"] = format_timestamp(row.get("expirationDate"))
    if pd.notna(row.get("createdDate")):
        user_json["createdDate"] = format_timestamp(row.get("createdDate"))
    if pd.notna(row.get("updatedDate")):
        user_json["updatedDate"] = format_timestamp(row.get("updatedDate"))

    metadata = {}
    if pd.notna(row.get("metadata.createdDate")):
        metadata["createdDate"] = format_timestamp(row.get("metadata.createdDate"))
    if pd.notna(row.get("metadata.createdByUserId")):
        metadata["createdByUserId"] = row.get("metadata.createdByUserId")
    if pd.notna(row.get("metadata.updatedDate")):
        metadata["updatedDate"] = format_timestamp(row.get("metadata.updatedDate"))
    if pd.notna(row.get("metadata.updatedByUserId")):
        metadata["updatedByUserId"] = row.get("metadata.updatedByUserId")

    if metadata:
        user_json["metadata"] = metadata

    customFields = {}
    if pd.notna(row.get("customFields.test")):
        customFields["test"] = row.get("customFields.test")
    if pd.notna(row.get("customFields.blocked")):
        customFields["blocked"] = row.get("customFields.blocked")
    if pd.notna(row.get("customFields.oldusername")):
        customFields["oldusername"] = row.get("customFields.oldusername")

    if customFields:
        user_json["customFields"] = customFields

    if pd.notna(row.get("libraryId")):
        user_json["libraryId"] = row.get("libraryId")
    if isinstance(row.get("scopes"), str):
        user_json["scopes"] = row.get("scopes").split(",")
    else:
        user_json["scopes"] = []

    return user_json

def post_users_batch(users_batch):
    response = requests.post(users_endpoint, json=users_batch, headers=headers)
    return response

def put_users_batch(users_batch):
    response = requests.put(users_endpoint, json=users_batch, headers=headers)
    return response

def main():
    st.title("CSV Column Mapper and User Poster")

    # File uploader
    uploaded_file = st.file_uploader("Upload your CSV file", type=["xlsx"])

    if uploaded_file is not None:
        # Read the CSV file
        df = pd.read_excel(uploaded_file)

        st.write("Original Columns:")
        st.write(df.columns)

        # Create a list to hold the new column names
        new_column_names = []

        st.subheader("Map CSV Columns to Predefined Columns")

        # Allow duplicate selection for column mappings
        for col in df.columns:
            options = ["None"] + predefined_columns
            #st.write(f"Options for {col}: {options}")  # Debug statement
            new_col_name = st.selectbox(f"Rename '{col}' to:", options, key=f"selectbox_{col}")
            if new_col_name != "None":
                new_column_names.append(new_col_name)
            else:
                new_column_names.append(None)  # Add None to indicate that the column should be skipped

        # Apply the new column names to the DataFrame
        df.columns = new_column_names

        # Remove columns set to None
        df = df.drop(columns=[col for col in df.columns if col is None])

        st.write("Mapped Columns:")
        st.write(df.columns)

        st.write("Data Preview:")
        st.write(df.head())

        # Option to download the modified CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Mapped CSV", data=csv, file_name="mapped_columns.csv", mime='text/csv')

        # DataFrame to hold failed users with an additional column for the error message
        failed_users_df = pd.DataFrame(columns=df.columns.tolist() + ["Error"])

        # Post each user to the API
        st.subheader("Post Users to API")
        batch_size = st.number_input("Batch Size", min_value=1, value=10)
        if st.button("Post Users"):
            progress_bar = st.progress(0)
            with st.spinner("Posting users..."):
                success_count = 0
                failure_count = 0
                for idx in range(0, len(df), batch_size):
                    batch_df = df.iloc[idx:idx + batch_size]
                    users_batch = [build_user_json(row) for _, row in batch_df.iterrows()]

                    response = post_users_batch(users_batch)

                    if response.status_code in [204, 201]:
                        success_count += len(users_batch)
                    else:
                        failure_count += len(users_batch)
                        for row in batch_df.itertuples(index=False):
                            row_with_error = pd.Series(row._asdict())
                            row_with_error["Error"] = response.content.decode('utf-8')
                            failed_users_df = pd.concat([failed_users_df, pd.DataFrame([row_with_error])], ignore_index=True)

                    # Update the progress bar
                    progress_bar.progress((idx + batch_size) / len(df))

                st.success(f"Successfully posted/Updated {success_count} users.")
                st.error(f"Failed to post {failure_count} users.")

        # Provide download button for failed users CSV
        if not failed_users_df.empty:
            st.subheader("Download Failed Users")
            failed_csv = failed_users_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Failed Users CSV", data=failed_csv, file_name="failed_users.csv", mime='text/csv')

if __name__ == "__main__":
    if st.session_state.allow_tenant:
        main()
    else:
        st.warning("Please Connect to Tenant First.")

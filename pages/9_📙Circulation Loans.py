import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from streamlit_extras.word_importances import format_word_importances
# Use legacy_session_state to ensure compatibility
from legacy_session_state import legacy_session_state

legacy_session_state()

# Set headers for API requests
headers = {
    "x-okapi-tenant": f"{st.session_state.tenant}",
    "x-okapi-token": f"{st.session_state.token}"
}

# Define the predefined column names
predefined_columns = [
    "BARCODE",
    "P_BARCODE",
    "LOAN_DATE",
    "DUE_DATE",
    "SERVICE_POINT_ID"  # Add this to allow mapping of service point ID
]

# Define the API endpoints
base_url = st.session_state.okapi
check_out_endpoint = '/circulation/check-out-by-barcode'
item_endpoint = '/item-storage/items?query="barcode"=="{}"'
user_endpoint = '/users?query="username"=="{}"'
loans_endpoint = '/circulation/loans'




st.markdown("""**This App is used to load current circulation transactions to Medad ILS**

The Excel file should contain **5 Columns**:
- **User Barcode**
- **Item Barcode**
- **Loan Date**
- **Due Date**
- **Service Point UUID**

**Please make sure that the date format should be `dd-mm-yyyy`.**

**Additional Recommendations:**
- It is better to make a circulation rule that accepts all items from all locations when importing loans for the first time.
- Don't forget to turn off automatic notices.

""",unsafe_allow_html=True)

def main():
    st.title("User Loans Import")

    # File uploader
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file is not None:
        # Read the Excel file
        df = pd.read_excel(uploaded_file, dtype='str')

        st.write("Original Columns:")
        st.write(df.columns)

        # Create a list to hold the new column names
        new_column_names = []

        st.subheader("Map CSV Columns to Predefined Columns")

        # Allow duplicate selection for column mappings
        for col in df.columns:
            options = ["None"] + predefined_columns
            st.write(f"Options for {col}: {options}")  # Debug statement
            new_col_name = st.selectbox(f"Rename '{col}' to:", options, key=f"selectbox_{col}")
            if new_col_name != "None":
                new_column_names.append(new_col_name)
            else:
                new_column_names.append(None)  # Add None to indicate that the column should be skipped

        # Apply the new column names to the DataFrame
        df.columns = new_column_names

        # Attempt to convert LOAN_DATE and DUE_DATE with multiple formats
        # Attempt to convert LOAN_DATE and DUE_DATE with multiple formats
        df['LOAN_DATE'] = pd.to_datetime(df['LOAN_DATE'])
        df['DUE_DATE'] = pd.to_datetime(df['DUE_DATE'])

        df['LOAN_DATE'] = df['LOAN_DATE'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        df['DUE_DATE'] = df['DUE_DATE'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Remove columns set to None
        df = df.drop(columns=[col for col in df.columns if col is None])

        st.write("Mapped Columns:")
        st.write(df.columns)

        # Check if all required columns are present
        missing_columns = [col for col in predefined_columns if col not in df.columns]
        if missing_columns:
            st.error(f"The following required columns are missing: {', '.join(missing_columns)}")
            return

        st.write("Data Preview:")
        st.write(df.head())



        # DataFrame to hold failed loans with an additional column for the error message
        failed_loans_df = pd.DataFrame(columns=df.columns.tolist() + ["Error"])

        # Log file content
        log_content = []

        # Post each loan to the API
        st.subheader("Post Loans to API")
        if st.button("Post Loans"):
            progress_bar = st.progress(0)
            with st.spinner("Posting loans..."):
                success_count = 0
                failure_count = 0
                for idx, row in df.iterrows():
                    # Fetch item by barcode
                    item_res = requests.get(base_url + item_endpoint.format(row["BARCODE"]), headers=headers).json()
                    if item_res['items']:
                        item_id = item_res['items'][0]['id']

                        # Fetch user by username (P_BARCODE)
                        user_res = requests.get(base_url + user_endpoint.format(row["P_BARCODE"]),
                                                headers=headers).json()
                        if user_res['users']:
                            user_id = user_res['users'][0]['id']

                            # Prepare loan data
                            data = {
                                "userId": user_id,
                                "itemId": item_id,
                                "dueDate": row['DUE_DATE'],
                                "loanDate": row['LOAN_DATE'],
                                "checkoutServicePointId": row['SERVICE_POINT_ID'],  # Use the mapped service point ID
                                "action": "checkedout"
                            }

                            # Post loan data
                            loans_res = requests.post(base_url + loans_endpoint, headers=headers, data=json.dumps(data))
                            if loans_res.status_code == 201:
                                success_count += 1
                                log_content.append(f'{row["BARCODE"]} Success\n')
                            else:
                                failure_count += 1
                                row_with_error = row.copy()
                                row_with_error["Error"] = loans_res.content.decode('utf-8')
                                failed_loans_df = pd.concat([failed_loans_df, pd.DataFrame([row_with_error])],
                                                            ignore_index=True)
                                log_content.append(f"{row['BARCODE']} Failed\n{loans_res.content.decode('utf-8')}\n")
                        else:
                            failure_count += 1
                            row_with_error = row.copy()
                            row_with_error["Error"] = "User not found"
                            failed_loans_df = pd.concat([failed_loans_df, pd.DataFrame([row_with_error])],
                                                        ignore_index=True)
                            log_content.append(f'User {row["P_BARCODE"]} not found.\n')
                    else:
                        failure_count += 1
                        row_with_error = row.copy()
                        row_with_error["Error"] = "Item not found"
                        failed_loans_df = pd.concat([failed_loans_df, pd.DataFrame([row_with_error])],
                                                    ignore_index=True)
                        log_content.append(f'Item {row["BARCODE"]} not found.\n')

                    # Update the progress bar
                    progress_bar.progress((idx + 1) / len(df))

                st.success(f"Successfully posted {success_count} loans.")
                st.error(f"Failed to post {failure_count} loans.")

        # Display log content
        st.subheader("Log")
        log_string = "".join(log_content)
        st.text_area("Log output", log_string, height=300)

        # Provide download button for the log file
        log_bytes = log_string.encode('utf-8')
        st.download_button(label="Download Log", data=log_bytes, file_name="loan_import_log.txt", mime='text/plain')

        # Provide download button for failed loans CSV
        if not failed_loans_df.empty:
            st.subheader("Download Failed Loans")
            failed_csv = failed_loans_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Failed Loans CSV", data=failed_csv, file_name="failed_loans.csv",
                               mime='text/csv')


if __name__ == "__main__":
    main()

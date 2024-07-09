import streamlit as st
import pandas as pd
import requests
import json
from uuid import uuid4

# Use legacy_session_state to ensure compatibility
from legacy_session_state import legacy_session_state

legacy_session_state()

# Define API endpoint and headers
api_url = "https://okapi.medad.com/accounts"
headers = {
    "X-Okapi-Tenant": st.session_state.tenant,
    "x-okapi-token": st.session_state.token,
    "Content-Type": "application/json"
}


st.markdown("""**This App is used to load bills to Medad ILS**

The Excel file should contain the following columns:
- **Amount**
- **FeeFineType** (This should be a name as added in Medad)
- **User UUID**
- **Fine UUID**
- **Owner UUID**
""",unsafe_allow_html=True)

def post_fine(data):
    response = requests.post(api_url, data=json.dumps(data), headers=headers)
    return response


def main():
    st.title("Fines Import")

    # File uploader
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file is not None:
        # Read the Excel file
        df = pd.read_excel(uploaded_file, dtype='str')

        st.write("Original Data:")
        st.write(df.head())

        # Create a list to hold the new column names
        predefined_columns = ["Amount", "UserUUID", "FeeFineID", "OwnerUUID", "FeeFineType"]

        new_column_names = []

        st.subheader("Map CSV Columns to Predefined Columns")

        # Allow duplicate selection for column mappings
        for col in df.columns:
            options = ["None"] + predefined_columns
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

        # DataFrame to hold failed fines with an additional column for the error message
        failed_fines_df = pd.DataFrame(columns=df.columns.tolist() + ["Error"])

        # Log file content
        log_content = []

        # Post each fine to the API
        st.subheader("Post Fines to API")
        if st.button("Post Fines"):
            progress_bar = st.progress(0)
            with st.spinner("Posting fines..."):
                success_count = 0
                failure_count = 0
                for idx, row in df.iterrows():
                    data = {
                        "amount": row['Amount'],
                        "remaining": row['Amount'],
                        "amountWithoutVat": row['Amount'],
                        "status": {"name": "Open"},
                        "paymentStatus": {"name": "Outstanding"},
                        "feeFineType": row['FeeFineType'],
                        "feeFineOwner": "Library",
                        "userId": row['UserUUID'],
                        "feeFineId": row['FeeFineID'],
                        "ownerId": row['OwnerUUID'],
                        "id": str(uuid4())
                    }

                    response = post_fine(data)
                    if response.status_code == 201:
                        success_count += 1
                        log_content.append(f'Row {idx + 1}: Fine posted successfully.\n')
                    else:
                        failure_count += 1
                        row_with_error = row.copy()
                        row_with_error["Error"] = response.content.decode('utf-8')
                        failed_fines_df = pd.concat([failed_fines_df, pd.DataFrame([row_with_error])],
                                                    ignore_index=True)
                        log_content.append(f'Row {idx + 1}: Failed to post fine.\n{response.content.decode("utf-8")}\n')

                    # Update the progress bar
                    progress_bar.progress((idx + 1) / len(df))

                st.success(f"Successfully posted {success_count} fines.")
                st.error(f"Failed to post {failure_count} fines.")

        # Display log content
        st.subheader("Log")
        log_string = "".join(log_content)
        st.text_area("Log output", log_string, height=300)

        # Provide download button for the log file
        log_bytes = log_string.encode('utf-8')
        st.download_button(label="Download Log", data=log_bytes, file_name="fines_import_log.txt", mime='text/plain')

        # Provide download button for failed fines CSV
        if not failed_fines_df.empty:
            st.subheader("Download Failed Fines")
            failed_csv = failed_fines_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Failed Fines CSV", data=failed_csv, file_name="failed_fines.csv",
                               mime='text/csv')


if __name__ == "__main__":
    main()

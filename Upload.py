import streamlit as st
import pandas as pd
import openpyxl
from legacy_session_state import legacy_session_state
legacy_session_state()

file = ""
if 'key' not in st.session_state:
    st.session_state['key'] = True


def upload_file():
    file = st.file_uploader("Please choose a file", type=['xlsx'])

    if st.session_state.get('profiling') !=True:
        st.session_state.profiling = file

    if st.session_state.profiling is not None:
        st.session_state['key'] = True

        # check if file contains required sheets
        xl = pd.ExcelFile(st.session_state.profiling)
        file_length = len(xl.sheet_names)

        # check sheet names
        test = openpyxl.load_workbook(file)
        sheets = test.sheetnames
        test_names = ["Material_Types", "Statistical_Codes", "Item_status", "User_groups", "Location", "Calendar", "Calendar Exceptions", "Department"]
        match_state = []
        j = 0
        if file_length == len(test_names):
            for i in test_names:
                if i.__eq__(sheets[j]):
                    match_state.append("True")
                else:
                    match_state.append("False")

                j = j + 1

            if "False" in match_state:
                st.warning("File not accepted. File must contain the following sheet names: " + str(test_names))
                st.session_state['key'] = False
            else:
                st.success("Uploaded!", icon="✅")

        elif file_length != len(test_names):
            st.warning(f"File not accepted. Excel file must have {len(test_names)} sheets.")
            st.session_state['key'] = False



    else:
        st.warning("Please upload a file")


def upload(type):
    if st.session_state.profiling is not None and st.session_state['key'] is True:
        xls = pd.ExcelFile(st.session_state.profiling)
        if type is not None:
            df = pd.read_excel(xls, type)
            return df

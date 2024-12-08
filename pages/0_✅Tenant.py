import streamlit as st
import json
import requests
from clone_functions import moveSettings, movelocations, movecircpolicies, movecircrules
from Tenant_Backup import backup

st.set_page_config(
    page_title="KAM TEAM", layout="wide", initial_sidebar_state="expanded"
)

if 'allow_tenant' not in st.session_state:
    st.session_state['allow_tenant'] = False

if 'clone' not in st.session_state:
    st.session_state['clone'] = False

if 'new_tenant' not in st.session_state:
    st.session_state['new_tenant'] = False

if 'download' not in st.session_state:
    st.session_state['download'] = False

if 'backup_ten' not in st.session_state:
    st.session_state['backup_ten'] = False

if 'allow_tenant_1' not in st.session_state:
    st.session_state['allow_tenant_1'] = False


if 'allow_tenant_2' not in st.session_state:
    st.session_state['allow_tenant_2'] = False


def tenantlogin(okapi, tenant, username, password):
    myobj = {"username": username, "password": password}
    data = json.dumps(myobj)
    header = {"x-okapi-tenant": tenant}

    x = requests.post(okapi + "/authn/login", data=data, headers=header)
    # st.write(x.content)
    if "x-okapi-token" in x.headers:
        token = x.headers["x-okapi-token"]
        st.success("Connected!", icon="✅")
        st.session_state.allow_tenant = True
        return token

    else:
        st.error("Please check the Tenant information", icon="🚨")


def reset():
    st.session_state.tenant_1 = ""
    st.session_state.username_1 = ""
    st.session_state.password_1 = ""


# CONFIGURE NEW TENANT
if st.session_state.new_tenant:

    st.subheader("Tenant Connection")
    st.caption('This Section is used to connect to the tenant in order to start the Automation Process')

    with st.form("myform"):
        st.text_input("Enter Tenant Username:", key="username_tenant", placeholder="Please enter your username")

        st.text_input("Enter Tenant Password:", key="password", placeholder="Please enter your password",
                      type='password')

        st.text_input("Enter Tenant Name:", placeholder="Please enter tenant name", key="tenant")

        options = st.selectbox(
            "Select Okapi URL:",
            ("https://okapi-cls01.ils.medad.com","https://okapi-cls02.ils.medad.com","https://okapi.medad.com", "https://okapi-uae.ils.medad.com", "https://okapi.medadstg.com","https://okapi-uae-cls01.ils.medad.com","https://okapi-uae-cls02.ils.medad.com"),
            key="okapi",
        )

        col1, col2 = st.columns(2)
        st.markdown(
            """<style>
      
                div.row-widget.stButton > button.css-1pr530z.edgvbvh5{
                
                margin-left:200px;
                
                }
                
                
                
                span.css-10trblm.e16nr0p30{
                text-align: center;
                }
                </style>""",
            unsafe_allow_html=True,
        )

        hide_menu_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
        st.markdown(hide_menu_style, unsafe_allow_html=True)

        with col1:
            submitted_2 = st.form_submit_button("Connect")
            if submitted_2:
                token = tenantlogin(
                    st.session_state.okapi,
                    st.session_state.tenant,
                    st.session_state.username_tenant,
                    st.session_state.password
                )
                if ('token' in st.session_state) or ('token' not in st.session_state):
                    st.session_state.token = token
        with col2:
            reset = st.form_submit_button("reset", on_click=reset)
            if reset:
                st.session_state.allow_tenant = False
                st.success("Cleared!", icon="✅")

# CLONE TENANT
elif st.session_state.clone:

    # Filters
    st.sidebar.write("ILS Settings Selections:")
    patron_groups = st.sidebar.checkbox("Move Patron Groups")
    Service_Points = st.sidebar.checkbox("Move Service Points")
    due_dates = st.sidebar.checkbox("Move Fixed Due Dates")
    Location_tree = st.sidebar.checkbox("Move Location Hierarchy")
    loan_types = st.sidebar.checkbox("Move Loan Types")
    loan_policy = st.sidebar.checkbox("Move Loan/Request Policy")
    over_policy = st.sidebar.checkbox("Move Overdue/Lost Policy")
    Notices = st.sidebar.checkbox("Move Notice Templates")
    staff_slips = st.sidebar.checkbox("Move Staff Slips")
    Circ_rules = st.sidebar.checkbox("Move Circulation Rules")

    dev1, dev2 = st.columns(2)

    with dev1:
        st.subheader("Master Tenant")
        st.caption('This is the Master Tenant where all the settings will be transferred to the Clone Tenant ')

        with st.form("Master"):
            st.text_input("Enter Tenant Username:", key="username_tenant_1", placeholder="Please enter your username")

            st.text_input("Enter Tenant Password:", key="password_1", placeholder="Please enter your password",
                          type='password')

            st.text_input("Enter Tenant Name:", placeholder="Please enter tenant name", key="tenant_1")

            options = st.selectbox(
                "Select Okapi URL:",
                ("https://okapi.medad.com", "https://okapi-g42.medad.com", "https://okapi-qa.medadstg.com",
                 "https://okapi-uae.ils.medad.com","https://darah-okapi.mynaseej.net"),
                key="okapi_1",
            )

            # col1, col2 = st.columns(2)
            st.markdown(
                """<style>
    
                    div.row-widget.stButton > button.css-1pr530z.edgvbvh5{
    
                    margin-left:200px;
    
                    }
    
    
    
                    span.css-10trblm.e16nr0p30{
                    text-align: center;
                    }
                    </style>""",
                unsafe_allow_html=True,
            )

            hide_menu_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
            st.markdown(hide_menu_style, unsafe_allow_html=True)

            submitted_3 = st.form_submit_button("Connect")
            if submitted_3:
                token = tenantlogin(
                    st.session_state.okapi_1,
                    st.session_state.tenant_1,
                    st.session_state.username_tenant_1,
                    st.session_state.password_1,
                )
                if ('token_1' in st.session_state) or ('token_1' not in st.session_state):
                    st.session_state.token_1 = token

            # with col1:
            #     submitted_3 = st.form_submit_button("Connect")
            #     if submitted_3:
            #         token = tenantlogin(
            #             st.session_state.okapi_1,
            #             st.session_state.tenant_1,
            #             st.session_state.username_tenant_1,
            #             st.session_state.password_1,
            #         )
            #         if ('token_1' in st.session_state) or ('token_1' not in st.session_state):
            #             st.session_state.token_1 = token
            # with col2:
            #     reset = st.form_submit_button("reset", on_click=reset)
            #     if reset:
            #         st.session_state.allow_tenant_1 = False
            #         st.success("Cleared!", icon="✅")

    with dev2:
        st.subheader("Clone Tenant")
        st.caption('This is the Cloned tenant where all the settings will be implemented')

        with st.form("cloned"):
            st.text_input("Enter Tenant Username:", key="username_tenant_2", placeholder="Please enter your username")

            st.text_input("Enter Tenant Password:", key="password_2", placeholder="Please enter your password",
                          type='password')

            st.text_input("Enter Tenant Name:", placeholder="Please enter tenant name", key="tenant_2")

            options = st.selectbox(
                "Select Okapi URL:",
                ("https://okapi.medad.com", "https://okapi-g42.medad.com", "https://okapi-qa.medadstg.com",
                 "https://okapi-uae.ils.medad.com", "https://darah-okapi.mynaseej.net","http://10.0.8.243/okapi","https://darah-ils.mynaseej.net/okapi"),
                key="okapi_2",
            )

            # col1, col2 = st.columns(2)
            st.markdown(
                """<style>

                    div.row-widget.stButton > button.css-1pr530z.edgvbvh5{

                    margin-left:200px;

                    }



                    span.css-10trblm.e16nr0p30{
                    text-align: center;
                    }
                    </style>""",
                unsafe_allow_html=True,
            )

            hide_menu_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
            st.markdown(hide_menu_style, unsafe_allow_html=True)
            submitted_1 = st.form_submit_button("Connect")
            if submitted_1:
                token = tenantlogin(
                    st.session_state.okapi_2,
                    st.session_state.tenant_2,
                    st.session_state.username_tenant_2,
                    st.session_state.password_2,
                )
                if ('token_2' in st.session_state) or ('token_2' not in st.session_state):
                    st.session_state.token_2 = token

    proceed = st.button("Clone it")

    if proceed:
        fetchHeaders = {
            'x-okapi-tenant': st.session_state.tenant_1,
            'x-okapi-token': st.session_state.token_1
        }
        postHeaders = {
            'x-okapi-tenant': st.session_state.tenant_2,
            'x-okapi-token': st.session_state.token_2,
            'Content-Type': 'application/json'
        }
        if patron_groups:
            moveSettings("/groups?limit=1000", "/groups/", "usergroups", st.session_state.okapi_1, st.session_state.okapi_2, fetchHeaders, postHeaders)

        if Service_Points:
            moveSettings("/service-points?limit=100", "/service-points/", "servicepoints", st.session_state.okapi_1, st.session_state.okapi_2,fetchHeaders, postHeaders)

        if due_dates:
            moveSettings("/fixed-due-date-schedule-storage/fixed-due-date-schedules?limit=1000",
                         "/fixed-due-date-schedule-storage/fixed-due-date-schedules/", "fixedDueDateSchedules", st.session_state.okapi_1,
                         st.session_state.okapi_2, fetchHeaders, postHeaders)

        if Location_tree:
            movelocations(st.session_state.okapi_1, st.session_state.okapi_2, fetchHeaders, postHeaders)

        if loan_types:
            moveSettings("/loan-types?limit=500", "/loan-types/", "loantypes", st.session_state.okapi_1, st.session_state.okapi_2, fetchHeaders,
                         postHeaders)

        if loan_policy:
            movecircpolicies("/loan-policy-storage/loan-policies?limit=100", "/loan-policy-storage/loan-policies/",
                                "loanPolicies", st.session_state.okapi_1, st.session_state.okapi_2, fetchHeaders, postHeaders)
            movecircpolicies("/fixed-due-date-schedule-storage/fixed-due-date-schedules?limit=100",
                                "/fixed-due-date-schedule-storage/fixed-due-date-schedules/", "fixedDueDateSchedules",
                                st.session_state.okapi_1, st.session_state.okapi_2, fetchHeaders, postHeaders)
            movecircpolicies("/request-policy-storage/request-policies?limit=100",
                                "/request-policy-storage/request-policies/", "requestPolicies", st.session_state.okapi_1, st.session_state.okapi_2,
                                fetchHeaders, postHeaders)

        if over_policy:
            movecircpolicies("/overdue-fines-policies?limit=100", "/overdue-fines-policies/", "overdueFinePolicies",
                                st.session_state.okapi_1, st.session_state.okapi_2, fetchHeaders, postHeaders)
            movecircpolicies("/lost-item-fees-policies?limit=100", "/lost-item-fees-policies/",
                                "lostItemFeePolicies", st.session_state.okapi_1, st.session_state.okapi_2, fetchHeaders, postHeaders)

        if Notices:
            movecircpolicies("/templates?query=active==true&limit=100", "/templates/", "templates",   st.session_state.okapi_1,   st.session_state.okapi_2,
                                fetchHeaders, postHeaders)
            movecircpolicies("/patron-notice-policy-storage/patron-notice-policies?limit=100",
                                "/patron-notice-policy-storage/patron-notice-policies/", "patronNoticePolicies",   st.session_state.okapi_1,
                             st.session_state.okapi_2, fetchHeaders, postHeaders)

        if staff_slips:
            movecircpolicies("/staff-slips-storage/staff-slips", "/staff-slips-storage/staff-slips/", "staffSlips",
                                st.session_state.okapi_1, st.session_state.okapi_2, fetchHeaders, postHeaders)

        if Circ_rules:
            movecircrules("/circulation/rules", "rulesAsText", st.session_state.okapi_1, st.session_state.okapi_2, fetchHeaders, postHeaders)

elif st.session_state.backup_ten:
    st.subheader("Tenant Backup")

    st.caption('This Section is used to connect to the tenant in order to start the Backup Process')

    with st.form("backup_form"):
        st.text_input("Enter Tenant Username:", key="username_tenant_3", placeholder="Please enter your username")

        st.text_input("Enter Tenant Password:", key="password_3", placeholder="Please enter your password",
                      type='password')

        st.text_input("Enter Tenant Name:", placeholder="Please enter tenant name", key="tenant_3")

        options = st.selectbox(
            "Select Okapi URL:",
            ("https://okapi.medad.com", "https://okapi-g42.medad.com", "https://okapi-qa.medadstg.com",
             "https://okapi-uae.ils.medad.com", "https://darah-okapi.mynaseej.net"),
            key="okapi_3",
        )
        submitted_backup = st.form_submit_button("Connect")
        if submitted_backup:
            st.session_state['download'] = True
            token = tenantlogin(
                st.session_state.okapi_3,
                st.session_state.tenant_3,
                st.session_state.username_tenant_3,
                st.session_state.password_3,
            )
            if ('token_3' in st.session_state) or ('token_3' not in st.session_state):
                st.session_state.token_3 = token
    if st.session_state.download:
        with st.spinner(f'Preparing Backup...'):
            headers = {
                'x-okapi-tenant': st.session_state.tenant_3,
                'x-okapi-token': st.session_state.token_3
            }

            file = backup(headers, st.session_state.okapi_3)
            st.download_button("Download Backup", data=file)

else:
    st.warning("Please Connect to Tenant First in Homepage.")



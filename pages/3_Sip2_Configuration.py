import pandas as pd
from datetime import datetime
import streamlit as st
import json
import requests
from legacy_session_state import legacy_session_state
legacy_session_state()
# st.session_state.update(st.session_state)



hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_menu_style, unsafe_allow_html=True)
def servicepoint():
    """
    Retrieves service points from the Okapi API and normalizes the data into a pandas dataframe
    :return: pandas dataframe containing the service point information
    """
    header = {"x-okapi-tenant": st.session_state.tenant, "x-okapi-token": st.session_state.token}
    # Endpoint for service points with a limit of 1000
    end_point_service = "service-points?limit=1000"
    url_service = f"{st.session_state.okapi}/{end_point_service}"
    # GET request to retrieve service points
    response = requests.get(url_service, headers=header).json()
    # Normalize the json data into a dataframe
    serivce_point = pd.json_normalize(response, record_path="servicepoints")
    return serivce_point



def sip(okapi, tenant, tokens, spoint1):
    now = datetime.now()
    date_time = now.strftime("%d-%m-%Y-%H%M%S")
    end_point_config = "configurations/entries?limit=1000"
    end_point_config_post = "configurations/entries"
    end_point_service = "service-points?limit=1000"

    url_config = f"{st.session_state.okapi}/{end_point_config}"
    url_service = f"{st.session_state.okapi}/{end_point_service}"
    url_config_post = f"{st.session_state.okapi}/{end_point_config_post}"
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    response = requests.get(url_config, headers=headers).json()

    acsTenantConfig = pd.json_normalize(response, record_path="configs")
    acsTenantConfig = acsTenantConfig[
        acsTenantConfig["configName"] == "acsTenantConfig"
    ]

    if len(acsTenantConfig) < 1:
        headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
        todo = {
            "module": "edge-sip2",
            "configName": "acsTenantConfig",
            "enabled": "true",
            "value": '{"supportedMessages":[{"messageName":"PATRON_STATUS_REQUEST","isSupported":"N"},{"messageName":"CHECKOUT","isSupported":"Y"},{"messageName":"CHECKIN","isSupported":"Y"},{"messageName":"BLOCK_PATRON","isSupported":"N"},{"messageName":"SC_ACS_STATUS","isSupported":"Y"},{"messageName":"LOGIN","isSupported":"Y"},{"messageName":"PATRON_INFORMATION","isSupported":"Y"},{"messageName":"END_PATRON_SESSION","isSupported":"Y"},{"messageName":"FEE_PAID","isSupported":"N"},{"messageName":"ITEM_INFORMATION","isSupported":"N"},{"messageName":"ITEM_STATUS_UPDATE","isSupported":"N"},{"messageName":"PATRON_ENABLE","isSupported":"N"},{"messageName":"HOLD","isSupported":"N"},{"messageName":"RENEW","isSupported":"N"},{"messageName":"RENEW_ALL","isSupported":"N"},{"messageName":"REQUEST_SC_ACS_RESEND","isSupported":"N"}],"statusUpdateOk":true,"offlineOk":false,"patronPasswordVerificationRequired":false}',
        }
        response = requests.post(url_config, data=json.dumps(todo), headers=headers)
    else:
        pass

    response = requests.get(url_service, headers=headers).json()
    serivce_point = pd.json_normalize(response, record_path= "servicepoints")
    serivce_point = serivce_point[["id", "name"]].reset_index()
    id_list = serivce_point.id.tolist()

    response = requests.get(url_config, headers=headers).json()
    selfCheckoutConfig = pd.json_normalize(response, record_path="configs")
    selfCheckoutConfig = selfCheckoutConfig[
        selfCheckoutConfig["configName"].str.contains("selfCheckoutConfig")
    ]
    selfCheckoutConfig["config_name_strip"] = selfCheckoutConfig.configName.str.split(
        "."
    ).str[1]

    for x in selfCheckoutConfig["config_name_strip"]:
        for i in selfCheckoutConfig["id"]:
            if x not in id_list:
                acsTenantConfig.to_csv("selfCheckoutConfig_output_before_delete.csv")
                selfCheckoutConfig = selfCheckoutConfig[
                    selfCheckoutConfig["config_name_strip"] == x
                ]
                for j in selfCheckoutConfig["id"]:
                    print(j)
                    del_url = f"{okapi}/{end_point_config_post}"
                    delt = requests.delete(del_url + "/" + j, headers=headers)


    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    todo = {
        "module": "edge-sip2",
        "configName": f"selfCheckoutConfig.{spoint2}",
        "enabled": "true",
        "value": '{"timeoutPeriod": 5,"retriesAllowed": 3,"checkinOk": true,"checkoutOk": true,"acsRenewalPolicy": false,"libraryName":"'
        + spoint1
        + '","terminalLocation":"'
        + spoint2
        + '"}',
    }
    response = requests.post(url_config_post, data=json.dumps(todo), headers=headers)

    # user_data = {
    #     "username": f"sip.{spoint2}",
    #     # "patronGroup": group_id,
    #     "active": True,
    #     "personal": {
    #         "lastName": f"sip.{spoint2}",
    #         "email": f"sip.{spoint2}",
    #         "addresses": [],
    #         "preferredContactTypeId": "002"
    #     }
    # }
    #
    # # Post user (create user)
    # create_user_res1 = requests.post(f"{st.session_state.okapi}/users", data=json.dumps(user_data), headers=headers)
    #
    # # Get user id
    # create_user_res = requests.get(f"{st.session_state.okapi}/users" + f"?query=(username ==sip.{spoint2})", headers=headers).json()
    # user_id = create_user_res["users"][0]["id"]
    #
    # # create user password
    # password_data = {
    #     "username": f"sip.{spoint2}",
    #     "password": "AAS@4770477!Medad",
    #     "userId": user_id
    # }
    # permissions_url1 = f"{st.session_state.okapi}/perms/permissions?query=(displayName==Naseej)"
    # permission_Admin_res = requests.get(permissions_url1, headers=headers).json()
    # admin_id = permission_Admin_res['permissions'][0]["id"]
    # perm_data = {
    #     "userId": user_id,
    #     "permissions": [admin_id]
    # }
    # # Add permissions
    # perm_res = requests.post(f"{st.session_state.okapi}/perms/users?full=true&indexField=userId", headers=headers,
    #                          data=json.dumps(perm_data))
    #
    # # Add password to user
    # pass_res = requests.post(f"{st.session_state.okapi}/authn/credentials", headers=headers,
    #                          data=json.dumps(password_data))
    #

def checkbox_disabled():
    confirm_disabled = True
    return confirm_disabled

confirm_disabled=False


st.markdown('''<html xmlns:v="urn:schemas-microsoft-com:vml"

<body lang=EN-US style='tab-interval:.5in;word-wrap:break-word'>

<div class=WordSection1>

<p class=MsoNormal><strong>Please make Sure that the following is completed before
proceeding:</strong></p>

<p class=MsoListParagraphCxSpFirst style='text-indent:-.25in;mso-list:l0 level1 lfo1'><![if !supportLists]><span
style='font-family:Symbol;mso-fareast-font-family:Symbol;mso-bidi-font-family:
Symbol'><span style='mso-list:Ignore'>·<span style='font:7.0pt "Times New Roman"'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</span></span></span><![endif]><span dir=LTR></span><span class=SpellE>Selfcheck</span>
has internet access.</p>

<p class=MsoListParagraphCxSpMiddle style='text-indent:-.25in;mso-list:l0 level1 lfo1'><![if !supportLists]><span
style='font-family:Symbol;mso-fareast-font-family:Symbol;mso-bidi-font-family:
Symbol'><span style='mso-list:Ignore'>·<span style='font:7.0pt "Times New Roman"'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</span></span></span><![endif]><span dir=LTR></span>Service points already been
configured.</p>

<p class=MsoListParagraphCxSpLast style='text-indent:-.25in;mso-list:l0 level1 lfo1'><![if !supportLists]><span
style='font-family:Symbol;mso-fareast-font-family:Symbol;mso-bidi-font-family:
Symbol'><span style='mso-list:Ignore'>·<span style='font:7.0pt "Times New Roman"'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</span></span></span><![endif]><span dir=LTR></span>Institution, Campuses,
Libraries and Locations already been configured</p>

</div>

</body>

</html>''', unsafe_allow_html=True)
confirm_sip=st.checkbox('Confirm', key='confirm', disabled=confirm_disabled,on_change=checkbox_disabled)


if confirm_sip:
    st.title("Sip Configuration")
    if st.session_state.allow_tenant:
        if 'sc_ip' not in st.session_state:
            st.session_state.sc_ip=''
        sip2_tenants = {
                "scTenants": [
                    {
                        "scSubnet": "127.0.0.1/24",
                        "tenant": f"{st.session_state.tenant}",
                        "errorDetectionEnabled": True,
                        "fieldDelimiter": "|",
                        "charset": "utf-8",
                    }
                ]
            }
        sip2tenant = json.dumps(sip2_tenants, sort_keys=False, indent=4)

        sip2 = {
                "port": 6443,
                "okapiUrl": f"{st.session_state.okapi}",
                "tenantConfigRetrieverOptions": {
                    "scanPeriod": 300000,
                    "stores": [
                        {
                            "type": "file",
                            "format": "json",
                            "config": {"path": "sip2-tenants.conf"},
                            "optional": False,
                        }
                    ],
                },
            }

        sip2conf=json.dumps(sip2, sort_keys=False, indent=4)

        sipb="""@echo off
            java -jar edge-sip2-fat.jar -conf sip2.conf
            """


        df = servicepoint()
        listspoint = df["name"].tolist()
        st.multiselect("Select Service point", options=listspoint, key="spoint1")
        # spoint2 = df.loc[df["name"] == st.session_state.spoint1, "id"].item()

        bt1, bt2 = st.columns(2)
        with bt1:
            if "sip2click" not in st.session_state:
                st.session_state.sip2click = False
            generatesip = st.button("Generate SIP")
            if generatesip:
                st.session_state.sip2click=True
            if st.session_state.sip2click:
                for i in st.session_state.spoint1:
                    spoint2 = df.loc[df["name"] == i, "id"].item()
                    sip(st.session_state.okapi, st.session_state.tenant, st.session_state.token, i)
                sipconfig = st.success("Sip Configured!", icon="✅")
                st.link_button('Download Java','https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.exe')
                st.link_button('Download Jar File', 'https://github.com/medadadmin/sip2-edge/releases/download/Sip2-Edge-Juniper/edge-sip2-fat.jar')
                st.download_button('Download sip2_tenants.conf', sip2tenant, file_name='sip2-tenants.conf')
                st.download_button('Download sip2.conf', sip2conf, file_name='sip2.conf')
                st.download_button('Download Sip2 Bat File', sipb, file_name='sip2.bat')

    else:
        st.warning("Please Connect to Tenant First.")





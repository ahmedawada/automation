import streamlit as st
from legacy_session_state import legacy_session_state
legacy_session_state()
from extras import (profile_picture,price_note,loan_type,default_job_profile,alt_types,
                    post_locale, addDepartments,circ_other,circ_loanhist,export_profile,configure_tenant,
                    post_record,modify_instance,post_holdings,get_holdings_id,
                    post_inventory_item,post_loan_period,post_patron_notice_policy,
                    post_overdue_fines_policy,post_lost_item_fees_policy)
from Notices import send_notice
import time
import asyncio


hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_menu_style, unsafe_allow_html=True)


st.subheader("Basic Tenant Configuration")
st.caption("in Order to start tenant configuration, kindly paste Medad ILS url (ex https://medad.ils.com ) and click on start configuration button.")

st.text_input('Client URL',key='clienturl')
c1, c2 = st.columns(2)
with c1:
    st.selectbox('TimeZone',
                 options=('Asia/Kuwait', 'Asia/Riyadh', 'Asia/Bahrain', 'Asia/Dubai', 'Asia/Muscat', 'Asia/Qatar'),
                 key='Timezone')


with c2:



    st.selectbox('Currency',options=('KWD','SAR','BHD','AED','OMR','QAR'),key='currency')


start = st.button("Start")
if 'btn2' not in st.session_state:
    st.session_state['btn2'] = False

if st.session_state.get('start_btn') != True:
    st.session_state.start_btn = start

if start:
    if st.session_state.start_btn is True:
        with st.spinner(f'Configuring the {st.session_state.tenant} Tenant'):
            time.sleep(5)

            post_record()
            time.sleep(5)
            instance_id = modify_instance()
            post_holdings(instance_id)
            holding_id = get_holdings_id(instance_id)
            post_inventory_item(holding_id)
            post_loan_period()
            post_overdue_fines_policy()
            post_lost_item_fees_policy()
            post_patron_notice_policy()
            send_notice()

            async def main():
                tasks = [
                    configure_tenant(),
                    price_note(),
                    loan_type(),
                    default_job_profile(),
                    alt_types(),
                    addDepartments(),
                    post_locale(st.session_state.Timezone, st.session_state.currency),
                    circ_other(),
                    circ_loanhist(),
                    export_profile(),
                    profile_picture()
                ]
                await asyncio.gather(*tasks)


            # Running the asyncio event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())



            st.success("Tenant is now Configured", icon="✅")
            st.session_state['btn2'] = True








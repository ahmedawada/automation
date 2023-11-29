from datetime import date
import streamlit as st
import requests as re
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import json
from Upload import upload
from legacy_session_state import legacy_session_state

legacy_session_state()

#https://okapi-g42.medad.com/configurations/entries
# {
#   "module": "CONFIGURATION_COLUMNS",
#   "configName": "DISPLAY_COLUMNS",
#   "value": "{\"cover\":true,\"publishers\":true,\"title\":true,\"indexTitle\":false,\"callNumber\":{\"classificationIdentifierType\":\"ce176ace-a53e-4b4d-aa89-725ed7b2edac\"},\"contributors\":false,\"publicationDate\":true,\"relation\":false}",
# }

# def time_interval(hour, minute, interval):
#     return [
#         f"{str(i).zfill(2)}:{str(j).zfill(2)}"
#         for i in range(hour)
#         for j in range(minute)
#         if j % interval == 0
#     ]
#
headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
services_endpoint = "/service-points"
calendar_endpoint = "/calendar/periods"
def calendar():
    # if 'allow_calendar' is True:
    File = upload('Calendar')
    df = pd.DataFrame(File)
    todays_date = date.today()
    days = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    # key = 0
    checkbox_statusses = []
    for day in days:
        checkbox_statusses.append(st.checkbox(day, key=day))
    create_cal_btn = st.button('Create Calendar')
    selected_days = []
    if create_cal_btn:
        if any(checkbox_statusses):
            st.success("You selected some checkboxes!")
            for d in days:
                if st.session_state[d] == True:
                    selected_days.append({"day": d})
            st.write(df)
            for index, row in df.iterrows():
                st.write(row['ServicePoints name'])

                service_points = re.get(
                    st.session_state.okapi + services_endpoint + f'?query=(name=={row["ServicePoints name"]})',
                    headers=headers).json()

                if not service_points['servicepoints']:
                    # IF THE SERVICE POINT DOES NOT EXIST
                    st.warning(f' Service point ({row["ServicePoints name"]}) does not exist.')

                else:
                    # IF SERVICE POINT FOUND, TAKE ID
                    service_id = service_points['servicepoints'][0]['id']

                    # CHECK IF CALENDAR EXISTS
                    cal_data = {
                        'withOpeningDays': True,
                        'showPast': True,
                        'showExceptional': False
                    }

                    check_cal_res = re.get(f'{st.session_state.okapi}{calendar_endpoint}/{service_id}/period?withOpeningDays=true&showPast=true&showExceptional=false', data=json.dumps(cal_data), headers=headers).json()
                    st.write(check_cal_res)

                    # FILL IN A DICTIONARY WITH ALL REQUIRED DATA
                    opening_days = []
                    hours = {
                        "startTime": str(row['start']),
                        "endTime": str(row['end'])
                    }
                    for i in selected_days:
                        opening_days.append(
                            {"weekdays": i,
                             "openingDay": {"openingHour": [hours],
                                            "allDay": False,
                                            "open": True
                                            }})

                    if not check_cal_res['openingPeriods']:
                        # IF CALENDAR NOT CREATED YET
                        st.success("Creating calendar")
                        # response = re.get(f'{st.session_state.okapi}/{calendar_endpoint}/')
                        data = {
                            "name": row['ServicePoints name'],
                            "startDate": str(todays_date),
                            "endDate": str(todays_date.replace(year=todays_date.year + 50)),
                            "openingDays": opening_days,
                            "servicePointId": service_id,
                            "id": service_id
                        }

                        create_cal = re.post(f'{st.session_state.okapi}{calendar_endpoint}/{service_id}/period',
                                            data=json.dumps(data), headers=headers)

                        st.write(create_cal.content)
                    else:
                        # IF CALENDAR CREATED, TAKE ID AND PUT REQUEST
                        st.success('Updating calendar')

                        cal_id = check_cal_res['openingPeriods'][0]['id']
                        data = {
                            "name": row['ServicePoints name'],
                            "startDate": str(todays_date),
                            "endDate": str(todays_date.replace(year=todays_date.year + 50)),
                            "openingDays": opening_days,
                            "servicePointId": service_id
                            # ,
                            # "id": cal_id
                        }

                        #https://okapi.medad.com/calendar/periods/3a40852d-49fd-4df2-a1f9-6e2641a6e91f/period/031e1b55-d340-436f-9cd6-6a04f740dbb7
                        update_cal = re.post(f'{st.session_state.okapi}{calendar_endpoint}/{service_id}/period',
                                            data=json.dumps(data), headers=headers)
                        st.write(update_cal.content)

        else:
            st.warning("No selectboxes selected!")




    # calendar_endpoint = "/calendar/periods/d8b94015-c108-4f18-89ce-c00d4f7b7fc0/period"
    #
    # service_points = re.get(st.session_state.okapi+services_endpoint, headers=headers).json()
    # todays_date = date.today()
    # days = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    # df = pd.DataFrame(days, columns=['Day'])
    # builder = GridOptionsBuilder.from_dataframe(df)
    # builder.configure_selection(selection_mode='multiple', use_checkbox=True, header_checkbox=True)
    # builder.configure_pagination(enabled=True)
    # list = ['1:00', '2:00', '3:00']
    # # times = time_interval(24, 60, 15)
    #
    # builder.configure_column('Opening Time', editable=True, index=times.index("00:00"), cellEditor='agSelectCellEditor', cellEditorParams={'values': times}, singleClickEdit=True)
    # builder.configure_column('Closing Time', editable=True, index=times.index("00:00"), cellEditor='agSelectCellEditor',cellEditorParams={'values': times}, singleClickEdit=True)
    # go = builder.build()
    # grid_return = AgGrid(df, editable=True, theme='balham', gridOptions=go)
    #
    # selected_rows = grid_return['selected_rows']
    #
    # if bool(selected_rows):
    #     selection = pd.DataFrame(selected_rows)
    #     selection.fillna("00:00", inplace=True)
    #     createCal = st.button('Update Calendar')
    #     st.write(selection)
    #     if createCal:
    #         working_days = []
    #         working = []
    #         hours = []
    #         open_hours = []
    #         closed_hours = []
    #         # FLAG TO CHECK IF TIMES ARE CHOSEN
    #         check_opening_chosen = 0
    #         check_closing_chosen = 0
    #
    #         row_num = selection.shape[0]
    #         # IF TIMES NOT SELECTED
    #         if ('Opening Time' not in selection):
    #             for j in range(0, selection.shape[0]):
    #                 open_hours.append("00:00")
    #             check_opening_chosen = 1
    #
    #         if ('Closing Time' not in selection):
    #             for j in range(0, selection.shape[0]):
    #                 closed_hours.append("00:00")
    #             check_closing_chosen = 1
    #
    #         counter = 0
    #         for index, row in selection.iterrows():
    #             if check_opening_chosen == 0:
    #                 open_hours = row['Opening Time']
    #             if check_closing_chosen == 0:
    #                 closed_hours = row['Closing Time']
    #             working_days.append(row['Day'])
    #             working.append({"day": row['Day']})
    #             hours.append({"startTime": open_hours[counter], "endTime": closed_hours[counter]})
    #             counter = counter + 1
    #         # st.write(working)
    #         # st.write(hours)
    #         data = {
    #             "name": "ra",
    #             "startDate": str(todays_date),
    #             "endDate": str(todays_date.replace(year=todays_date.year + 50)),
    #             "openingDays": [],
    #             "servicePointId": "d8b94015-c108-4f18-89ce-c00d4f7b7fc0",
    #             "id": "166b6783-29b2-4782-8cc9-6301ab81ae31"
    #         }
    #         for i in range(0, counter):
    #             data["openingDays"].append({"weekdays": working[i], "openingDay": {"openingHour": [hours[i]],
    #                                                                                "allDay": False, "open": True}})
    #         st.write(json.dumps(data))
    #         c = 1
    #         for x in service_points['servicepoints']:
    #             # st.write(c)
    #             service_id = x['id']
    #             # st.write(service_id)
    #             c = c+1
    # https: // okapi - g42.medad.com/calendar/periods/e82a8ea3-0db6-4da4-b67d-6e9efd2d8738/period
    # {
    #     "name": "test",
    #     "startDate": "2023-03-15",
    #     "endDate": "2023-03-15",
    #     "openingDays": [
    #         {
    #             "weekdays": {
    #                 "day": "SUNDAY"
    #             },
    #             "openingDay": {
    #                 "openingHour": [
    #                     {
    #                         "startTime": "00:00",
    #                         "endTime": "02:30"
    #                     }
    #                 ],
    #                 "allDay": false,
    #                 "open": true
    #             }
    #         },
    #         {
    #             "weekdays": {
    #                 "day": "MONDAY"
    #             },
    #             "openingDay": {
    #                 "openingHour": [
    #                     {
    #                         "startTime": "00:00",
    #                         "endTime": "02:30"
    #                     }
    #                 ],
    #                 "allDay": false,
    #                 "open": true
    #             }
    #         },
    #         {
    #             "weekdays": {
    #                 "day": "TUESDAY"
    #             },
    #             "openingDay": {
    #                 "openingHour": [
    #                     {
    #                         "startTime": "00:00",
    #                         "endTime": "02:00"
    #                     }
    #                 ],
    #                 "allDay": false,
    #                 "open": true
    #             }
    #         }
    #     ],
    #     "servicePointId": "e82a8ea3-0db6-4da4-b67d-6e9efd2d8738",
    #     "id": "68ca0415-3452-47a7-818f-0c09da6e07c1"
    # }

    # from_time = st.time_input('Opening at: ', datetime.time(8, 0))
    # st.write('Library open from ', from_time)
    #
    # close_time = st.time_input('Closes at: ', datetime.time(20, 0))
    # st.write('Library closes ', close_time)


    # else:
    #     st.warning('Please create locations first.')

def exceptions():
    file = upload('Calendar Exceptions')
    df = pd.DataFrame(file)
    for index, row in df.iterrows():
        # st.write(row['ServicePoints name'])
        service_points = re.get(
            st.session_state.okapi + services_endpoint + f'?query=(name=={row["ServicePoints name"]})',
            headers=headers).json()
        if not service_points['servicepoints']:
            # IF THE SERVICE POINT DOES NOT EXIST
            st.warning(f' Service point ({row["ServicePoints name"]}) does not exist.')

        else:
            # IF SERVICE POINT FOUND, TAKE ID
            service_id = service_points['servicepoints'][0]['id']
            # 'https://okapi.medadstg.com/calendar/periods/1b9f5ef4-3450-48a2-afdc-f2ca9e02805f/period'
            # {
            #     "servicePointId": "1b9f5ef4-3450-48a2-afdc-f2ca9e02805f",
            #     "name": "test",
            #     "startDate": "2023-05-14",
            #     "endDate": "2023-05-14",
            #     "openingDays": [
            #         {
            #             "openingDay": {
            #                 "openingHour": [
            #                     {
            #                         "startTime": "19:10",
            #                         "endTime": "21:10"
            #                     }
            #                 ],
            #                 "allDay": null,
            #                 "open": true
            #             }
            #         }
            #     ],
            #     "id": "0e7c1080-b2f9-428a-8b27-9d7fa5fa4aae"
            # }


import streamlit as st
import requests
import json
from legacy_session_state import legacy_session_state

legacy_session_state()


def backup(headers, okapi):
    ends = ['/groups?limit=1000', '/service-points?limit=100',
            '/fixed-due-date-schedule-storage/fixed-due-date-schedules?limit=1000', '/loan-types?limit=500',
            '/loan-policy-storage/loan-policies?limit=100',
            '/fixed-due-date-schedule-storage/fixed-due-date-schedules?limit=100',
            '/request-policy-storage/request-policies?limit=100', '/overdue-fines-policies?limit=100',
            '/lost-item-fees-policies?limit=100', '/templates?query=active==true&limit=100',
            '/patron-notice-policy-storage/patron-notice-policies?limit=100', '/staff-slips-storage/staff-slips',
            '/circulation/rules', '/configurations/entries?limit=500',
            '/calendar/periods?limit=1000', '/alternative-title-types?limit=1000', '/classification-types?limit=1000',
            '/contributor-types?limit=1000', '/instance-formats?limit=1000', '/instance-note-types?limit=1000',
            '/instance-statuses?limit=1000', '/modes-of-issuance?limit=1000', '/nature-of-content-terms?limit=1000',
            '/identifier-types?limit=1000', '/instance-types?limit=1000', '/holdings-note-types?limit=1000',
            '/holdings-sources?limit=1000', '/holdings-types?limit=1000', '/ill-policies?limit=1000',
            '/item-note-types?limit=1000', '/loan-types?limit=1000', '/material-types?limit=1000']
    keys = ['usergroups', 'servicepoints']
    allResults = []
    for i in range(0, len(ends)):
        urlGet = '{}{}'.format(okapi, ends[i])  # create variable for the GET URL
        responseVar = requests.request("GET", urlGet, headers=headers)
        responseJson = responseVar.json()
        # responseResults = responseJson[keys[i]]
        allResults.append(responseJson)

    # for b in allResults:
    #     if 'metadata' in b:
    #         del (b['metadata'])

    return json.dumps(allResults, sort_keys=False, indent=4)


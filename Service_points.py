import streamlit as st
from Upload import upload
import requests
from pandas import json_normalize
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import json

from legacy_session_state import legacy_session_state

# Get session state of legacy session
legacy_session_state()

def create_sp(sp_name,sp_code,disp_name,desc):
    spurl=f'{st.session_state.okapi}/service-points'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    to_do= {
  "name" : f"{sp_name}",
  "code" : f"{sp_code}",
  "discoveryDisplayName" : f"{disp_name}",
  "description" : f"{desc}"

    }
    response = requests.post(spurl, data=json.dumps(to_do), headers=headers)
    st.write(response.content)
def create_institutions(inistname,insticode):
    insurl=f'{st.session_state.okapi}/location-units/institutions'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    to_do={
  "name" : f"{inistname}",
  "code" : f"{insticode}"

}
    response = requests.post(insurl, data=json.dumps(to_do), headers=headers)

def create_campuses(campusname, campuscode, instuuid):
    campusurl=f'{st.session_state.okapi}/location-units/campuses'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    to_do={
  "name" : f"{campusname}",
  "code" : f"{campuscode}",
  "institutionId" : f"{instuuid}",

}
    response = requests.post(campusurl, data=json.dumps(to_do), headers=headers)


def create_libraries(libraryname, librarycode, campusuuid):
    liburl=f'{st.session_state.okapi}/location-units/libraries'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}
    to_do={
  "name" : f"{libraryname}",
  "code" : f"{librarycode}",
  "campusId" : f"{campusuuid}"
}
    requests.post(liburl, data=json.dumps(to_do), headers=headers)

def create_locations(locationname, locationcode, displayname, instuuid, campusuuid, libuuid, spprimaryuuid, splistuuid):
    locurl=f'{st.session_state.okapi}/locations'
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}


    to_do={

  "name" : f"{locationname}",
  "code" : f"{locationcode}",
  "discoveryDisplayName" : f"{displayname}",
  "isActive" : True,
  "institutionId" : f"{instuuid}",
  "campusId" : f"{campusuuid}",
  "libraryId" : f"{libuuid}",
  # "details" : { },
  "primaryServicePoint" : f"{spprimaryuuid}",
  "servicePointIds" : splistuuid,

}

    requests.post(locurl, data=json.dumps(to_do), headers=headers)

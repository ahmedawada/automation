import requests
import json
import sys
from legacy_session_state import legacy_session_state

legacy_session_state()

"""
support checking whether a POST request errored out - 
if it did, one of the phrases below appears in the request
response, and we can use that to trigger trying a PUT request instead.
"""

error_phrases = ["errors", "ERROR", "duplicate key"]

"""
First function - askenvironment()

This is specific to Duke, and allows you to ask in real time which environments you are moving 
settings from, and which you are moving to.

It returns two variables that are used to match to the appropriate section in
config-template.ini in main.py

"""


def askenvironment():
    movefromserver = input("Which environment are we moving configs from? (prod, stag) ")
    if movefromserver == 'prod':
        movefromenv = 'prod'
    elif movefromserver == 'stag':
        movefromenv = 'stag'
    else:
        print("unrecognized move from environment")
        sys.exit()
    movetoserver = input("Which environment are we moving to? (prod, stag) ")
    if movefromserver == movetoserver:
        print("Can't be the same thing!")
        sys.exit()
    if movetoserver == 'prod':
        movetoenv = 'prod'
    elif movetoserver == 'stag':
        movetoenv = 'stag'

    else:
        print("Unrecognized move to environment")
        sys.exit()
    return movefromenv, movetoenv


"""
Some scripts only use one server - this function is used for those.
"""


def asksingleenvironment():
    whichsingleserver = input("Which environment are we working on? (prod, stag) ")
    if whichsingleserver == 'prod':
        workingserver = 'prod'
    elif whichsingleserver == 'stag':
        workingserver = 'stag'
    elif whichsingleserver == 'snapshot':
        workingserver = 'snapshot'
    else:
        print("unrecognized server environment")
        sys.exit()
    return workingserver


"""
Next set of definitions - fetching settings files and returning the JSON.

This could be made more generalized, but for now, the API calls
are individually hard coded since we may want the limits to change depending on the values.
"""


def fetchsettings(server, fetchheaders, *args):
    fetchsettingsurl = f'{server}{"".join(args)}'
    fetchsettingsrequest = requests.get(fetchsettingsurl, headers=fetchheaders)
    fetchsettingsjson = fetchsettingsrequest.json()
    return fetchsettingsjson


def fetchpatrongroups(server, fetchheaders):
    patronGroupsUrl = '{}{}'.format(server, '/groups?limit=1000')
    patronGroupsRequest = requests.get(patronGroupsUrl, headers=fetchheaders)
    patronGroupsJson = patronGroupsRequest.json()
    return patronGroupsJson


def fetchloantypes(server, fetchHeaders):
    loanTypesUrl = '{}{}'.format(server, '/loan-types?limit=1000')
    loanTypesRequest = requests.get(loanTypesUrl, headers=fetchHeaders)
    loanTypesJson = loanTypesRequest.json()
    return loanTypesJson


def fetchmaterialtypes(server, fetchHeaders):
    materialTypesUrl = '{}{}'.format(server, '/material-types?limit=1000')
    materialTypesRequest = requests.get(materialTypesUrl, headers=fetchHeaders)
    materialTypesJson = materialTypesRequest.json()
    return materialTypesJson


def fetchlibraries(server, fetchHeaders):
    librariesUrl = '{}{}'.format(server, '/location-units/libraries?limit=100')
    librariesRequest = requests.get(librariesUrl, headers=fetchHeaders)
    librariesJson = librariesRequest.json()
    return librariesJson


def fetchlocations(server, fetchHeaders):
    locationsUrl = '{}{}'.format(server, '/locations?limit=1500')
    locationsRequest = requests.get(locationsUrl, headers=fetchHeaders)
    locationsJson = locationsRequest.json()
    return locationsJson


def fetchloanpolicies(server, fetchHeaders):
    loanPoliciesUrl = '{}{}'.format(server, '/loan-policy-storage/loan-policies?limit=500')
    loanPoliciesRequest = requests.get(loanPoliciesUrl, headers=fetchHeaders)
    loanPoliciesJson = loanPoliciesRequest.json()
    return loanPoliciesJson


def fetchnoticepolicies(server, fetchHeaders):
    noticePoliciesUrl = '{}{}'.format(server, '/patron-notice-policy-storage/patron-notice-policies?limit=100')
    noticePoliciesRequest = requests.get(noticePoliciesUrl, headers=fetchHeaders)
    noticePoliciesJson = noticePoliciesRequest.json()
    return noticePoliciesJson


def fetchrequestpolicies(server, fetchHeaders):
    requestPoliciesUrl = '{}{}'.format(server, '/request-policy-storage/request-policies?limit=50')
    requestPoliciesRequest = requests.get(requestPoliciesUrl, headers=fetchHeaders)
    requestPoliciesJson = requestPoliciesRequest.json()
    return requestPoliciesJson


def fetchoverduepolicies(server, fetchHeaders):
    overduePoliciesUrl = '{}{}'.format(server, '/overdue-fines-policies?limit=100')
    overduePoliciesRequest = requests.get(overduePoliciesUrl, headers=fetchHeaders)
    overduePoliciesJson = overduePoliciesRequest.json()
    return overduePoliciesJson


def fetchlostpolicies(server, fetchHeaders):
    lostItemPoliciesUrl = '{}{}'.format(server, '/lost-item-fees-policies?limit=100')
    lostItemPoliciesRequest = requests.get(lostItemPoliciesUrl, headers=fetchHeaders)
    lostItemPoliciesJson = lostItemPoliciesRequest.json()
    return lostItemPoliciesJson


"""
fetchfriendlysettingname()

this lets you take a setting UUID from a query and pull the friendly name from the
json file that you previously had downloaded using one of the functions above.

WIP - making this more generalizable

"""
#
# def fetchfriendlysettingname(id, jsonSettingsFile, key, friendlyResults):
#     # key in the function call is a variable; here, you have to read its value into a local variable to get
#     # python's dictionary functions to call values as expected
#     keyname = key
#     for i in jsonSettingsFile:
#         print((jsonSettingsFile[keyname]))
#         # if id == jsonSettingsFile['id']:
#         #     friendlyResults[keyname] = i['name']
#         # if not keyname in friendlyResults:
#         #     friendlyResults[keyname] = "Setting %s not found" % key


"""
These functions take a setting UUID and add the friendly name to a file.

Could be more generalizable; work in progress.

"""


def fetchfriendlyusergroupname(id, patronGroupsJson, friendlyResults):
    for i in patronGroupsJson['usergroups']:
        if i['id'] == id:
            friendlyResults['patron_group'] = i['group']
    if not 'patron_group' in friendlyResults:
        friendlyResults['patron_group'] = "Patron group not found"


def fetchfriendlyloantypename(id, loanTypesJson, friendlyResults):
    for i in loanTypesJson['loantypes']:
        if i['id'] == id:
            friendlyResults['loan_type'] = i['name']
    if not 'loan_type' in friendlyResults:
        friendlyResults['loan_type'] = "Loan type not found"


def fetchfriendlymaterialtypename(id, materialTypesJson, friendlyResults):
    for i in materialTypesJson['mtypes']:
        if i['id'] == id:
            friendlyResults['material_type'] = i['name']
    if not 'material_type' in friendlyResults:
        friendlyResults['material_type'] = "Material type not found"


# # pull location friendly name - using location code since a lot of Duke location names have commas in them
# # which makes working with CSV a little too messy
# #
# # also pulling library friendly name so that it can be used in sorting/reviewing results in the
# # output file

def fetchlocationcode(id, locationsJson, librariesJson, friendlyResults):
    for i in locationsJson['locations']:
        if i['id'] == id:  # once you find the location ....
            for j in librariesJson['loclibs']:  # use the location to search your stored copy of the libraries Json
                if i['libraryId'] == j['id']:  # to find the associated library
                    friendlyResults['library_name'] = j['name']  # and pull the name
            friendlyResults['location'] = i[
                'code']  # finally, add the location code so that it shows up in that order in the output file.
    if not 'library_name' in friendlyResults:
        friendlyResults['libraryName'], friendlyResults['location'] = "Library not found", "Location not found"
    if not 'location' in friendlyResults:
        friendlyResults['location'] = "Location not found"


# map a circulation policy ID to friendly name

def policytoname(url, fetchHeaders, key, friendlyResults):
    # key in the function call is a variable; here, you have to read its value into a local variable to get
    # python's dictionary functions to call values as expected
    keyname = key
    postPolicy = requests.get(url, headers=fetchHeaders)
    postPolicyJson = postPolicy.json()
    # you should always get a policy - either the matched policy, or the fallback. So we don't add functions here to
    # accommodate not finding a result like we do in other functions
    for i in postPolicyJson:
        print(postPolicyJson[i])


"""
Now we have our desired settings function that we can use to move our settings between
environments

param  is the string to use to construct the URL for 'GET' or 'POST'
param2 is the string to use to construct the URL for 'PUT'

E.g., for patron groups, the function is
    ff.moveSettings("/groups?limit=1000", "/groups/", "usergroups", moveUrl, moveToUrl, fetchHeaders, postHeaders)

param = "/groups?limit=1000" -- that is used for both the GET and the POST call, the ?limit=1000 isn't needed for the post but
it doesn't hurt to include it.
param2 = "/groups/" -- that is used for the PUT call, which includes a UUID after /groups/ and as such has a different URL structure.

"""


def moveSettings(param, param2, key, moveFromEnv, moveToEnv, fetchHeaders, postHeaders):
    urlGet = '{}{}'.format(moveFromEnv, param)  # create variable for the GET URL
    urlPost = '{}{}'.format(moveToEnv, param)  # create variable for the POST URL
    responseVar = requests.request("GET", urlGet, headers=fetchHeaders)
    responseJson = responseVar.json()
    responseResults = responseJson[key]
    for b in responseResults:
        del (b['metadata'])  # you need to remove the metadata object in order to send it to the new server
        # b.popitem()
    for c in responseResults:
        #st.write("Sending setting %s" % c)
        payload = json.dumps(c)
        r = requests.post(urlPost, data=payload, headers=postHeaders)
        # if your object already exists, the API will give an error. This next loop checks for an identified
        # phrase in the response to indicate error (since it varies by API) - if it finds the phrase,
        # it sends the request again as a PUT, and prints the response to the screen
        if any(x in r.text for x in error_phrases):
            #st.write("Resending as PUT %s" % c)
            urlPut = '{}{}{}'.format(moveToEnv, param2, c['id'])
            rPut = requests.put(urlPut, data=payload, headers=postHeaders)
            #st.write(rPut.text)


# movecircrules
#
# The circulation rules file always exist when FOLIO has circulation modules,
# so there's no concept of an API post here,
# only a PUT.

def movecircrules(param, key, moveFromEnv, moveToEnv, fetchHeaders, postHeaders):
    urlGet = '{}{}'.format(moveFromEnv, param)  # create variable for the GET URL
    urlPut = '{}{}'.format(moveToEnv, param)  # create variable for the PUT URL
    responseVar = requests.request("GET", urlGet, headers=fetchHeaders)
    rules = responseVar.json()
    rulesAsText = rules[key]
    rulesAsTextJson = json.dumps(rulesAsText)
    rulesAsTextPayload = '{ "rulesAsText" : ' + rulesAsTextJson + '}'  # construct the rules payload by adding the attribute name
    print("Sending circulation rules")
    rulesPut = requests.request("PUT", urlPut, headers=postHeaders, data=rulesAsTextPayload)
    print(rulesPut.text)


def movelocations(moveFromEnv, moveToEnv, fetchHeaders, postHeaders):
    locationApiValues = {'locinsts': '/location-units/institutions?limit=100',
                         'loccamps': '/location-units/campuses?limit=100',
                         'loclibs': '/location-units/libraries?limit=100',
                         'locations': '/locations?limit=1000'}
    apiPutValues = {'locinsts': '/location-units/institutions/', 'loccamps': '/location-units/campuses/',
                    'loclibs': '/location-units/libraries/', 'locations': '/locations/'}
    for g in locationApiValues:
        urlGet = '{}{}'.format(moveFromEnv, locationApiValues.get(g))  # create variable for the GET URL
        urlPost = '{}{}'.format(moveToEnv, locationApiValues.get(g))  # create variable for the POST URL
        responseVar = requests.request("GET", urlGet, headers=fetchHeaders)
        responseJson = responseVar.json()
        responseResults = responseJson[g]
        for f in responseResults:
            f.popitem()
        for h in responseResults:
            payload = json.dumps(h)
            print("Sending %s" % h['name'])
            r = requests.post(urlPost, data=payload, headers=postHeaders)
            # if your object already exists, the API will give an error. This next loop checks for an identified
            # phrase in the response to indicate error (since it varies by API) - if it finds the phrase,
            # it sends the request again but as a PUT
            if any(x in r.text for x in error_phrases):
                print("Sending again as PUT request %s" % h['name'])
                urlPut = '{}{}{}'.format(moveToEnv, apiPutValues.get(g), h['id'])
                rPut = requests.put(urlPut, data=payload, headers=postHeaders)


# generic function to move the majority of circulation policy stuff from one environment to another
# this can be used with
# loan policies
# request policies
# notice policies
# overdue policies
# lost item policies
# fixed due date schedules
# notice templates
# it can be moved with service points if you only want the service point to move and not the calendar
# if you want calendars to move, it's easier to do it with the service point in one function

def movecircpolicies(param, param2, key, moveFromEnv, moveToEnv, fetchHeaders, postHeaders):
    urlGet = '{}{}'.format(moveFromEnv, param)  # create variable for the GET URL
    urlPost = '{}{}'.format(moveToEnv, param)  # create variable for the POST URL
    responseVar = requests.request("GET", urlGet, headers=fetchHeaders)  # fetch settings from moveFrom environment
    responseJson = responseVar.json()  # turn response into Json object so you can get rid of the keys
    responseResults = responseJson[key]

    for j in responseResults:  # remove metadata object
        if 'metadata' in j:
            del (j['metadata'])  # remove metadata object
    for k in responseResults:  # post object to moveToEnv.
        print("sending %s" % k)
        payload = json.dumps(k)
        r = requests.post(urlPost, data=payload, headers=postHeaders)
        # if your object already exists, the API will give an error. This next loop checks for an identified
        # phrase in the response to indicate error (since it varies by API) - if it finds the phrase,
        # it sends the request again as a PUT
        if any(x in r.text for x in error_phrases):
            print("Sending as PUT request %s" % k)
            urlPut = '{}{}{}'.format(moveToEnv, param2, k['id'])
            rPut = requests.put(urlPut, data=payload, headers=postHeaders)

# if you need to move calendars,  you move them with the service point info, so that is defined here as
# a separate function

# def movecalendars(moveFromEnv, moveToEnv, fetchHeaders, postHeaders):
#     # first, you're going to get the service points
#     urlGetServicePoints = '{}{}'.format(moveFromEnv, "/service-points?limit=100")  # create variable for the GET URL
#     responseGetServicePoints = requests.request("GET", urlGetServicePoints, headers=fetchHeaders)
#     responseServicePointsJson = responseGetServicePoints.json()
#     responseServicePoints = responseServicePointsJson["servicepoints"]
#     for j in responseServicePoints:
#         calendarId = j["id"]
#         urlGetCalendarPeriods = '{}{}{}{}'.format(moveFromEnv, "/calendar/periods/", calendarId, "/period?withOpeningDays" )
#
#     urlPost = '{}{}'.format(moveToEnv, param)  # create variable for the POST URL
#     responseVar = requests.request("GET", urlGet, headers=fetchHeaders)  # fetch settings from moveFrom environment
#     responseJson = responseVar.json()  # turn response into Json object so you can get rid of the keys
#     responseResults = responseJson[key]
#     for j in responseResults:  # remove metadata object
#         del (j['metadata'])  # remove metadata object
#     for k in responseResults:  # post object to moveToEnv.
#         print("sending %s" % k)
#         payload = json.dumps(k)
#         r = requests.post(urlPost, data=payload, headers=postHeaders)
#         # if your object already exists, the API will give an error. This next loop checks for an identified
#         # phrase in the response to indicate error (since it varies by API) - if it finds the phrase,
#         # it sends the request again as a PUT
#         if any(x in r.text for x in error_phrases):
#             print("Sending as PUT request %s" % k)
#             urlPut = '{}{}{}'.format(moveToEnv, param2, k['id'])
#             rPut = requests.put(urlPut, data=payload, headers=postHeaders)


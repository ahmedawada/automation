import requests
import json
import streamlit as st
from legacy_session_state import legacy_session_state

legacy_session_state()


def send_notice():
    template_names=["Cancellation Notice","Item Available Notice","Recall Overdue Notice","Courtesy Notice",
                    "Check out Notice","Check in Notice","Hold Placed Notice","Page Request Notice","Recall Request Notice",
                    "Hold Expiration Notice","Request Expiration Notice","Recall Notice","Overdue Notice","Notice of Fine or Fee"]
    end_point_template_post = "templates"
    url_template_post = f"{st.session_state.okapi}/{end_point_template_post}"
    headers = {"x-okapi-tenant": f"{st.session_state.tenant}", "x-okapi-token": f"{st.session_state.token}"}

    circ_template = []
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Cancellation Notice",
                "body": "<div>{{item.effectiveLocationLibrary}}</div><div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>We regret that your request for the following item was cancelled.</div><div><br></div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><br></div><div>In most cases cancellations occur because the item was not available by the (not needed after) date you specified in your original request.</div><div>&nbsp;</div><div>Please contact the library staff if you still have a need for this item.</div><div>&nbsp;</div><div>If you have any questions please contact us at the indicated location.</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Phone: </strong>(XXX)XXX-XXXX</div>",
                "attachments": []
            }
        },
        "name": template_names[0],
        "active": "true",
        "category": "Request"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Item Available Notice",
                "body": "<div>{{request.servicePointPickup}}</div><div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>The item that you requested are now available at the location(s) shown below. Please pick up item(s) before the indicated expiration date.</div><div><br></div><div><strong>Location</strong>: {{request.servicePointPickup}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Expiration Date</strong>: {{request.holdShelfExpirationDate}}</div><div><br></div><div>If you have any questions please contact us at the indicated location.</div><div><strong>Location</strong>: {{request.servicePointPickup}}</div><div><strong>Phone:</strong> (XXX)XXX-XXXX</div>",
                "attachments": []
            }
        },
        "name": template_names[1],
        "active": "true",
        "category": "Request"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Recall- Overdue Notice",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}},</div><div><br></div><div>Please return the following recalled item(s) immediateley to the indicated location. Fines will be assessed for overdue recalled library material(s). A fine of $1.00 per day with a maximum fine amount of $20.00 will be charged to your account for each item not returned by the recalled due date(s).</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Notification Number</strong>: XXX</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Due Date</strong>: {{loan.dueDate}}</div><div><br></div><div>{{/loans}}</div><div>Fines for overdue recalled items are substantial and increase the longer you keep the item. Please return the urgently needed item(s).</div><div>&nbsp;</div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone</strong>: (XXX)XXX-XXXX</div>",
                "attachments": []
            }
        },
        "name": template_names[2],
        "active": "true",
        "category": "Loan"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Courtesy Notice",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>This notice is to remind you that these item(s) will be due soon. To renew your item(s) please log in to to your library account. Please verify that your items were renewed. Some items are not renewable. If your items were not renewed and/or you have any questions, please contact us at the indicated location(s).</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Notification Number:</strong> XXX</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Copy #</strong>: {{item.copy}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Due Date</strong>: {{loan.dueDate}}</div><div><br></div><div>{{/loans}}</div><div>Please return the item(s) or have the item(s) renewed.</div><div><br></div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone:</strong> (XXX)XXX-XXXX</div><div><br></div>",
                "attachments": []
            }
        },
        "name": template_names[3],
        "active": "true",
        "category": "Loan"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Thank You for Borrowing!",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>This a confirmation that you checked out the following:</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Copy #</strong>: {{item.copy}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Due Date</strong>: {{loan.dueDate}}</div><div><br></div><div>{{/loans}}</div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone:</strong> (XXX)XXX-XXXX</div><div><br></div>",
                "attachments": []
            }
        },
        "name": template_names[4],
        "active": "true",
        "category": "Loan"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Thank you for returning library materials",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>This a confirmation that you returned the following:</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Copy #</strong>: {{item.copy}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><br></div><div>{{/loans}}</div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone:</strong> (XXX)XXX-XXXX</div><div><br></div>",
                "attachments": []
            }
        },
        "name": template_names[5],
        "active": "true",
        "category": "Loan"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Your hold was successfully placed",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>This a notice that you have successfully placed a hold on: </div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Copy #</strong>: {{item.copy}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><br></div><div>{{/loans}}</div><div>You will be contacted when it is ready to pick up. If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone:</strong> (XXX)XXX-XXXX</div><div><br></div>",
                "attachments": []
            }
        },
        "name": template_names[6],
        "active": "true",
        "category": "Request"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Your page request has been received",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>This a notice that you have successfully requested a page for: </div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Copy #</strong>: {{item.copy}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><br></div><div>{{/loans}}</div><div>You will be contacted when it is ready to pick up. If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone:</strong> (XXX)XXX-XXXX</div><div><br></div>",
                "attachments": []
            }
        },
        "name": template_names[7],
        "active": "true",
        "category": "Request"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Your recall request has been made",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>This a notice that you have successfully requested the following item be recalled: </div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Copy #</strong>: {{item.copy}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><br></div><div>{{/loans}}</div><div>You will be contacted when it is ready to pick up. If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone:</strong> (XXX)XXX-XXXX</div><div><br></div>",
                "attachments": []
            }
        },
        "name": template_names[8],
        "active": "true",
        "category": "Request"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Your Hold has Expired",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>This a notice that hold(s) expired you made for:</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Copy #</strong>: {{item.copy}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><br></div><div>{{/loans}}</div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone:</strong> (XXX)XXX-XXXX</div><div><br></div>",
                "attachments": []
            }
        },
        "name": template_names[9],
        "active": "true",
        "category": "Request"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Your Request has Expired",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>This a notice that request(s) expired you made for:</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Copy #</strong>: {{item.copy}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><br></div><div>{{/loans}}</div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone:</strong> (XXX)XXX-XXXX</div><div><br></div>",
                "attachments": []
            }
        },
        "name": template_names[10],
        "active": "true",
        "category": "Request"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Recall Notice",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>The following item(s) currently charged to you are needed by another patron. The new due date(s) are shown below. Please return item(s) to the indicated location(s). Fines will be assessed for items not returned by the new due date(s). A fine daily fine up to a maximum will be charged to your account if item(s) are returned after the new due date(s).</div><div><br></div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Due Date</strong>: {{loan.dueDate}}</div><div><br></div><div>If you have any questions please contact us at the indicated location:</div><div><br></div><div><strong>Phone: </strong>(XXX)XXX-XXXX</div>",
                "attachments": []
            }
        },
        "name": template_names[11],
        "active": "true",
        "category": "Loan"
    })
    circ_template.append({
        "id": "c3213107-c92b-40d2-9710-6293cbc111b9",
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Overdue Notice",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>Please renew the following items or return to the locations indicated as soon as possible. Items can be renewed by logging into your library account. Please verify that your items were renewed. Some items may not be renewable.</div><div><br></div><div>Fines will be assessed for overdue library materials. Books that are are considered lost will be charged to your account for each item. </div><div><br></div><div>More information about fines and fees can be found at library home page. If you have any questions, please contact us at the indicated location(s).</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Notification Number</strong>:&nbsp;XXX</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Due Date</strong>: {{loan.dueDate}}</div><div><br></div><div>{{/loans}}</div><div>If you are liable for overdue fines remember that the fine increases the longer you keep the item. You may also be charged if item is not returned.</div><div><br></div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone</strong>: (XXX)XXX-XXXX</div>",
                "attachments": []
            }
        },
        "name": template_names[12],
        "active": "true",
        "category": "Loan"
    })
    circ_template.append({
        "outputFormats": ["text/html"],
        "templateResolver": "mustache",
        "localizedTemplates": {
            "en": {
                "header": "Notice of Fine or Fee",
                "body": "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>The following is a list of current fine(s) or fee(s). More detailed information is available at the library. For payment information, please contact us at the indicated location(s). Information about fines and fees can be found at library home page.</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Due Date</strong>: {{loan.dueDate}}</div><div><strong>Due Date when Fined</strong>: XXX</div><div><strong>Fine/Fee Date</strong>: {{feeCharge.chargeDateTime}}</div><div><strong>Description</strong>: {{feeCharge.type}}</div><div><strong>Fine/Fee Amount</strong>: {{feeCharge.amount}}</div><div><strong>Fine/Fee Balance</strong>: {{feeCharge.remainingAmount}</div><div><strong>Previously Billed: </strong>XXX</div><div><br></div><div>{{/loans}}</div><div><br></div><div><strong>Total of all Fines and Fees</strong>: XXX</div><div><br></div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone</strong>:<strong> </strong>(XXX)XXX-XXXX</div>",
                "attachments": []
            }
        },
        "name": template_names[13],
        "active": "true",
        "category": "AutomatedFeeFine"
    })

    respnotice = requests.get(f"{st.session_state.okapi}/templates?limit=1000", headers=headers)
    data = respnotice.json()
    templates = data['templates']
    st.write(respnotice.content)

    for x in range(0, len(templates)):
        for i in template_names:
            if 'name' in templates[x]:
                if (templates[x]['name'] == i):
                    indexposition = template_names.index(templates[x]['name'])
                    template_names.pop(indexposition)
                    circ_template.pop(indexposition)



    body = circ_template
    for i in body:
        temp_res = requests.post(url_template_post, data=json.dumps(i), headers=headers)



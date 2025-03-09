from flask import url_for
from datetime import date
import requests as rq
import os

BASE_URL = os.environ.get("FINAPI_BASE_URL")
FORM_URL = os.environ.get("FINAPI_BASE_FORM_URL")


def _client_access_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": os.environ.get("FINAPI_CLIENT_ID"),
        "client_secret": os.environ.get("FINAPI_CLIENT_SECRET")
    }
    res = rq.post(BASE_URL+"/api/v2/oauth/token", data=data)
    if res.status_code == 200:
        return "Bearer "+res.json().get("access_token")


def _user_access_token(existingClient):
    data = {
        "grant_type": "password",
        "client_id": os.environ.get("FINAPI_CLIENT_ID"),
        "client_secret": os.environ.get("FINAPI_CLIENT_SECRET"),
        "username": existingClient.bank_username,
        "password": existingClient.bank_password,
    }
    res = rq.post(BASE_URL+"/api/v2/oauth/token", data=data)
    if res.status_code == 200:
        return "Bearer "+res.json().get("access_token")


def create_customer(existingClient):
    email = existingClient.email
    username = existingClient.bank_username
    password = existingClient.bank_password
    phone = existingClient.phone
    data = {
        "id": username,
        "password": password,
        "email": email,
        "phone": phone,
        "isAutoUpdateEnabled": True
    }
    token = _client_access_token()
    headers = {
        "authorization": token
    }
    res = rq.post(BASE_URL+"/api/v2/users", json=data, headers=headers)
    if res.status_code == 201:
        return True
    print(res.json())
    print(res.status_code)
    return False


def get_webform_link(existingClient):
    # Add web form id column in Client Model
    data = {
        "loadOwnerData": True,
        "accountTypes": ["CHECKING", "SAVINGS", "SECURITY", "MEMBERSHIP", "LOAN"],
        "allowedInterfaces": ["XS2A", "FINTS_SERVER"],
        "callbacks": {
            "finalised": url_for("client.bank_form_connected", _external=True, _scheme="https")
        }
    }
    token = _user_access_token(existingClient)
    headers = {
        "authorization": token
    }
    res = rq.post(FORM_URL+"/api/webForms/bankConnectionImport", headers=headers, json=data)
    if res.status_code == 201:
        return res.json()
    print(res.status_code)
    print(res.json())
    return False


def get_transactions(existingClient, existingCampaign):
    token = _user_access_token(existingClient)
    headers = {
        "authorization": token
    }
    apiData = {"transactions": []}
    for lead in existingCampaign.leads:
        params = {
            "view": "userView",
            "minBankBookingDate": existingCampaign.start_date.isoformat(),
            "maxBankBookingDate": existingCampaign.end_date or date.today().isoformat(),
            "direction": "income",
            "counterpart": lead.fullname,
            "perPage": 100,
            "order": "bankBookingDate,desc",
            "includeChildCategories": False,
        }
        res = rq.get(BASE_URL+"/api/v2/transactions", headers=headers, params=params)
        if res.status_code == 200:
            transactions = res.json().get("transactions")
            for transaction in transactions:
                transaction["lead_id"] = lead.id
                apiData["transactions"].append(transaction)
    if apiData["transactions"]:
        return apiData
    return False


def delete_user(existingClient):
    token = _user_access_token(existingClient)
    headers = {
        "authorization": token
    }
    res = rq.delete(BASE_URL+"/api/v2/users", headers=headers)
    print(res.json())
    print(res.status_code)
    return res.status_code == 200

import base64
import json
import logging
from textwrap import indent

import requests
from requests import Session
from requests.auth import HTTPBasicAuth

from app.config import (
    SISA_API_ENDPOINT,
    SISA_API_REQUEST_TIMEOUT_SECONDS,
    SISA_CLIENT_ID,
    SISA_CLIENT_SECRET,
    SISA_ENCRYPTION_KEY,
)
from app.helpers import encrypt


def send_request(url, headers=None):

    session = Session()
    session.auth = HTTPBasicAuth(SISA_CLIENT_ID, SISA_CLIENT_SECRET)

    res = requests.get(
        url, headers=headers, timeout=SISA_API_REQUEST_TIMEOUT_SECONDS, session=session
    )

    # Error handling

    return res


def transform_notifications(source):
    return source


def get_request_url(encrypted_payload, iv):
    payload = base64.urlsafe_b64encode(iv + encrypted_payload).decode("ASCII")

    return SISA_API_ENDPOINT + payload


def get_all(bsn):
    notifications = []
    is_known = False

    (bsn_encrypted, iv) = encrypt(bsn, SISA_ENCRYPTION_KEY)
    url = get_request_url(bsn_encrypted, iv)

    response = send_request(url)
    response_json = response.json()

    payload = response_json

    logging.debug(json.dumps(response_json, indent=4))

    if response_json.get("iemand"):
        is_known = response_json["iemand"]

    if response_json.get("dingen"):
        notifications = transform_notifications(response_json["dingen"])

    payload = {"isKnown": is_known, "notifications": notifications}

    return payload

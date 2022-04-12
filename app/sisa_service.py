import base64
from datetime import datetime

import jwt
import requests
from app.auth import PROFILE_TYPE_COMMERCIAL, PROFILE_TYPE_PRIVATE

from app.config import (
    SISA_API_BSN_ENDPOINT,
    SISA_API_KVK_ENDPOINT,
    SISA_API_REQUEST_TIMEOUT_SECONDS,
    SISA_CERT_FILE,
    SISA_CLIENT_ID,
    SISA_CLIENT_SECRET,
    SISA_ENCRYPTION_KEY,
)
from app.helpers import encrypt


def send_request(url, headers=None):

    token = jwt.encode(
        {"iss": SISA_CLIENT_ID, "iat": datetime.now()},
        SISA_CLIENT_SECRET,
        algorithm="HS256",
    )

    headers = {"Authorization": f"Bearer {token}"}

    res = requests.get(
        url,
        headers=headers,
        timeout=SISA_API_REQUEST_TIMEOUT_SECONDS,
        verify=SISA_CERT_FILE,
    )

    res.raise_for_status()

    # TODO: Implement Error handling?

    return res


def get_request_url(profile_type, encrypted_payload, iv):
    payload = base64.urlsafe_b64encode(iv + encrypted_payload).decode("ASCII")

    if profile_type == PROFILE_TYPE_COMMERCIAL:
        endpoint = SISA_API_KVK_ENDPOINT
    else:
        endpoint = SISA_API_BSN_ENDPOINT

    return endpoint + payload


def get_all(user_id, profile_type=PROFILE_TYPE_PRIVATE):
    (user_id_encrypted, iv) = encrypt(user_id, SISA_ENCRYPTION_KEY)
    url = get_request_url(profile_type, user_id_encrypted, iv)

    response = send_request(url)
    response_json = response.json()

    return response_json["content"]

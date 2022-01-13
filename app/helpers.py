import base64
import os
import secrets
import string
from datetime import date, datetime
from functools import wraps

import yaml
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from flask import g, request
from flask.helpers import make_response
from openapi_core import create_spec
from openapi_core.contrib.flask import FlaskOpenAPIRequest, FlaskOpenAPIResponse
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator
from tma_saml import (
    HR_KVK_NUMBER_KEY,
    SamlVerificationException,
    get_digi_d_bsn,
    get_e_herkenning_attribs,
)
from tma_saml.tma_saml import get_user_type
from tma_saml.user_type import UserType
from yaml import load

from app.config import (
    BASE_PATH,
    ENABLE_OPENAPI_VALIDATION,
    SISA_API_ENDPOINT,
    SISA_ENCRYPTION_KEY,
)

openapi_spec = None


def get_tma_certificate():

    tma_certificate = g.get("tma_certificate", None)

    if not tma_certificate:
        tma_cert_location = os.getenv("TMA_CERTIFICATE")

        if tma_cert_location:
            with open(tma_cert_location, "r") as f:
                tma_certificate = g.tma_certificate = f.read()

    return tma_certificate


def get_bsn_from_request():
    """
    Get the BSN based on a request, expecting a SAML token in the headers
    """
    # Load the TMA certificate
    tma_certificate = get_tma_certificate()

    # Decode the BSN from the request with the TMA certificate
    bsn = get_digi_d_bsn(request, tma_certificate)
    return bsn


def get_kvk_number_from_request():
    """
    Get the KVK number from the request headers.
    """
    # Load the TMA certificate
    tma_certificate = get_tma_certificate()

    # Decode the BSN from the request with the TMA certificate
    attribs = get_e_herkenning_attribs(request, tma_certificate)
    kvk = attribs[HR_KVK_NUMBER_KEY]
    return kvk


def get_tma_user():
    user_type = get_user_type(request, get_tma_certificate())
    user_id = None

    if user_type is UserType.BEDRIJF:
        user_id = get_kvk_number_from_request()
    elif user_type is UserType.BURGER:
        user_id = get_bsn_from_request()
    else:
        raise SamlVerificationException("TMA user type not found")

    if not user_id:
        raise SamlVerificationException("TMA user id not found")

    return {"id": user_id, "type": user_type}


def verify_tma_user(function):
    @wraps(function)
    def verify(*args, **kwargs):
        get_tma_user()
        return function(*args, **kwargs)

    return verify


def get_openapi_spec():
    global openapi_spec
    if not openapi_spec:
        with open(os.path.join(BASE_PATH, "openapi.yml"), "r") as spec_file:
            spec_dict = load(spec_file, Loader=yaml.Loader)

        openapi_spec = create_spec(spec_dict)

    return openapi_spec


def validate_openapi(function):
    @wraps(function)
    def validate(*args, **kwargs):

        if ENABLE_OPENAPI_VALIDATION:
            spec = get_openapi_spec()
            openapi_request = FlaskOpenAPIRequest(request)
            validator = RequestValidator(spec)
            result = validator.validate(openapi_request)
            result.raise_for_errors()

        response = function(*args, **kwargs)

        if ENABLE_OPENAPI_VALIDATION:
            openapi_response = FlaskOpenAPIResponse(response)
            validator = ResponseValidator(spec)
            result = validator.validate(openapi_request, openapi_response)
            result.raise_for_errors()

        return response

    return validate


def success_response_json(response_content):
    return make_response({"status": "OK", "content": response_content}, 200)


def error_response_json(message: str, code: int = 500):
    return make_response({"status": "ERROR", "message": message}, code)


def to_date(date_input):
    if isinstance(date_input, date):
        return date_input

    if isinstance(date_input, datetime):
        return date_input.date()

    if "T" in date_input:
        return datetime.strptime(date_input, "%Y-%m-%dT%H:%M:%S").date()

    return datetime.strptime(date_input, "%Y-%m-%d").date()


def encrypt(plaintext, secret_key):
    # Generate random ascii IV
    iv = bytes(
        "".join(
            secrets.choice(string.ascii_uppercase + string.ascii_lowercase)
            for i in range(AES.block_size)
        ),
        "utf-8",
    )

    encryption_key = bytes(secret_key, "utf-8")
    cipher = AES.new(key=encryption_key, mode=AES.MODE_CBC, IV=iv)
    padded_plaintext = pad(plaintext.encode("utf-8"), AES.block_size)

    return (cipher.encrypt(padded_plaintext), iv)


def decrypt(encrypted, iv, secret_key):
    encryption_key = bytes(secret_key, "utf-8")

    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted), AES.block_size).decode("utf-8")

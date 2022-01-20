import logging
import os
import os.path
from datetime import date, time

from flask.json import JSONEncoder
from tma_saml.exceptions import (
    InvalidBSNException,
    SamlExpiredException,
    SamlVerificationException,
)

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# Sentry configuration.
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENV = os.getenv("SENTRY_ENVIRONMENT")

# Environment determination
IS_PRODUCTION = SENTRY_ENV == "production"
IS_ACCEPTANCE = SENTRY_ENV == "acceptance"
IS_AP = IS_PRODUCTION or IS_ACCEPTANCE
IS_DEV = os.getenv("FLASK_ENV") == "development" and not IS_AP

# App constants
TMAException = (SamlVerificationException, InvalidBSNException, SamlExpiredException)
ENABLE_OPENAPI_VALIDATION = os.getenv("ENABLE_OPENAPI_VALIDATION", "1")

# SISA specific config
SISA_API_REQUEST_TIMEOUT_SECONDS = 30
SISA_API_ENDPOINT = os.getenv("SISA_API_ENDPOINT")
SISA_ENCRYPTION_KEY = os.getenv("SISA_ENCRYPTION_KEY")
SISA_CLIENT_SECRET = os.getenv("SISA_CLIENT_SECRET")
SISA_CLIENT_ID = os.getenv("SISA_CLIENT_ID")
SISA_CERT_FILE = BASE_PATH + "/../cert/Private_G1_chain_acc_temp.pem"

# Set-up logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR").upper()
logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s:%(lineno)d in function %(funcName)s] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=LOG_LEVEL,
)


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.isoformat(timespec="minutes")
        if isinstance(obj, date):
            return obj.isoformat()

        return JSONEncoder.default(self, obj)

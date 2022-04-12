import os
import unittest
from flask_httpauth import HTTPTokenAuth
import jwt

auth = HTTPTokenAuth(scheme="Bearer")

AuthException = jwt.PyJWTError

PROFILE_TYPE_PRIVATE = "private"
PROFILE_TYPE_COMMERCIAL = "commercial"

OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET", "")
OIDC_CLIENT_ID_DIGID = os.getenv("OIDC_CLIENT_ID_DIGID", "digid")
OIDC_CLIENT_ID_EHERKENNING = os.getenv("OIDC_CLIENT_ID_EHERKENNING", "eherkenning")

TOKEN_ID_ATTRIBUTE_COMMERCIAL = "urn:etoegang:1.9:EntityConcernedID:KvKnr"
TOKEN_ID_ATTRIBUTE_PRIVATE = "sub"

ProfileTypeByClientId = {
    OIDC_CLIENT_ID_DIGID: PROFILE_TYPE_PRIVATE,
    OIDC_CLIENT_ID_EHERKENNING: PROFILE_TYPE_COMMERCIAL,
}

ClientIdByProfileType = {
    PROFILE_TYPE_PRIVATE: OIDC_CLIENT_ID_DIGID,
    PROFILE_TYPE_COMMERCIAL: OIDC_CLIENT_ID_EHERKENNING,
}

TokenAttributeByProfileType = {
    PROFILE_TYPE_PRIVATE: TOKEN_ID_ATTRIBUTE_PRIVATE,
    PROFILE_TYPE_COMMERCIAL: TOKEN_ID_ATTRIBUTE_COMMERCIAL,
}

login_required = auth.login_required


def get_profile_type(token_data):
    return ProfileTypeByClientId[token_data["aud"]]


def get_client_id(profile_type):
    return ClientIdByProfileType[profile_type]


def get_id_token_attribute_by_profile_type(profile_type):
    return TokenAttributeByProfileType[profile_type]


def get_profile_id(token_data):
    profile_type = get_profile_type(token_data)
    id_attribute = get_id_token_attribute_by_profile_type(profile_type)
    return token_data[id_attribute]


def get_user_profile_from_token(token):
    audience = [
        get_client_id(PROFILE_TYPE_PRIVATE),
        get_client_id(PROFILE_TYPE_COMMERCIAL),
    ]
    token_data = jwt.decode(
        token,
        OIDC_CLIENT_SECRET,
        audience=audience,
        algorithms="HS256",
        options={"verify_signature": True, "verify_exp": True, "verify_iat": True},
    )

    profile_type = get_profile_type(token_data)
    profile_id = get_profile_id(token_data)

    return {"id": profile_id, "type": profile_type}


@auth.verify_token
def verify_token(token):
    return get_user_profile_from_token(token)


def get_current_user():
    return auth.current_user()


class FlaskServerTestCase(unittest.TestCase):
    TEST_BSN = "111222333"
    TEST_KVK = "333222111"

    app = None
    client = None

    def get_test_app_client(self, app):
        app.testing = True
        return app.test_client()

    def setUp(self):
        self.client = self.get_test_app_client(self.app)
        self.maxDiff = None

    def get_user_id(self, profile_type):
        if profile_type == PROFILE_TYPE_COMMERCIAL:
            return self.TEST_KVK

        return self.TEST_BSN

    def get_token_header_value(self, profile_type):
        id_attribute = get_id_token_attribute_by_profile_type(profile_type)
        token_data = {
            id_attribute: self.get_user_id(profile_type),
            "aud": get_client_id(profile_type),
        }

        token = jwt.encode(
            token_data,
            OIDC_CLIENT_SECRET,
            algorithm="HS256",
        )

        return f"Bearer {token}"

    def add_authorization_headers(self, profile_type, headers=None):
        if headers is None:
            headers = {}

        headers["Authorization"] = self.get_token_header_value(profile_type)

        return headers

    def get_secure(self, location, profile_type=PROFILE_TYPE_PRIVATE, headers=None):
        return self.client.get(
            location,
            headers=self.add_authorization_headers(profile_type, headers=headers),
        )

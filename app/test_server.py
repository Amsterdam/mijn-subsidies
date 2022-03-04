from unittest import mock
from unittest.mock import patch

from app.server import app
from tma_saml import FlaskServerTMATestCase, UserType
from tma_saml.for_tests.cert_and_key import server_crt


@patch("app.helpers.get_tma_certificate", lambda: server_crt)
class ApiTests(FlaskServerTMATestCase):
    TEST_BSN = "111222333"
    TEST_KVK = "333222111"

    def setUp(self):
        self.client = self.get_tma_test_app(app)
        self.maxDiff = None

    def get_secure(self, location, user_type=UserType.BURGER):
        return self.client.get(location, headers=self.saml_headers(user_type))

    def saml_headers(self, user_type=UserType.BURGER):
        if user_type is UserType.BEDRIJF:
            return self.add_e_herkenning_headers(self.TEST_KVK)

        return self.add_digi_d_headers(self.TEST_BSN)

    def mock_response(*args, **kwargs):
        return {"body": {"FOo": "Barrr"}}

    def test_status(self):
        response = self.client.get("/status/health")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "OK")
        self.assertEqual(data["content"], "OK")

    @mock.patch(
        "app.sisa_service.get_all",
    )
    def test_get_all_none(self, get_all_mock):

        get_all_mock.return_value = None

        response = self.get_secure("/subsidies/summary", UserType.BURGER)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        expected_content = None

        self.assertEqual(data["status"], "OK")
        self.assertEqual(data["content"], expected_content)

        get_all_mock.assert_called_with(self.TEST_BSN, UserType.BURGER)

    @mock.patch(
        "app.sisa_service.get_all",
    )
    def test_get_all_some_bsn(self, get_all_mock):

        get_all_mock.return_value = {"foo": [], "bar": True}

        response = self.get_secure("/subsidies/summary", UserType.BURGER)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        expected_content = {"bar": True, "foo": []}

        self.assertEqual(data["status"], "OK")
        self.assertEqual(data["content"], expected_content)

        get_all_mock.assert_called_with(self.TEST_BSN, UserType.BURGER)

    @mock.patch(
        "app.sisa_service.get_all",
    )
    def test_get_all_some_kvk(self, get_all_mock):

        get_all_mock.return_value = {"foo": [], "bar": True}

        response = self.get_secure("/subsidies/summary", UserType.BEDRIJF)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        expected_content = {"bar": True, "foo": []}

        self.assertEqual(data["status"], "OK")
        self.assertEqual(data["content"], expected_content)

        get_all_mock.assert_called_with(self.TEST_KVK, UserType.BEDRIJF)

    def test_error_handler(self):
        response = self.get_secure("/subsidies/hack")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json, {"message": "Server error occurred", "status": "ERROR"}
        )

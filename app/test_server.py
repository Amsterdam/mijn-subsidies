from unittest import mock
from unittest.mock import patch

from app.server import app
from tma_saml import FlaskServerTMATestCase
from tma_saml.for_tests.cert_and_key import server_crt


@patch("app.helpers.get_tma_certificate", lambda: server_crt)
class ApiTests(FlaskServerTMATestCase):
    TEST_BSN = "111222333"

    def setUp(self):
        self.client = self.get_tma_test_app(app)
        self.maxDiff = None

    def get_secure(self, location):
        return self.client.get(location, headers=self.saml_headers())

    def saml_headers(self):
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
        "app.xxx_service.get_all",
    )
    def test_get_all(self, get_all_mock):

        get_all_mock.return_value = None

        response = self.get_secure("/subsidies/all")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        expected_content = None

        self.assertEqual(data["status"], "OK")
        self.assertEqual(data["content"], expected_content)

        get_all_mock.assert_called_with(self.TEST_BSN)

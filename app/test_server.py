from unittest import mock

from app.auth import PROFILE_TYPE_COMMERCIAL, PROFILE_TYPE_PRIVATE, FlaskServerTestCase
from app.server import app


class ApiTests(FlaskServerTestCase):

    app = app

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

        response = self.get_secure("/subsidies/summary", PROFILE_TYPE_PRIVATE)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        expected_content = None

        self.assertEqual(data["status"], "OK")
        self.assertEqual(data["content"], expected_content)

        get_all_mock.assert_called_with(self.TEST_BSN, PROFILE_TYPE_PRIVATE)

    @mock.patch(
        "app.sisa_service.get_all",
    )
    def test_get_all_some_bsn(self, get_all_mock):

        get_all_mock.return_value = {"foo": [], "bar": True}

        response = self.get_secure("/subsidies/summary", PROFILE_TYPE_PRIVATE)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        expected_content = {"bar": True, "foo": []}

        self.assertEqual(data["status"], "OK")
        self.assertEqual(data["content"], expected_content)

        get_all_mock.assert_called_with(self.TEST_BSN, PROFILE_TYPE_PRIVATE)

    @mock.patch(
        "app.sisa_service.get_all",
    )
    def test_get_all_some_kvk(self, get_all_mock):

        get_all_mock.return_value = {"foo": [], "bar": True}

        response = self.get_secure("/subsidies/summary", PROFILE_TYPE_COMMERCIAL)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        expected_content = {"bar": True, "foo": []}

        self.assertEqual(data["status"], "OK")
        self.assertEqual(data["content"], expected_content)

        get_all_mock.assert_called_with(self.TEST_KVK, PROFILE_TYPE_COMMERCIAL)

    def test_error_handler(self):
        response = self.get_secure("/subsidies/hack")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json, {"message": "Server error occurred", "status": "ERROR"}
        )

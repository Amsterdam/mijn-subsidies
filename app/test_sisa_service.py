import json

from unittest import TestCase
from unittest.mock import patch
from app.sisa_service import get_all
from app.server import app


class SISAApiMock:
    status_code = 200
    response_json = None

    def __init__(self, response_json):
        if isinstance(response_json, str):
            with open(response_json, "r") as read_file:
                self.response_json = json.load(read_file)
        else:
            self.response_json = response_json

    def json(self):
        return self.response_json

    def raise_for_status(*args, **kwargs):
        return


class ServiceTests(TestCase):
    TEST_BSN = "111222333"

    def setUp(self):
        self.maxDiff = None

    @patch("app.sisa_service.SISA_ENCRYPTION_KEY", "abcdefghijklmnop")
    @patch("app.sisa_service.SISA_API_ENDPOINT", "http://nothing")
    @patch("app.sisa_service.SISA_CLIENT_ID", "_some_id_")
    @patch("app.sisa_service.SISA_CLIENT_SECRET", "_some_secret_")
    @patch("app.sisa_service.requests.get")
    def test_get_all(self, get_mock):

        get_mock.return_value = SISAApiMock({"notifications": [], "isKnown": True})

        with app.app_context():
            result_all = get_all(self.TEST_BSN)

        get_mock.assert_called_once()

        self.assertEqual(result_all, {"notifications": [], "isKnown": True})

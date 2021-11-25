import logging

import sentry_sdk
from flask import Flask
from requests.exceptions import HTTPError
from sentry_sdk.integrations.flask import FlaskIntegration

from app import xxx_service
from app.config import (
    IS_DEV,
    SENTRY_DSN,
    CustomJSONEncoder,
    TMAException,
)
from app.helpers import (
    error_response_json,
    get_tma_user,
    success_response_json,
    verify_tma_user,
)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

if SENTRY_DSN:  # pragma: no cover
    sentry_sdk.init(
        dsn=SENTRY_DSN, integrations=[FlaskIntegration()], with_locals=False
    )


@app.route("/subsidies/summary", methods=["GET"])
@verify_tma_user
def get_all():
    user = get_tma_user()
    content = xxx_service.get_all(user["id"])

    return success_response_json(content)


@app.route("/status/health")
def health_check():
    return success_response_json("OK")


@app.errorhandler(Exception)
def handle_error(error):

    error_message_original = str(error)

    msg_tma_exception = "TMA error occurred"
    msg_request_http_error = "Request error occurred"
    msg_server_error = "Server error occurred"

    if not app.config["TESTING"]:  # pragma: no cover
        logging.exception(
            error, extra={"error_message_original": error_message_original}
        )

    if IS_DEV:  # pragma: no cover
        msg_tma_exception = error_message_original
        msg_request_http_error = error_message_original
        msg_server_error = error_message_original

    if isinstance(error, HTTPError):
        return error_response_json(
            msg_request_http_error,
            error.response.status_code,
        )
    elif isinstance(error, TMAException):
        return error_response_json(msg_tma_exception, 400)

    return error_response_json(msg_server_error, 500)


if __name__ == "__main__":  # pragma: no cover
    app.run()

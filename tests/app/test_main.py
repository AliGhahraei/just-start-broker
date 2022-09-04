from just_start_broker.app import app, register_handler

from starlette.status import HTTP_418_IM_A_TEAPOT
from starlette.testclient import TestClient


class TestApp:
    @staticmethod
    def test_error_response_contains_error_string(client: TestClient) -> None:
        class TempException(Exception):
            pass

        @app.get("/error/")
        def error_route() -> None:
            raise TempException("test_string")

        register_handler(TempException, HTTP_418_IM_A_TEAPOT)

        assert client.get("/error/").json() == {"error": "test_string"}

from _pytest.fixtures import fixture

from just_start_broker.app import app
from starlette.testclient import TestClient


@fixture
def client() -> TestClient:
    return TestClient(app)

from datetime import date, time
from typing import Any
from unittest.mock import Mock

from just_start_broker.app import app, ScheduleStorer
from just_start_broker.file_persistence import get_schedule_storer

from just_start_broker.schemas import Event, Schedule
from pytest import fixture, mark
from starlette.testclient import TestClient


@fixture
def client() -> TestClient:
    return TestClient(app)


class TestSchedule:
    @staticmethod
    @fixture(autouse=True)
    def storer() -> Mock:
        mock = Mock(spec_set=ScheduleStorer)
        app.dependency_overrides[get_schedule_storer] = lambda: mock
        return mock

    @staticmethod
    @mark.parametrize(
        "payload",
        [
            {},
            {"date": "2022-08-01", "events": []},
            {"date": "2022-08-01", "events": [{}]},
        ],
    )
    def test_create_schedule_responds_with_unprocessable_entity_given_invalid_payload(
        client: TestClient, payload: dict[str, Any]
    ) -> None:
        response = client.post("/schedule", json=payload)

        assert response.status_code == 422

    class TestValidPayload:
        @staticmethod
        @fixture
        def payload() -> dict[str, Any]:
            return {
                "date": "2022-08-01",
                "events": [
                    {"type": "test_type", "start": "03:00:00", "end": "04:00:00"}
                ],
            }

        @staticmethod
        def test_create_schedule_stores_schedule(
            client: TestClient,
            storer: Mock,
            payload: dict[str, Any],
        ) -> None:
            client.post("/schedule", json=payload)

            storer.store.assert_called_once_with(
                Schedule(
                    date(2022, 8, 1),
                    [Event("test_type", time(3), time(4))],
                ),
            )

        @staticmethod
        def test_create_schedule_responds_correctly(
            client: TestClient,
            storer: Mock,
            payload: dict[str, Any],
        ) -> None:
            response = client.post("/schedule", json=payload)

            assert response.status_code == 200
            assert response.json() == payload

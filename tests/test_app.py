from datetime import datetime
from typing import Any
from unittest.mock import Mock

from just_start_broker.app import app, ScheduleAccessor
from just_start_broker.file_persistence import get_schedule_accessor

from just_start_broker.schemas import Event, Schedule
from pytest import fixture, mark
from starlette.testclient import TestClient


@fixture
def client() -> TestClient:
    return TestClient(app)


class TestSchedule:
    @staticmethod
    @fixture(autouse=True)
    def accessor() -> Mock:
        mock = Mock(spec_set=ScheduleAccessor)
        app.dependency_overrides[get_schedule_accessor] = lambda: mock
        return mock

    @staticmethod
    @mark.parametrize(
        "payload",
        [
            {},
            {"expiration": "2022-08-14T08:00", "events": []},
            {"expiration": "2022-08-14T08:00", "events": [{}]},
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
                "expiration": "2022-08-15T00:00:00",
                "events": [
                    {
                        "type": "test_type",
                        "start": "2022-08-14T03:00:00",
                        "end": "2022-08-14T04:00:00",
                    }
                ],
            }

        @staticmethod
        def test_create_schedule_creates_schedule(
            client: TestClient,
            accessor: Mock,
            payload: dict[str, Any],
        ) -> None:
            client.post("/schedule", json=payload)

            accessor.create.assert_called_once_with(
                Schedule(
                    datetime(2022, 8, 15),
                    [
                        Event(
                            "test_type",
                            datetime(2022, 8, 14, 3),
                            datetime(2022, 8, 14, 4),
                        )
                    ],
                ),
            )

        @staticmethod
        def test_create_schedule_responds_correctly(
            client: TestClient,
            payload: dict[str, Any],
        ) -> None:
            response = client.post("/schedule", json=payload)

            assert response.status_code == 200
            assert response.json() == payload

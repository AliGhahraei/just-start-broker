from datetime import datetime
from typing import Any
from unittest.mock import Mock

from just_start_broker.app import app, ScheduleAccessor
from just_start_broker.file_persistence import get_schedule_accessor
from just_start_broker.persistence import ScheduleNotExpired, ScheduleNotFoundError

from just_start_broker.schemas import Schedule
from pytest import fixture, FixtureRequest, mark
from starlette.testclient import TestClient


@fixture
def client() -> TestClient:
    return TestClient(app)


class TestSchedule:
    @staticmethod
    @fixture(autouse=True)
    def accessor(request: FixtureRequest) -> Mock:
        mock = Mock(spec_set=ScheduleAccessor)
        side_effects = {
            "ScheduleNotExpired": ScheduleNotExpired(datetime(2022, 8, 15)),
            "ScheduleNotFoundError": ScheduleNotFoundError,
        }
        if (param := getattr(request, "param", None)) is not None:
            mock.create.side_effect = side_effects[param]
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
    def test_create_raises_unprocessable_entity_given_invalid_payload(
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
                        "type": "Work",
                        "start": "2022-08-14T03:00:00",
                        "end": "2022-08-14T04:00:00",
                    }
                ],
            }

        @staticmethod
        @mark.parametrize(
            "accessor", ["ScheduleNotExpired", "ScheduleNotFoundError"], indirect=True
        )
        def test_create_raises_unprocessable_entity_if_schedule_has_not_expired(
            client: TestClient, accessor: Mock, payload: dict[str, Any]
        ) -> None:
            response = client.post("/schedule", json=payload)

            assert response.status_code == 422

        @staticmethod
        @mark.parametrize(
            "accessor,expected_error",
            [
                ["ScheduleNotFoundError", "Schedule did not exist"],
                [
                    "ScheduleNotExpired",
                    "Cannot set a new schedule until 2022-08-15 00:00:00",
                ],
            ],
            indirect=["accessor"],
        )
        def test_create_shows_expected_message_if_schedule_raises_client_error(
            client: TestClient,
            accessor: Mock,
            expected_error: str,
            payload: dict[str, Any],
        ) -> None:
            response = client.post("/schedule", json=payload)

            assert response.json() == {
                "error": expected_error,
            }

        @staticmethod
        def test_create_schedule_creates_schedule(
            client: TestClient,
            accessor: Mock,
            payload: dict[str, Any],
            schedule: Schedule,
        ) -> None:
            client.post("/schedule", json=payload)

            accessor.create.assert_called_once_with(schedule)

        @staticmethod
        def test_create_schedule_responds_correctly(
            client: TestClient,
            payload: dict[str, Any],
        ) -> None:
            response = client.post("/schedule", json=payload)

            assert response.status_code == 200
            assert response.json() == payload

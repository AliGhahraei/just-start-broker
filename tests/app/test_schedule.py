from datetime import datetime
from typing import Any
from unittest.mock import Mock

from just_start_broker.app import app, ScheduleAccessor
from just_start_broker.file_persistence import get_schedule_accessor
from just_start_broker.persistence import ScheduleNotExpired, ScheduleNotFoundError
from just_start_broker.schemas import Event, Schedule

from pytest import fixture, mark
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY
from starlette.testclient import TestClient


class TestSchedule:
    @staticmethod
    @fixture(autouse=True)
    def accessor() -> Mock:
        mock = Mock(spec_set=ScheduleAccessor)
        app.dependency_overrides[get_schedule_accessor] = lambda: mock
        return mock

    @staticmethod
    @fixture
    def schedule_dict() -> dict[str, Any]:
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

    class TestCreate:
        class TestExceptions:
            @staticmethod
            @fixture(autouse=True)
            def accessor(accessor: Mock) -> Mock:
                accessor.create.side_effect = ScheduleNotFoundError
                return accessor

            @staticmethod
            def test_create_returns_expected_status_for_exception(
                client: TestClient,
                schedule_dict: dict[str, Any],
            ) -> None:
                response = client.post("/schedule/", json=schedule_dict)

                assert response.status_code == HTTP_404_NOT_FOUND

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
            response = client.post("/schedule/", json=payload)

            assert response.status_code == 422

        @staticmethod
        def test_create_schedule_creates_schedule(
            client: TestClient,
            accessor: Mock,
            schedule_dict: dict[str, Any],
            schedule: Schedule,
        ) -> None:
            client.post("/schedule/", json=schedule_dict)

            accessor.create.assert_called_once_with(schedule)

        @staticmethod
        def test_create_schedule_returns_ok(
            client: TestClient,
            schedule_dict: dict[str, Any],
        ) -> None:
            assert client.post("/schedule/", json=schedule_dict).status_code == 200

        @staticmethod
        def test_create_schedule_responds_with_schedule(
            client: TestClient,
            schedule_dict: dict[str, Any],
        ) -> None:
            assert client.post("/schedule/", json=schedule_dict).json() == schedule_dict

    class TestRead:
        class TestExceptions:
            @staticmethod
            @fixture(autouse=True)
            def accessor(accessor: Mock) -> Mock:
                accessor.read.side_effect = ScheduleNotExpired(datetime(2022, 8, 15))
                return accessor

            @staticmethod
            def test_read_returns_expected_status_for_exception(
                client: TestClient,
            ) -> None:
                response = client.get("/schedule/")

                assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

        class TestWithExistingSchedule:
            @staticmethod
            @fixture(autouse=True)
            def accessor(accessor: Mock) -> Mock:
                accessor.read.return_value = Schedule(
                    [Event("Work", datetime(2022, 8, 14, 3), datetime(2022, 8, 14, 4))],
                    datetime(2022, 8, 15),
                )
                return accessor

            @staticmethod
            def test_read_schedule_responds_with_schedule(
                client: TestClient,
                schedule_dict: dict[str, Any],
            ) -> None:
                assert client.get("/schedule/").json() == schedule_dict

            @staticmethod
            def test_read_schedule_returns_ok(
                client: TestClient,
            ) -> None:
                assert client.get("/schedule/").status_code == 200

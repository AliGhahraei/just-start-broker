from datetime import datetime
from json import dumps, load
from pathlib import Path
from typing import Any
from unittest.mock import Mock

from just_start_broker.file_persistence import (
    FileScheduleAccessor,
    get_schedule_accessor,
    ScheduleEncoder,
)
from just_start_broker.persistence import ScheduleNotExpired, ScheduleNotFoundError
from just_start_broker.schemas import Event, Schedule

from pytest import fixture, mark, raises


def assert_content_equals(filepath: Path, serialized_schedule: dict[str, Any]) -> None:
    with open(filepath) as f:
        contents = load(f)
    assert contents == serialized_schedule


class TestGetScheduleAccessor:
    @staticmethod
    def test_call_returns_accessor_with_default_path() -> None:
        config_path = Path("config")
        accessor = get_schedule_accessor(config_path=config_path)
        expected_path = config_path / "just-start-broker" / "schedule.json"
        assert accessor.path == expected_path  # type: ignore[attr-defined]


class TestScheduleEncoder:
    @staticmethod
    def test_default_raises_type_error_for_unknown_type() -> None:
        class UnknownType:
            pass

        with raises(TypeError):
            dumps(UnknownType(), cls=ScheduleEncoder)


class TestFileScheduleAccessor:
    @staticmethod
    @fixture
    def filepath(tmp_path: Path) -> Path:
        return tmp_path / "file"

    @staticmethod
    @fixture
    def serialized_schedule() -> dict[str, Any]:
        return {
            "expiration": "2022-08-15 00:00:00",
            "events": [
                {
                    "start": "2022-08-14 03:00:00",
                    "end": "2022-08-14 04:00:00",
                    "type": "Work",
                }
            ],
        }

    @staticmethod
    @mark.parametrize(
        "subpath", [Path("file"), Path("dir") / "file", Path("dir") / "subdir" / "file"]
    )
    def test_create_writes_file(
        schedule: Schedule,
        serialized_schedule: dict[str, Any],
        tmp_path: Path,
        subpath: Path,
    ) -> None:
        filepath = tmp_path / subpath

        FileScheduleAccessor(filepath, Mock()).create(schedule)

        assert_content_equals(filepath, serialized_schedule)

    class TestMultipleCreateCalls:
        @staticmethod
        @fixture
        def second_schedule() -> Schedule:
            return Schedule(
                expiration=datetime(2022, 8, 16),
                events=[
                    Event("Gym", datetime(2022, 8, 15, 1), datetime(2022, 8, 15, 2))
                ],
            )

        @staticmethod
        @fixture
        def second_serialized_schedule() -> dict[str, Any]:
            return {
                "expiration": "2022-08-16 00:00:00",
                "events": [
                    {
                        "start": "2022-08-15 01:00:00",
                        "end": "2022-08-15 02:00:00",
                        "type": "Gym",
                    }
                ],
            }

        @staticmethod
        def test_create_rejects_schedule_if_past_expiration_is_in_future(
            schedule: Schedule,
            second_schedule: Schedule,
            filepath: Path,
        ) -> None:
            get_now = Mock(return_value=datetime(2022, 8, 14, 23))
            accessor = FileScheduleAccessor(filepath, get_now)

            accessor.create(schedule)
            with raises(ScheduleNotExpired):
                accessor.create(second_schedule)

        @staticmethod
        def test_create_writes_file_if_past_expiration_is_not_in_future(
            schedule: Schedule,
            second_schedule: Schedule,
            second_serialized_schedule: dict[str, Any],
            filepath: Path,
        ) -> None:
            get_now = Mock(return_value=datetime(2022, 8, 15))
            accessor = FileScheduleAccessor(filepath, get_now)

            accessor.create(schedule)
            accessor.create(second_schedule)

            assert_content_equals(filepath, second_serialized_schedule)

    @staticmethod
    def test_read_raises_schedule_not_found_error_if_schedule_has_not_been_added(
        filepath: Path,
    ) -> None:
        with raises(ScheduleNotFoundError):
            FileScheduleAccessor(filepath, Mock()).read()

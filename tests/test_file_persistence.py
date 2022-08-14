from datetime import datetime
from json import dumps, load
from pathlib import Path

from just_start_broker.file_persistence import (
    FileScheduleAccessor,
    get_schedule_accessor,
    ScheduleEncoder,
)
from just_start_broker.schemas import Event, Schedule

from pytest import fixture, mark, raises


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
    def schedule() -> Schedule:
        return Schedule(
            datetime(2022, 8, 15),
            [Event("Work", datetime(2022, 8, 14, 4), datetime(2022, 8, 14, 5))],
        )

    @staticmethod
    @mark.parametrize(
        "subpath", [Path("file"), Path("dir") / "file", Path("dir") / "subdir" / "file"]
    )
    def test_create_writes_file(
        schedule: Schedule, tmp_path: Path, subpath: Path
    ) -> None:
        filepath = tmp_path / subpath

        FileScheduleAccessor(filepath).create(schedule)

        with open(filepath) as f:
            contents = load(f)

        assert contents == {
            "expiration": "2022-08-15 00:00:00",
            "events": [
                {
                    "start": "2022-08-14 04:00:00",
                    "end": "2022-08-14 05:00:00",
                    "type": "Work",
                }
            ],
        }

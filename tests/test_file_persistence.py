from datetime import date, time
from json import dumps, load
from pathlib import Path

from just_start_broker.file_persistence import (
    FileScheduleStorer,
    get_schedule_storer,
    ScheduleEncoder,
)
from just_start_broker.schemas import Event, Schedule

from pytest import mark, raises


class TestGetScheduleStorer:
    @staticmethod
    def test_call_returns_storer_with_default_path() -> None:
        config_path = Path("config")
        storer = get_schedule_storer(config_path=config_path)
        expected_path = config_path / "just-start-broker" / "schedule.json"
        assert storer.path == expected_path  # type: ignore[attr-defined]


class TestScheduleEncoder:
    @staticmethod
    def test_default_raises_type_error_for_unknown_type() -> None:
        class UnknownType:
            pass

        with raises(TypeError):
            dumps(UnknownType(), cls=ScheduleEncoder)


class TestFileScheduleStorer:
    @staticmethod
    @mark.parametrize(
        "subpath", [Path("file"), Path("dir") / "file", Path("dir") / "subdir" / "file"]
    )
    def test_store_stores_file(tmp_path: Path, subpath: Path) -> None:
        filepath = tmp_path / subpath

        FileScheduleStorer(filepath).store(
            Schedule(date(2022, 8, 13), [Event("Work", time(4), time(5))])
        )

        with open(filepath) as f:
            contents = load(f)

        assert contents == {
            "date": "2022-08-13",
            "events": [{"start": "04:00:00", "end": "05:00:00", "type": "Work"}],
        }

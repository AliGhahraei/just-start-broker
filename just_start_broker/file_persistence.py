from dataclasses import asdict
from datetime import datetime
from json import dump, JSONEncoder
from pathlib import Path
from typing import Any, Callable, TYPE_CHECKING

from pydantic import parse_file_as
from xdg import xdg_config_home

from just_start_broker.persistence import ScheduleNotExpired
from just_start_broker.schemas import Schedule

if TYPE_CHECKING:
    from just_start_broker.app import ScheduleAccessor


def get_schedule_accessor(
    *, config_path: Path = xdg_config_home()
) -> "ScheduleAccessor":
    return FileScheduleAccessor(config_path / "just-start-broker" / "schedule.json")


class ScheduleEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return str(o)
        return super().default(o)


class FileScheduleAccessor:
    def __init__(self, path: Path, get_now: Callable[[], datetime] = datetime.utcnow):
        self.path = path
        self.get_now = get_now

    def create(self, schedule: Schedule) -> None:
        if self.path.exists() and self.read().expiration > self.get_now():
            raise ScheduleNotExpired

        self.path.parent.mkdir(exist_ok=True, parents=True)
        with open(self.path, "w") as f:
            dump(asdict(schedule), f, cls=ScheduleEncoder)

    def read(self) -> Schedule:
        return parse_file_as(Schedule, self.path)

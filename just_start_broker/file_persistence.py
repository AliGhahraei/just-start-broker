from dataclasses import asdict
from datetime import date, time
from json import dump, JSONEncoder
from pathlib import Path
from typing import Any, TYPE_CHECKING

from xdg import xdg_config_home

from just_start_broker.schemas import Schedule

if TYPE_CHECKING:
    from just_start_broker.app import ScheduleStorer


def get_schedule_storer(*, config_path: Path = xdg_config_home()) -> "ScheduleStorer":
    return FileScheduleStorer(config_path / "just-start-broker" / "schedule.json")


class ScheduleEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, (date, time)):
            return str(o)
        return super().default(o)


class FileScheduleStorer:
    def __init__(self, path: Path):
        self.path = path

    def store(self, schedule: Schedule) -> None:
        self.path.parent.mkdir(exist_ok=True, parents=True)
        with open(self.path, "w") as f:
            dump(asdict(schedule), f, cls=ScheduleEncoder)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from just_start_broker.app import ScheduleStorer


def get_schedule_storer() -> "ScheduleStorer":
    pass

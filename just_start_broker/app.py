from typing import Protocol

from fastapi import Depends, FastAPI

from just_start_broker.file_persistence import get_schedule_accessor
from just_start_broker.schemas import Schedule

app = FastAPI()


class ScheduleAccessor(Protocol):
    def create(self, schedule: Schedule) -> None:
        pass


@app.post("/schedule", response_model=Schedule)
def create_schedule(
    schedule: Schedule,
    accessor: ScheduleAccessor = Depends(get_schedule_accessor),
) -> Schedule:
    accessor.create(schedule)
    return schedule

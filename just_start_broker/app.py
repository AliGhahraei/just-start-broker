from typing import Protocol

from fastapi import Depends, FastAPI

from just_start_broker.file_persistence import get_schedule_storer
from just_start_broker.schemas import Schedule

app = FastAPI()


class ScheduleStorer(Protocol):
    def store(self, schedule: Schedule) -> None:
        pass


@app.post("/schedule", response_model=Schedule)
def create_schedule(
    schedule: Schedule,
    storer: ScheduleStorer = Depends(get_schedule_storer),
) -> Schedule:
    storer.store(schedule)
    return schedule
